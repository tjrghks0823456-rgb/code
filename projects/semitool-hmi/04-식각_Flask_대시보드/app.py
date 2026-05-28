from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
from datetime import datetime
from data_manager import DataManager
from etch_ai import etch_ai_status_payload, etch_ai_predict_stub

# bat/IDE 어디서 실행하든 templates 를 찾도록 앱 루트 고정 (__main__ 일 때 cwd에 따라 404 나는 문제 방지)
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_DASHBOARD_HTML = os.path.join(_APP_DIR, 'templates', 'etch_dashboard.html')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(_APP_DIR, 'flask_server.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__, root_path=_APP_DIR)
CORS(app)

use_database = False
data_manager = DataManager(use_db=use_database)


def serve_dashboard():
    """대시보드 HTML (절대 경로 send_file — 경로/버전 이슈로 404 나는 경우 방지)."""
    if not os.path.isfile(_DASHBOARD_HTML):
        app.logger.error('템플릿 없음: %s (root=%s)', _DASHBOARD_HTML, _APP_DIR)
        return (
            jsonify({
                'error': '대시보드 파일 없음',
                'expected': _DASHBOARD_HTML,
                'app_dir': _APP_DIR,
            }),
            404,
        )
    return send_file(_DASHBOARD_HTML, mimetype='text/html; charset=utf-8', max_age=0)


@app.route('/')
@app.route('/index.html')
@app.route('/etch_dashboard.html')
@app.route('/dashboard')
def index():
    return serve_dashboard()


@app.errorhandler(404)
def page_not_found(_e):
    """어떤 URL로 들어왔는지 표시 — 오타·다른 포트의 앱과 구분에 도움."""
    p = request.path or ''
    body = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"/><title>404 · 식각 HMI</title></head>
<body style="font-family:Segoe UI,Malgun Gothic,sans-serif;padding:24px;">
<h1>404 — 식각 HMI Flask</h1>
<p>요청한 경로: <code>{p}</code></p>
<p>아래 중 하나로 접속해 보세요.</p>
<ul>
  <li><a href="/">/ · 메인 대시보드</a></li>
  <li><a href="/index.html">/index.html</a></li>
  <li><a href="/etch_dashboard.html">/etch_dashboard.html</a></li>
  <li><a href="/api/sensors">/api/sensors</a> (JSON 스냅샷)</li>
</ul>
<p style="color:#666;font-size:14px;">이 박스가 보이면 이 프로세스는 <strong>etchflask app.py</strong>입니다.
다른 화면이 나오면 5000 포트에 다른 프로그램이 떠 있을 수 있습니다.</p>
</body></html>"""
    return body, 404, {'Content-Type': 'text/html; charset=utf-8'}


@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        logs = data_manager.get_logs(limit=500)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    """최신 식각 HMI 스냅샷 (메모리: 마지막 수신 건)."""
    try:
        sensor_data = data_manager.get_latest_sensor_data(farm_id=None)
        if not sensor_data.get('sensors'):
            app.logger.debug("센서 데이터 없음 — WPF 실행 및 POST /api/etch/sensor-data 확인")
        return jsonify(sensor_data)
    except Exception as e:
        app.logger.error(f"센서 데이터 조회 오류: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/save-logs', methods=['POST'])
def save_logs():
    try:
        data = request.get_json()
        file_path = data.get('filePath', '') if isinstance(data, dict) else ''
        if not file_path:
            file_path = os.path.join(_APP_DIR, 'logs', f'EtchHMI_Logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        logs = data.get('logs', []) if isinstance(data, dict) else []
        success = data_manager.save_logs_to_file(file_path, logs)
        if success:
            return jsonify({"success": True, "message": "로그 저장 완료"})
        return jsonify({"success": False, "message": "로그 저장 실패"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/load-logs-file', methods=['POST'])
def load_logs_file():
    try:
        content = request.get_data(as_text=True)
        if '\n' in content or len(content) > 260:
            logs = data_manager.parse_logs_from_content(content)
        else:
            file_path = content.strip().strip('"\'')
            logs = data_manager.load_logs_from_file(file_path)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/add-logs', methods=['POST'])
def add_logs():
    try:
        logs_json = request.get_data(as_text=True)
        success = data_manager.add_logs_from_json(logs_json)
        if success:
            return jsonify({"success": True, "message": "로그 추가 완료"})
        return jsonify({"success": False, "message": "로그 추가 실패"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/load-logs', methods=['GET'])
def load_logs():
    try:
        logs = data_manager.get_logs(limit=500)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/etch/sensor-data', methods=['POST'])
def receive_etch_sensor_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "데이터가 없습니다"}), 400

        sensor_data = {
            'currentFarm': data.get('equipmentId', 1),
            'powerOn': data.get('powerOn', False),
            'connected': data.get('connected', False),
            'lastUpdate': data.get('lastUpdate', datetime.now().isoformat()),
            'sensors': [
                {'name': '온도', 'rawValue': data.get('temperature', 0)},
                {'name': '습도', 'rawValue': data.get('humidity', 0)},
                {'name': '압력', 'rawValue': data.get('pressure', 0)},
                {'name': '진동', 'rawValue': data.get('vibration', 0)}
            ],
            'equipmentState': data.get('equipmentState'),
            'alarmCode': data.get('alarmCode'),
            'accessSafe': data.get('accessSafe'),
            'interlockOk': data.get('interlockOk'),
            'username': data.get('username'),
        }

        data_manager.save_sensor_data(sensor_data)
        return jsonify({"success": True, "message": "식각 센서 데이터 수신 완료"})
    except Exception as e:
        app.logger.error(f"식각 센서 데이터 수신 오류: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/etch/history', methods=['GET'])
def etch_history():
    try:
        limit = request.args.get('limit', default=500, type=int)
        return jsonify({"success": True, "items": data_manager.get_etch_telemetry_history(limit)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/etch/events', methods=['GET'])
def etch_events():
    try:
        limit = request.args.get('limit', default=100, type=int)
        return jsonify({"success": True, "items": data_manager.get_etch_events(limit)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/etch/summary', methods=['GET'])
def etch_summary():
    try:
        s = data_manager.get_etch_summary()
        snap = data_manager.get_latest_sensor_data(farm_id=None)
        s['live'] = {
            'equipmentState': snap.get('equipmentState'),
            'alarmCode': snap.get('alarmCode'),
            'interlockOk': snap.get('interlockOk'),
            'lastUpdate': snap.get('lastUpdate'),
            'username': snap.get('username'),
            'accessSafe': snap.get('accessSafe'),
        }
        return jsonify({"success": True, "summary": s})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/etch/ai/status', methods=['GET'])
def etch_ai_status():
    return jsonify(etch_ai_status_payload())


@app.route('/api/etch/ai/predict', methods=['POST'])
def etch_ai_predict():
    try:
        payload = request.get_json() or {}
        return jsonify(etch_ai_predict_stub(payload))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    import webbrowser
    import threading
    import time

    os.makedirs(os.path.join(_APP_DIR, 'logs'), exist_ok=True)
    os.makedirs(os.path.join(_APP_DIR, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(_APP_DIR, 'models'), exist_ok=True)

    print("메모리 모드 (DB 사용 안 함) — 식각 HMI 전용")
    print(f"[etchflask] 앱 폴더: {_APP_DIR}")
    print(f"[etchflask] 대시보드 파일: {_DASHBOARD_HTML} (존재: {os.path.isfile(_DASHBOARD_HTML)})")

    def open_browser():
        time.sleep(1.5)
        url = 'http://localhost:5000'
        print(f"\n브라우저: {url}")
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    print("\n" + "=" * 50)
    print("Flask: http://localhost:5000")
    print("=" * 50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
