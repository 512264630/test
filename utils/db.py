from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from models import Base, DeviceInfo, TempData, AlertLog
from datetime import datetime

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_size=20, max_overflow=5)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()

def init_db():
    Base.metadata.create_all(engine)

def add_device(session, device_id, device_name, location=None):
    device = session.query(DeviceInfo).filter_by(device_id=device_id).first()
    if device:
        device.device_name = device_name
        if location:
            device.location = location
        device.update_time = datetime.now()
    else:
        device = DeviceInfo(
            device_id=device_id,
            device_name=device_name,
            location=location,
            status=1,
            online=0
        )
        session.add(device)
    session.commit()
    return device

def update_device_online(session, device_id, online):
    device = session.query(DeviceInfo).filter_by(device_id=device_id).first()
    if device:
        device.online = online
        device.last_seen = datetime.now()
        session.commit()
        return True
    return False

def add_temp_data(session, device_id, temperature, collect_time=None):
    data = TempData(
        device_id=device_id,
        temperature=temperature,
        collect_time=collect_time or datetime.now()
    )
    session.add(data)
    session.commit()
    return data

def add_alert(session, device_id, alert_type, value, msg):
    alert = AlertLog(
        device_id=device_id,
        alert_type=alert_type,
        value=value,
        msg=msg,
        status=0
    )
    session.add(alert)
    session.commit()
    return alert

def get_device(session, device_id):
    return session.query(DeviceInfo).filter_by(device_id=device_id).first()

def get_all_devices(session):
    return session.query(DeviceInfo).all()

def get_device_temp_data(session, device_id, start_time=None, end_time=None):
    query = session.query(TempData).filter_by(device_id=device_id)
    if start_time:
        query = query.filter(TempData.collect_time >= start_time)
    if end_time:
        query = query.filter(TempData.collect_time <= end_time)
    return query.order_by(TempData.collect_time.desc()).all()

def get_device_alerts(session, device_id, status=None):
    query = session.query(AlertLog).filter_by(device_id=device_id)
    if status is not None:
        query = query.filter_by(status=status)
    return query.order_by(AlertLog.create_time.desc()).all()

def get_all_alerts(session, status=None):
    query = session.query(AlertLog)
    if status is not None:
        query = query.filter_by(status=status)
    return query.order_by(AlertLog.create_time.desc()).all()

def update_alert_status(session, alert_id, status):
    alert = session.query(AlertLog).filter_by(id=alert_id).first()
    if alert:
        alert.status = status
        session.commit()
        return True
    return False