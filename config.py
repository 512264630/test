import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
    
    if DB_TYPE == 'mysql':
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = int(os.getenv('DB_PORT', 3306))
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
        DB_NAME = os.getenv('DB_NAME', 'temp_monitor')
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///temp_monitor.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
    MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
    MQTT_USER = os.getenv('MQTT_USER', '')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
    
    topic_str = os.getenv('MQTT_TOPICS', 'temp_monitor/+/data,device/temp/#')
    MQTT_TOPICS = [t.strip() for t in topic_str.split(',') if t.strip()]
    
    MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'temp_monitor_server')
    
    ALERT_MIN_TEMP = float(os.getenv('ALERT_MIN_TEMP', -10.0))
    ALERT_MAX_TEMP = float(os.getenv('ALERT_MAX_TEMP', 30.0))
    ALERT_TOPIC = os.getenv('ALERT_TOPIC', 'alert/temp')
    
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')