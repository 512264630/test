from flask import Flask, jsonify, request
from datetime import datetime
from utils.db import (
    get_session, add_device, get_device, get_all_devices,
    get_device_temp_data, get_device_alerts, get_all_alerts,
    update_device_online, update_alert_status
)

app = Flask(__name__)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    session = get_session()
    try:
        devices = get_all_devices(session)
        return jsonify([d.to_dict() for d in devices])
    finally:
        session.close()

@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device_info(device_id):
    session = get_session()
    try:
        device = get_device(session, device_id)
        if device:
            return jsonify(device.to_dict())
        return jsonify({'error': '设备不存在'}), 404
    finally:
        session.close()

@app.route('/api/devices', methods=['POST'])
def create_device():
    data = request.json
    device_id = data.get('device_id')
    device_name = data.get('device_name')
    location = data.get('location')
    
    if not device_id or not device_name:
        return jsonify({'error': '缺少必要参数'}), 400
    
    session = get_session()
    try:
        device = add_device(session, device_id, device_name, location)
        return jsonify(device.to_dict()), 201
    finally:
        session.close()

@app.route('/api/devices/<device_id>/data', methods=['GET'])
def get_device_data(device_id):
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    session = get_session()
    try:
        device = get_device(session, device_id)
        if not device:
            return jsonify({'error': '设备不存在'}), 404
        
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None
        
        data = get_device_temp_data(session, device_id, start_dt, end_dt)
        return jsonify([d.to_dict() for d in data])
    finally:
        session.close()

@app.route('/api/devices/<device_id>/alerts', methods=['GET'])
def get_device_alert_logs(device_id):
    status = request.args.get('status', type=int)
    
    session = get_session()
    try:
        device = get_device(session, device_id)
        if not device:
            return jsonify({'error': '设备不存在'}), 404
        
        alerts = get_device_alerts(session, device_id, status)
        return jsonify([a.to_dict() for a in alerts])
    finally:
        session.close()

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    status = request.args.get('status', type=int)
    
    session = get_session()
    try:
        alerts = get_all_alerts(session, status)
        return jsonify([a.to_dict() for a in alerts])
    finally:
        session.close()

@app.route('/api/alerts/<alert_id>/status', methods=['PUT'])
def update_alert(alert_id):
    data = request.json
    status = data.get('status')
    
    if status not in [0, 1]:
        return jsonify({'error': '状态值无效'}), 400
    
    session = get_session()
    try:
        success = update_alert_status(session, alert_id, status)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': '告警记录不存在'}), 404
    finally:
        session.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

def run_api(host, port):
    app.run(host=host, port=port, debug=False)