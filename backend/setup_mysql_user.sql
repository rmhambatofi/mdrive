-- Script pour créer la base de données et l'utilisateur MDrive
-- Exécutez avec : mysql -u root -p < setup_mysql_user.sql

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS mdrive CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur (changez le mot de passe)
CREATE USER IF NOT EXISTS 'mdrive_user'@'localhost' IDENTIFIED BY 'root_password';
CREATE USER IF NOT EXISTS 'mdrive_user'@'%' IDENTIFIED BY 'root_password';

-- Accorder tous les privilèges sur la base mdrive
GRANT ALL PRIVILEGES ON mdrive.* TO 'mdrive_user'@'localhost';
GRANT ALL PRIVILEGES ON mdrive.* TO 'mdrive_user'@'%';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Vérifier
SELECT user, host FROM mysql.user WHERE user = 'mdrive_user';
SHOW GRANTS FOR 'mdrive_user'@'localhost';
