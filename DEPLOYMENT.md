# MDrive - Production Deployment Guide

Guide for deploying MDrive to a production environment.

## Pre-Deployment Checklist

### Security
- [ ] Change all default passwords
- [ ] Generate strong JWT secret keys
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up firewall rules
- [ ] Enable CORS only for your domain
- [ ] Review file upload restrictions
- [ ] Disable debug mode in Flask
- [ ] Set secure session cookies
- [ ] Implement rate limiting
- [ ] Configure backup strategy

### Performance
- [ ] Enable database connection pooling
- [ ] Set up CDN for static assets
- [ ] Configure caching (Redis recommended)
- [ ] Optimize database indexes
- [ ] Enable Gzip compression
- [ ] Set up monitoring and logging

### Infrastructure
- [ ] Provision server (minimum 2GB RAM, 20GB storage)
- [ ] Set up MySQL database
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL/TLS certificates
- [ ] Configure domain DNS

---

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### 2. Clone Project

```bash
cd /opt
sudo git clone <your-repo-url> mdrive
cd mdrive
```

#### 3. Configure Environment

```bash
# Update docker-compose.yml with production settings
sudo nano docker-compose.yml
```

Update these values:
```yaml
environment:
  JWT_SECRET_KEY: <generate-strong-key>
  SECRET_KEY: <generate-another-strong-key>
  FLASK_ENV: production
  MYSQL_ROOT_PASSWORD: <strong-password>
  MYSQL_PASSWORD: <strong-password>
```

#### 4. Set Up SSL with Let's Encrypt

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  nginx-proxy:
    image: nginxproxy/nginx-proxy
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/tmp/docker.sock:ro
      - certs:/etc/nginx/certs:ro
      - vhost:/etc/nginx/vhost.d
      - html:/usr/share/nginx/html
    networks:
      - mdrive-network

  letsencrypt:
    image: nginxproxy/acme-companion
    container_name: letsencrypt
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - certs:/etc/nginx/certs
      - vhost:/etc/nginx/vhost.d
      - html:/usr/share/nginx/html
      - acme:/etc/acme.sh
    environment:
      - DEFAULT_EMAIL=your@email.com
    depends_on:
      - nginx-proxy
    networks:
      - mdrive-network

  frontend:
    environment:
      - VIRTUAL_HOST=yourdomain.com
      - LETSENCRYPT_HOST=yourdomain.com
      - LETSENCRYPT_EMAIL=your@email.com

volumes:
  certs:
  vhost:
  html:
  acme:
```

#### 5. Start Services

```bash
# Start with production configuration
sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Initialize database
sudo docker exec -it mdrive-backend python init_db.py

# Check logs
sudo docker-compose logs -f
```

#### 6. Set Up Automatic Backups

Create backup script `/opt/mdrive/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/opt/backups/mdrive"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec mdrive-mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD mdrive > $BACKUP_DIR/db_$DATE.sql

# Backup user files
tar -czf $BACKUP_DIR/userdata_$DATE.tar.gz /opt/mdrive/backend/userdata

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and add to crontab:
```bash
chmod +x /opt/mdrive/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/mdrive/backup.sh") | crontab -
```

---

### Option 2: Traditional Server Deployment

#### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# Install Nginx
sudo apt install nginx -y
```

#### 2. Set Up Application

```bash
# Create application directory
sudo mkdir -p /var/www/mdrive
cd /var/www/mdrive

# Clone repository
sudo git clone <your-repo-url> .

# Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configure environment
sudo cp .env.example .env
sudo nano .env  # Update with production settings

# Initialize database
python init_db.py
```

#### 3. Build Frontend

```bash
cd /var/www/mdrive/frontend
npm install
npm run build
```

#### 4. Configure Gunicorn

Create `/etc/systemd/system/mdrive-backend.service`:
```ini
[Unit]
Description=MDrive Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/mdrive/backend
Environment="PATH=/var/www/mdrive/backend/venv/bin"
ExecStart=/var/www/mdrive/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mdrive-backend
sudo systemctl start mdrive-backend
sudo systemctl status mdrive-backend
```

#### 5. Configure Nginx

Create `/etc/nginx/sites-available/mdrive`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    root /var/www/mdrive/frontend/dist;
    index index.html;

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # File upload settings
        client_max_body_size 100M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/mdrive /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. Set Up SSL with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check backend
curl http://localhost:5000/api/auth/login

# Check frontend
curl http://localhost

# Check SSL
curl https://yourdomain.com
```

