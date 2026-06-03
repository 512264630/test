from config import Config
from utils.db import add_alert, get_session

class AlertService:
    def __init__(self):
        self.min_temp = Config.ALERT_MIN_TEMP
        self.max_temp = Config.ALERT_MAX_TEMP
    
    def check_temperature(self, device_id, temperature):
        alerts = []
        
        if temperature < self.min_temp:
            alerts.append({
                'type': 'LOW_TEMP',
                'value': temperature,
                'msg': f'温度过低: {temperature}°C，低于阈值 {self.min_temp}°C'
            })
        
        if temperature > self.max_temp:
            alerts.append({
                'type': 'HIGH_TEMP',
                'value': temperature,
                'msg': f'温度过高: {temperature}°C，高于阈值 {self.max_temp}°C'
            })
        
        if alerts:
            session = get_session()
            try:
                for alert in alerts:
                    add_alert(session, device_id, alert['type'], alert['value'], alert['msg'])
            finally:
                session.close()
        
        return alerts