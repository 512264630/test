import logging
import threading
import signal
import sys
from config import Config
from utils.db import init_db
from mqtt_client.client import MQTTClient
from api.routes import run_api

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

mqtt_client = None
api_thread = None

def signal_handler(signal, frame):
    logger.info('收到停止信号，正在关闭服务...')
    if mqtt_client:
        mqtt_client.stop()
        logger.info('MQTT客户端已停止')
    sys.exit(0)

def main():
    global mqtt_client, api_thread
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info('初始化温度监控系统...')
    
    logger.info('初始化数据库...')
    init_db()
    logger.info('数据库初始化完成')
    
    logger.info('启动MQTT客户端...')
    mqtt_client = MQTTClient()
    mqtt_client.start()
    logger.info('MQTT客户端启动完成')
    
    logger.info('启动API服务...')
    api_thread = threading.Thread(
        target=run_api,
        args=(Config.API_HOST, Config.API_PORT),
        daemon=True
    )
    api_thread.start()
    logger.info(f'API服务已启动在 http://{Config.API_HOST}:{Config.API_PORT}')
    
    logger.info('温度监控系统启动完成')
    
    try:
        api_thread.join()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main()