### 2. Set Up Monitoring

Install monitoring tools:
```bash
# Install htop for system monitoring
sudo apt install htop -y

# Install MySQL monitoring
sudo apt install mytop -y
```

Create health check script `/opt/mdrive/health-check.sh`:
```bash
#!/bin/bash

# Check backend
if ! curl -f http://localhost:5000/api/auth/login > /dev/null 2>&1; then
    echo "Backend is down!" | mail -s "MDrive Alert" admin@yourdomain.com
    systemctl restart mdrive-backend
fi

# Check database
if ! mysqladmin ping -h localhost --silent; then
    echo "Database is down!" | mail -s "MDrive Alert" admin@yourdomain.com
    systemctl restart mysql
fi
```

Add to crontab (every 5 minutes):
```bash
*/5 * * * * /opt/mdrive/health-check.sh
```

### 3. Configure Log Rotation

Create `/etc/logrotate.d/mdrive`:
```
/var/log/mdrive/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### 4. Set Up Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

## Performance Tuning

### MySQL Optimization

Edit `/etc/mysql/mysql.conf.d/mysqld.cnf`:
```ini
[mysqld]
# InnoDB settings
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# Query cache
query_cache_type = 1
query_cache_size = 64M

# Connections
max_connections = 200
```

### Nginx Caching

Add to nginx config:
```nginx
# Cache configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=mdrive_cache:10m max_size=1g inactive=60m;

location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Gunicorn Workers

Adjust workers based on CPU cores:
```bash
# Workers = (2 x CPU cores) + 1
# For 2 cores: 5 workers
gunicorn -w 5 -b 127.0.0.1:5000 run:app
```

---

## Maintenance

### Update Application

```bash
cd /var/www/mdrive
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart mdrive-backend

# Frontend
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

### Database Migrations

```bash
cd /var/www/mdrive/backend
source venv/bin/activate
flask db upgrade
```

### Monitor Logs

```bash
# Backend logs
sudo journalctl -u mdrive-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# MySQL logs
sudo tail -f /var/log/mysql/error.log
```

---

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Backend Instances**: Run multiple Gunicorn instances
3. **Shared Storage**: Use NFS or S3 for user files
4. **Database Replication**: Set up MySQL master-slave replication
5. **Redis Cache**: Implement caching layer

### Vertical Scaling

- Increase server resources (CPU, RAM, storage)
- Optimize database queries
- Implement CDN for static assets
- Use database connection pooling

---

## Security Best Practices

1. **Keep Software Updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Regular Security Audits**
   - Monitor access logs
   - Review user activities
   - Check for suspicious uploads

3. **Implement Rate Limiting**
   - Add Flask-Limiter to backend
   - Configure nginx rate limiting

4. **Database Security**
   - Use strong passwords
   - Limit database access to localhost
   - Regular security patches

5. **File Upload Security**
   - Validate file types strictly
   - Scan for malware
   - Limit file sizes

---

## Troubleshooting Production Issues

### High CPU Usage
```bash
# Check processes
htop

# Check Gunicorn workers
ps aux | grep gunicorn
```

### Database Connection Errors
```bash
# Check MySQL connections
mysql -e "SHOW PROCESSLIST;"

# Restart MySQL
sudo systemctl restart mysql
```

### Out of Disk Space
```bash
# Check disk usage
df -h

# Find large files
du -sh /var/www/mdrive/* | sort -hr | head -10

# Clean old backups
find /opt/backups -mtime +30 -delete
```

---

## Support and Monitoring

### Set Up Email Alerts

Configure system to send alerts:
```bash
# Install mail utilities
sudo apt install mailutils -y

# Configure alerts in cron jobs
```

### Application Monitoring

Consider using:
- **Sentry**: Error tracking
- **New Relic**: Application performance
- **Datadog**: Infrastructure monitoring
- **Prometheus + Grafana**: Custom metrics

---

## Backup Strategy

### What to Backup
1. MySQL database
2. User uploaded files (/userdata)
3. Configuration files (.env)
4. SSL certificates

### Backup Schedule
- **Daily**: Database and user files
- **Weekly**: Full system backup
- **Monthly**: Offsite backup

### Restore Procedure
```bash
# Restore database
mysql -u root -p mdrive < backup.sql

# Restore user files
tar -xzf userdata_backup.tar.gz -C /var/www/mdrive/backend/
```

---

This deployment guide ensures a production-ready MDrive installation with security, performance, and reliability.
