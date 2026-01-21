-- Script pour créer la base de données MDrive
-- Exécutez ce script avec : mysql -u root -p < create_database.sql

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS mdrive CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer un utilisateur dédié (optionnel mais recommandé)
-- CREATE USER IF NOT EXISTS 'mdrive_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
-- GRANT ALL PRIVILEGES ON mdrive.* TO 'mdrive_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Afficher les bases de données
SHOW DATABASES;
