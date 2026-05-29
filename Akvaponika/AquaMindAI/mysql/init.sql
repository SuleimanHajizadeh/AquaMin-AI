CREATE DATABASE IF NOT EXISTS aquamind CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aquamind;

CREATE TABLE IF NOT EXISTS pools (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL DEFAULT 'Ana Hovuz',
    species VARCHAR(100) DEFAULT 'Tilapia / Şirbit',
    volume_liters FLOAT DEFAULT 500.0,
    location VARCHAR(200) DEFAULT 'Bakı, Azərbaycan',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT IGNORE INTO pools VALUES (1,'AquaMind Demo Hovuzu','Tilapia',500,'Bakı, Azərbaycan',NOW());

CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pool_id INT NOT NULL DEFAULT 1,
    timestamp DATETIME NOT NULL,
    water_temp_c FLOAT COMMENT 'DS18B20 - Su temperaturu',
    water_level_cm FLOAT COMMENT 'HC-SR04 - Su seviyyesi',
    air_temp_c FLOAT COMMENT 'DHT11 - Hava temperaturu',
    air_humidity_pct FLOAT COMMENT 'DHT11 - Hava rutubeti',
    source ENUM('mock','arduino','manual') DEFAULT 'mock',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_pool_time (pool_id, timestamp)
);

CREATE TABLE IF NOT EXISTS ai_predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pool_id INT NOT NULL DEFAULT 1,
    predicted_at DATETIME NOT NULL,
    target_time DATETIME NOT NULL,
    metric VARCHAR(50),
    predicted_value FLOAT,
    confidence FLOAT,
    model_used VARCHAR(50) DEFAULT 'RandomForest',
    INDEX idx_predicted_at (predicted_at)
);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pool_id INT NOT NULL DEFAULT 1,
    timestamp DATETIME NOT NULL,
    severity ENUM('critical','warning','info') NOT NULL,
    sensor VARCHAR(50),
    message TEXT,
    value FLOAT,
    threshold_min FLOAT,
    threshold_max FLOAT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME NULL
);
