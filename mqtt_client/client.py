import json
import logging
import paho.mqtt.client as mqtt
from datetime import datetime
from config import Config
from utils.db import get_session, add_temp_data, update_device_online, add_device
from utils.alert import AlertService

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, Config.MQTT_CLIENT_ID)
        if Config.MQTT_USER:
            self.client.username_pw_set(Config.MQTT_USER, Config.MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.alert_service = AlertService()
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info('MQTT连接成功')
            for topic in Config.MQTT_TOPICS:
                self.client.subscribe(topic)
                logger.info(f'已订阅主题: {topic}')
        else:
            logger.error(f'MQTT连接失败，错误码: {rc}')
    
    def parse_device_id(self, topic):
        parts = topic.split('/')
        
        if len(parts) >= 2:
            if parts[0] == 'temp_monitor' and len(parts) >= 2:
                return parts[1]
            elif parts[0] == 'device' and parts[1] == 'temp' and len(parts) >= 3:
                return parts[2]
        
        return parts[-1] if parts else 'unknown'
    
    def parse_payload(self, payload_str, device_id):
        payload_str = payload_str.strip()
        
        if payload_str.startswith('{'):
            data = json.loads(payload_str)
            device_id = data.get('device_id', device_id)
            temperature = data.get('temp') or data.get('temperature')
            device_name = data.get('device_name', device_id)
            location = data.get('location')
        else:
            temperature = float(payload_str)
            device_name = device_id
            location = None
        
        return device_id, temperature, device_name, location
    
    def publish_alert(self, device_id, temperature, msg):
        if Config.ALERT_TOPIC:
            alert_data = {
                'device_id': device_id,
                'temperature': temperature,
                'msg': msg,
                'threshold': Config.ALERT_MAX_TEMP,
                'time': datetime.now().isoformat()
            }
            self.client.publish(Config.ALERT_TOPIC, json.dumps(alert_data))
            logger.info(f'已发送MQTT告警到 {Config.ALERT_TOPIC}: {alert_data}')
    
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload_bytes = msg.payload.decode('utf-8')
            logger.info(f'收到主题: {topic}  数据: {payload_bytes}')
            
            device_id = self.parse_device_id(topic)
            device_id, temperature, device_name, location = self.parse_payload(payload_bytes, device_id)
            
            if temperature is None:
                logger.error(f'消息缺少温度数据: {msg.payload}')
                return
            
            temperature = float(temperature)
            
            session = get_session()
            try:
                add_device(session, device_id, device_name, location)
                update_device_online(session, device_id, 1)
                add_temp_data(session, device_id, temperature)
                
                alerts = self.alert_service.check_temperature(device_id, temperature)
                for alert in alerts:
                    self.publish_alert(device_id, temperature, alert['msg'])
                
                logger.info(f'入库成功: 设备={device_id}  温度={temperature}°C')
                
                if temperature > Config.ALERT_MAX_TEMP:
                    self.publish_alert(device_id, temperature, f'温度{temperature}°C超过预警值{Config.ALERT_MAX_TEMP}°C')
                    
            finally:
                session.close()
                
        except json.JSONDecodeError as e:
            logger.error(f'JSON解析失败: {e}')
        except Exception as e:
            logger.error(f'处理消息时出错: {e}')
    
    def on_disconnect(self, client, userdata, rc):
        logger.warning(f'MQTT断开连接，错误码: {rc}')
        if rc != 0:
            self.connect()
    
    def connect(self):
        try:
            logger.info(f'连接到MQTT服务器: {Config.MQTT_BROKER}:{Config.MQTT_PORT}')
            self.client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)
        except Exception as e:
            logger.error(f'连接MQTT服务器失败: {e}')
    
    def start(self):
        self.connect()
        self.client.loop_start()
    
    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()