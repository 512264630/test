from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DeviceInfo(Base):
    __tablename__ = 'device_info'
    
    device_id = Column(String(50), primary_key=True)
    device_name = Column(String(100), nullable=False)
    location = Column(String(100))
    status = Column(Integer, default=1)
    online = Column(Integer, default=0)
    last_seen = Column(DateTime)
    first_seen = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'location': self.location,
            'status': self.status,
            'online': self.online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }

class TempData(Base):
    __tablename__ = 'temp_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), ForeignKey('device_info.device_id'))
    temperature = Column(Float)
    collect_time = Column(DateTime)
    create_time = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'temperature': self.temperature,
            'collect_time': self.collect_time.isoformat() if self.collect_time else None,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }

class AlertLog(Base):
    __tablename__ = 'alert_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), ForeignKey('device_info.device_id'))
    alert_type = Column(String(50))
    value = Column(Float)
    msg = Column(String(255))
    status = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alert_type': self.alert_type,
            'value': self.value,
            'msg': self.msg,
            'status': self.status,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }