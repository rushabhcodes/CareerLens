-- For an existing MySQL 8 installation. Replace the password before executing.
-- This is an example bootstrap script, not the source of application secrets.
CREATE DATABASE IF NOT EXISTS careerlens CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS 'careerlens'@'127.0.0.1' IDENTIFIED BY 'REPLACE_WITH_ENV_PASSWORD';
GRANT ALL PRIVILEGES ON careerlens.* TO 'careerlens'@'127.0.0.1';
-- Optional development-only permission needed by Django's test database lifecycle.
GRANT ALL PRIVILEGES ON test_careerlens.* TO 'careerlens'@'127.0.0.1';
-- Apply the canonical application schema with: python backend/manage.py migrate
