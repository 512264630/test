CREATE DATABASE IF NOT EXISTS temp_monitor
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE temp_monitor;

DROP TABLE IF EXISTS alert_log;
DROP TABLE IF EXISTS temp_data;
DROP TABLE IF EXISTS device_info;

CREATE TABLE device_info (
    device_id    VARCHAR(50) PRIMARY KEY,
    device_name  VARCHAR(100) NOT NULL,
    location     VARCHAR(100),
    status       TINYINT(1) DEFAULT 1 COMMENT '1=启用 0=禁用',
    online       TINYINT(1) DEFAULT 0 COMMENT '0=离线 1=在线',
    last_seen    DATETIME NULL,
    first_seen   DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB
COMMENT='设备信息表';

CREATE TABLE temp_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    device_id    VARCHAR(50),
    temperature  FLOAT,
    collect_time DATETIME,
    create_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_device FOREIGN KEY (device_id)
        REFERENCES device_info(device_id)
) ENGINE=InnoDB
COMMENT='温度采集表';

CREATE TABLE alert_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    device_id    VARCHAR(50),
    alert_type   VARCHAR(50),
    value        FLOAT,
    msg          VARCHAR(255),
    status       TINYINT(1) DEFAULT 0 COMMENT '0=未恢复 1=已恢复',
    create_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alert_device FOREIGN KEY (device_id)
        REFERENCES device_info(device_id)
) ENGINE=InnoDB
COMMENT='告警日志表';

CREATE INDEX idx_temp_data_device_id ON temp_data(device_id);
CREATE INDEX idx_temp_data_collect_time ON temp_data(collect_time);
CREATE INDEX idx_alert_log_device_id ON alert_log(device_id);
CREATE INDEX idx_alert_log_create_time ON alert_log(create_time);