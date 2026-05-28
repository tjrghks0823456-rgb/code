import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class DataManager:
    """센서 데이터 및 로그를 관리하는 클래스"""
    
    def __init__(self, db_path='data/smart_farm.db', use_db=True):
        """
        Args:
            db_path: 데이터베이스 파일 경로
            use_db: DB 사용 여부 (False면 메모리 기반)
        """
        self.use_db = use_db
        self.db_path = db_path if use_db else ':memory:'
        
        # 메모리 기반일 때는 인메모리 리스트 사용
        if not use_db:
            self.sensor_data_list = []
            self.logs_list = []
            self.production_data_list = []
            # WPF → Flask 식각 텔레메트리 링버퍼(모니터링/리포트용)
            self.etch_history: List[Dict[str, Any]] = []
            self.etch_events: List[Dict[str, Any]] = []
            self._last_etch_equipment_state: Optional[str] = None
            self._last_etch_alarm: Optional[str] = None
            self._last_etch_interlock: Optional[bool] = None
        else:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def initialize_database(self):
        """데이터베이스 초기화 (DB 사용 시에만)"""
        if not self.use_db:
            # 메모리 모드에서는 초기화 불필요
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 센서 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                farm_id INTEGER NOT NULL,
                humidity REAL,
                temperature REAL,
                light REAL,
                soil_moisture REAL,
                power_on INTEGER,
                connected INTEGER
            )
        ''')
        
        # 로그 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL,
                date TEXT,
                log_type TEXT
            )
        ''')
        
        # 농장 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farm_info (
                farm_id INTEGER PRIMARY KEY,
                crop_name TEXT,
                note TEXT,
                last_updated TEXT
            )
        ''')
        
        # 생산량 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS production_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                farm_id INTEGER NOT NULL,
                production_amount REAL,
                unit TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def validate_sensor_value(self, sensor_key: str, value: float) -> float:
        """
        센서 값 검증 및 정규화
        
        Args:
            sensor_key: 센서 키 ('humidity', 'temperature', 'light', 'soil_moisture')
            value: 검증할 값
        
        Returns:
            검증된 값 (범위를 벗어난 경우 클리핑됨)
        """
        valid_ranges = {
            'humidity': (0, 100),
            'temperature': (-10, 50),
            'light': (0, 100),
            'soil_moisture': (0, 100)
        }
        
        if sensor_key in valid_ranges:
            min_val, max_val = valid_ranges[sensor_key]
            if value < min_val:
                return min_val
            elif value > max_val:
                return max_val
        return value
    
    def save_sensor_data(self, sensor_data: Dict[str, Any]):
        """센서 데이터 저장 (데이터 검증 포함)"""
        if not self.use_db:
            # 메모리 모드: 리스트에 추가 (최대 1000개 유지)
            timestamp = sensor_data.get('lastUpdate', datetime.now().isoformat())
            farm_id = sensor_data.get('currentFarm', 1)
            power_on = 1 if sensor_data.get('powerOn', False) else 0
            connected = 1 if sensor_data.get('connected', False) else 0
            
            sensors = sensor_data.get('sensors', [])
            
            # 센서 값 추출 및 검증
            humidity = None
            temperature = None
            light = None
            soil_moisture = None
            
            for sensor in sensors:
                name = sensor.get('name', '')
                raw_value = sensor.get('rawValue', 0)
                
                # 데이터 검증 및 정규화
                if name == '습도':
                    humidity = self.validate_sensor_value('humidity', raw_value)
                elif name == '온도':
                    temperature = self.validate_sensor_value('temperature', raw_value)
                elif name in ('채광', '압력'):
                    light = self.validate_sensor_value('light', raw_value)
                elif name in ('토양습도', '진동'):
                    soil_moisture = self.validate_sensor_value('soil_moisture', raw_value)
            
            data_entry = {
                'id': len(self.sensor_data_list) + 1,
                'timestamp': timestamp,
                'farm_id': farm_id,
                'humidity': humidity,
                'temperature': temperature,
                'light': light,
                'soil_moisture': soil_moisture,
                'power_on': power_on,
                'connected': connected
            }

            for ek in ('equipmentState', 'alarmCode', 'accessSafe', 'interlockOk', 'username'):
                if ek in sensor_data:
                    data_entry[ek] = sensor_data[ek]

            self.sensor_data_list.append(data_entry)
            self._append_etch_history_and_events(data_entry)
            
            # 최대 1000개까지만 유지 (오래된 데이터 삭제)
            if len(self.sensor_data_list) > 1000:
                self.sensor_data_list.pop(0)
            
            return
        
        # DB 모드
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            timestamp = sensor_data.get('lastUpdate', datetime.now().isoformat())
            farm_id = sensor_data.get('currentFarm', 1)
            power_on = 1 if sensor_data.get('powerOn', False) else 0
            connected = 1 if sensor_data.get('connected', False) else 0
            
            sensors = sensor_data.get('sensors', [])
            
            # 센서 값 추출
            humidity = None
            temperature = None
            light = None
            soil_moisture = None
            
            for sensor in sensors:
                name = sensor.get('name', '')
                raw_value = sensor.get('rawValue', 0)
                
                if name == '습도':
                    humidity = raw_value
                elif name == '온도':
                    temperature = raw_value
                elif name in ('채광', '압력'):
                    light = raw_value
                elif name in ('토양습도', '진동'):
                    soil_moisture = raw_value
            
            cursor.execute('''
                INSERT INTO sensor_data 
                (timestamp, farm_id, humidity, temperature, light, soil_moisture, power_on, connected)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, farm_id, humidity, temperature, light, soil_moisture, power_on, connected))
            
            conn.commit()
        except Exception as e:
            print(f"센서 데이터 저장 오류: {e}")
        finally:
            conn.close()

    def _ring_append(self, buf: List[Dict[str, Any]], item: Dict[str, Any], max_len: int) -> None:
        buf.append(item)
        overflow = len(buf) - max_len
        if overflow > 0:
            del buf[0:overflow]

    def _append_etch_history_and_events(self, data_entry: Dict[str, Any]) -> None:
        """메모리 모드: 수신 샘플을 이력에 넣고 상태·알람·인터록 변화는 이벤트로 남김."""
        if self.use_db:
            return

        ts = data_entry.get('timestamp', datetime.now().isoformat())
        sample: Dict[str, Any] = {
            'timestamp': ts,
            'equipmentId': data_entry.get('farm_id'),
            'temperature': data_entry.get('temperature'),
            'humidity': data_entry.get('humidity'),
            'pressure_kpa': data_entry.get('light'),
            'vibration_g': data_entry.get('soil_moisture'),
            'equipmentState': data_entry.get('equipmentState'),
            'alarmCode': data_entry.get('alarmCode'),
            'interlockOk': data_entry.get('interlockOk'),
            'accessSafe': data_entry.get('accessSafe'),
            'username': data_entry.get('username'),
            'connected': bool(data_entry.get('connected')),
            'powerOn': bool(data_entry.get('power_on')),
        }
        self._ring_append(self.etch_history, sample, 2500)

        st = data_entry.get('equipmentState')
        al = data_entry.get('alarmCode')
        il = data_entry.get('interlockOk')
        user = data_entry.get('username')

        def ev(kind: str, message: str) -> Dict[str, Any]:
            return {
                'time': ts,
                'kind': kind,
                'message': message,
                'equipmentState': st,
                'alarmCode': al,
                'interlockOk': il,
                'username': user,
            }

        if st is not None:
            prev_st = self._last_etch_equipment_state
            if prev_st is not None and str(st) != prev_st:
                self._ring_append(
                    self.etch_events,
                    ev('state_change', f"상태 {prev_st} → {st}"),
                    400,
                )
            self._last_etch_equipment_state = str(st)

        prev_al = self._last_etch_alarm
        cur_al = str(al) if al else None
        if cur_al != prev_al:
            if al:
                self._ring_append(
                    self.etch_events,
                    ev('alarm', f"알람: {al}"),
                    400,
                )
            elif prev_al:
                self._ring_append(
                    self.etch_events,
                    ev('alarm', f"알람 해제 (이전 {prev_al})"),
                    400,
                )
            self._last_etch_alarm = cur_al

        if isinstance(il, bool):
            prev_il = self._last_etch_interlock
            if prev_il is True and il is False:
                self._ring_append(
                    self.etch_events,
                    ev('interlock_lost', '인터록 미충족'),
                    400,
                )
            elif prev_il is False and il is True:
                self._ring_append(
                    self.etch_events,
                    ev('interlock_ok', '인터록 충족'),
                    400,
                )
            self._last_etch_interlock = il

    def get_etch_telemetry_history(self, limit: int = 500) -> List[Dict[str, Any]]:
        if self.use_db:
            return []
        n = max(1, min(int(limit), 2500))
        return list(self.etch_history[-n:])

    def get_etch_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        if self.use_db:
            return []
        n = max(1, min(int(limit), 400))
        return list(self.etch_events[-n:])[::-1]

    def get_etch_summary(self) -> Dict[str, Any]:
        """브라우저용 간단 KPI(메모리 이력 기준)."""
        if self.use_db or not self.etch_history:
            return {
                'samples': 0,
                'last': None,
                'runningRatio': None,
                'alarmEvents': 0,
                'interlockEvents': 0,
            }

        hist = self.etch_history
        last = dict(hist[-1])
        total = len(hist)
        run_ct = sum(
            1
            for s in hist
            if str(s.get('equipmentState') or '').upper() == 'RUNNING'
        )
        alarm_ev = sum(1 for e in self.etch_events if e.get('kind') == 'alarm')
        il_ev = sum(1 for e in self.etch_events if e.get('kind') == 'interlock_lost')
        return {
            'samples': total,
            'last': last,
            'runningRatio': round(run_ct / total, 4) if total else None,
            'alarmEvents': alarm_ev,
            'interlockEvents': il_ev,
        }
    
    def get_latest_sensor_data(self, farm_id: Optional[int] = None) -> Dict[str, Any]:
        """
        최신 센서 데이터 가져오기 (농장별 필터링 지원)
        
        Args:
            farm_id: 특정 농장 ID (None이면 전체 농장 중 최신 데이터)
        """
        if not self.use_db:
            # 메모리 모드: 최신 데이터 반환
            if not self.sensor_data_list:
                return {
                    "currentFarm": farm_id or 1,
                    "powerOn": False,
                    "connected": False,
                    "lastUpdate": datetime.now().isoformat(),
                    "sensors": []
                }
            
            # farm_id가 지정되면 해당 농장의 최신 데이터만 반환
            if farm_id is not None:
                # 역순으로 검색하여 해당 농장의 최신 데이터 찾기
                for row_data in reversed(self.sensor_data_list):
                    if row_data.get('farm_id') == farm_id:
                        break
                else:
                    # 해당 농장 데이터가 없으면 빈 데이터 반환
                    return {
                        "currentFarm": farm_id,
                        "powerOn": False,
                        "connected": False,
                        "lastUpdate": datetime.now().isoformat(),
                        "sensors": []
                    }
            else:
                # farm_id가 없으면 전체 중 최신 데이터
                row_data = self.sensor_data_list[-1]
            
            result = {
                "currentFarm": row_data['farm_id'],
                "powerOn": bool(row_data['power_on']),
                "connected": bool(row_data['connected']),
                "lastUpdate": row_data['timestamp'],
                "sensors": [
                    {
                        "id": 1,
                        "name": "습도",
                        "value": f"{row_data['humidity']:.1f}%" if row_data['humidity'] is not None else "0%",
                        "rawValue": row_data['humidity'] if row_data['humidity'] is not None else 0,
                        "percentage": int(row_data['humidity']) if row_data['humidity'] is not None else 0,
                        "status": "정상"
                    },
                    {
                        "id": 2,
                        "name": "온도",
                        "value": f"{row_data['temperature']:.1f}℃" if row_data['temperature'] is not None else "0℃",
                        "rawValue": row_data['temperature'] if row_data['temperature'] is not None else 0,
                        "percentage": int(row_data['temperature']) if row_data['temperature'] is not None else 0,
                        "status": "정상"
                    },
                    {
                        "id": 3,
                        "name": "압력",
                        "value": f"{row_data['light']:.2f} kPa" if row_data['light'] is not None else "0 kPa",
                        "rawValue": row_data['light'] if row_data['light'] is not None else 0,
                        "percentage": int(row_data['light']) if row_data['light'] is not None else 0,
                        "status": "정상"
                    },
                    {
                        "id": 4,
                        "name": "진동",
                        "value": f"{row_data['soil_moisture']:.2f} g" if row_data['soil_moisture'] is not None else "0 g",
                        "rawValue": row_data['soil_moisture'] if row_data['soil_moisture'] is not None else 0,
                        "percentage": int(row_data['soil_moisture']) if row_data['soil_moisture'] is not None else 0,
                        "status": "정상"
                    }
                ]
            }
            for ek in ('equipmentState', 'alarmCode', 'accessSafe', 'interlockOk', 'username'):
                if ek in row_data:
                    result[ek] = row_data[ek]
            return result
        
        # DB 모드
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if farm_id is not None:
                # 특정 농장의 최신 데이터만 조회
                cursor.execute('''
                    SELECT * FROM sensor_data 
                    WHERE farm_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ''', (farm_id,))
            else:
                # 전체 농장 중 최신 데이터 조회
                cursor.execute('''
                    SELECT * FROM sensor_data 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ''')
            
            row = cursor.fetchone()
            
            # farm_id가 지정되었는데 데이터가 없으면 빈 데이터 반환
            if not row and farm_id is not None:
                return {
                    "currentFarm": farm_id,
                    "powerOn": False,
                    "connected": False,
                    "lastUpdate": datetime.now().isoformat(),
                    "sensors": []
                }
            
            if row:
                # DB 스키마: id, timestamp, farm_id, humidity, temperature, light, soil_moisture, power_on, connected
                return {
                    "currentFarm": row[2],
                    "powerOn": bool(row[7]),
                    "connected": bool(row[8]),
                    "lastUpdate": row[1],
                    "sensors": [
                        {
                            "id": 1,
                            "name": "습도",
                            "value": f"{row[3]:.1f}%" if row[3] is not None else "0%",
                            "rawValue": row[3] if row[3] is not None else 0,
                            "percentage": int(row[3]) if row[3] is not None else 0,
                            "status": "정상"
                        },
                        {
                            "id": 2,
                            "name": "온도",
                            "value": f"{row[4]:.1f}℃" if row[4] is not None else "0℃",
                            "rawValue": row[4] if row[4] is not None else 0,
                            "percentage": int(row[4]) if row[4] is not None else 0,
                            "status": "정상"
                        },
                        {
                            "id": 3,
                            "name": "압력",
                            "value": f"{row[5]:.2f} kPa" if row[5] is not None else "0 kPa",
                            "rawValue": row[5] if row[5] is not None else 0,
                            "percentage": int(row[5]) if row[5] is not None else 0,
                            "status": "정상"
                        },
                        {
                            "id": 4,
                            "name": "진동",
                            "value": f"{row[6]:.2f} g" if row[6] is not None else "0 g",
                            "rawValue": row[6] if row[6] is not None else 0,
                            "percentage": int(row[6]) if row[6] is not None else 0,
                            "status": "정상"
                        }
                    ]
                }
            else:
                # 기본값 반환
                return {
                    "currentFarm": 1,
                    "powerOn": False,
                    "connected": False,
                    "lastUpdate": datetime.now().isoformat(),
                    "sensors": []
                }
        finally:
            conn.close()
    
    def get_sensor_data_history(self, days: int = 7, farm_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """센서 데이터 히스토리 가져오기"""
        if not self.use_db:
            # 메모리 모드: 리스트에서 필터링
            if not self.sensor_data_list:
                return []
            
            result = []
            start_date = datetime.now() - timedelta(days=days)
            
            for data in self.sensor_data_list:
                try:
                    # 타임스탬프 파싱
                    if isinstance(data['timestamp'], str):
                        data_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                    else:
                        continue
                    
                    # 날짜 필터링
                    if data_time >= start_date:
                        if farm_id is None or data['farm_id'] == farm_id:
                            result.append({
                                "id": data['id'],
                                "timestamp": data['timestamp'],
                                "farm_id": data['farm_id'],
                                "humidity": data['humidity'],
                                "temperature": data['temperature'],
                                "light": data['light'],
                                "soil_moisture": data['soil_moisture'],
                                "power_on": bool(data['power_on']),
                                "connected": bool(data['connected'])
                            })
                except:
                    continue
            
            return sorted(result, key=lambda x: x['timestamp'])
        
        # DB 모드
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            if farm_id:
                cursor.execute('''
                    SELECT * FROM sensor_data 
                    WHERE timestamp >= ? AND farm_id = ?
                    ORDER BY timestamp ASC
                ''', (start_date, farm_id))
            else:
                cursor.execute('''
                    SELECT * FROM sensor_data 
                    WHERE timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (start_date,))
            
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                result.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "farm_id": row[2],
                    "humidity": row[3],
                    "temperature": row[4],
                    "light": row[5],
                    "soil_moisture": row[6],
                    "power_on": bool(row[7]),
                    "connected": bool(row[8])
                })
            
            return result
        finally:
            conn.close()
    
    def get_logs(self, limit: int = 500) -> List[Dict[str, Any]]:
        """로그 가져오기"""
        if not self.use_db:
            # 메모리 모드: 리스트에서 가져오기
            result = []
            for log in self.logs_list[-limit:]:
                result.append({
                    "timestamp": log.get('timestamp', datetime.now().strftime("%H:%M:%S")),
                    "message": log.get('message', ''),
                    "date": log.get('date', datetime.now().strftime("%Y-%m-%d")),
                    "log_type": log.get('log_type', 'info')
                })
            return result[::-1]  # 최신 순으로 반환
        
        # DB 모드
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT timestamp, message, date, log_type FROM logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                result.append({
                    "timestamp": row[0],
                    "message": row[1],
                    "date": row[2] or datetime.now().strftime("%Y-%m-%d"),
                    "log_type": row[3]
                })
            
            return result
        finally:
            conn.close()
    
    def add_log(self, message: str, log_type: str = 'info'):
        """로그 추가"""
        if not self.use_db:
            # 메모리 모드: 리스트에 추가
            log_entry = {
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'message': message,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'log_type': log_type
            }
            self.logs_list.append(log_entry)
            
            # 최대 1000개까지만 유지
            if len(self.logs_list) > 1000:
                self.logs_list.pop(0)
            return
        
        # DB 모드
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            date = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute('''
                INSERT INTO logs (timestamp, message, date, log_type)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, message, date, log_type))
            
            conn.commit()
        finally:
            conn.close()
    
    def save_logs_to_file(self, file_path: str, logs: List[str]) -> bool:
        """로그를 파일로 저장"""
        try:
            os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for log in logs:
                    f.write(log + '\n')
            
            return True
        except Exception as e:
            print(f"로그 파일 저장 오류: {e}")
            return False
    
    def load_logs_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """파일에서 로그 불러오기"""
        try:
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            logs = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # [HH:MM:SS] 형식의 타임스탬프 추출
                if line.startswith('[') and len(line) > 11:
                    timestamp = line[1:9] if ']' in line[:10] else datetime.now().strftime("%H:%M:%S")
                    message = line[11:].strip() if ']' in line[:10] else line
                else:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    message = line
                
                logs.append({
                    "timestamp": timestamp,
                    "message": message,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
            
            return logs[:500]  # 최대 500개
        except Exception as e:
            print(f"로그 파일 불러오기 오류: {e}")
            return []
    
    def parse_logs_from_content(self, content: str) -> List[Dict[str, Any]]:
        """로그 내용 파싱 - 다양한 타임스탬프 형식 지원"""
        import re
        try:
            lines = content.split('\n')
            logs = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                message = line
                
                # 다양한 타임스탬프 형식 지원
                if line.startswith('['):
                    # 형식 1: [HH:MM:SS] (예: [18:12:12])
                    match1 = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s*(.*)', line)
                    if match1:
                        timestamp = match1.group(1)
                        message = match1.group(2).strip()
                    else:
                        # 형식 2: [2025. 11. 19. 오후 5:19:41] 또는 [2025. 11. 19. 오전 10:30:15]
                        match2 = re.match(r'\[(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(오전|오후)\s*(\d{1,2}):(\d{2}):(\d{2})\]\s*(.*)', line)
                        if match2:
                            year = int(match2.group(1))
                            month = int(match2.group(2))
                            day = int(match2.group(3))
                            am_pm = match2.group(4)
                            hour = int(match2.group(5))
                            minute = int(match2.group(6))
                            second = int(match2.group(7))
                            message = match2.group(8).strip()
                            
                            # 오전/오후 변환
                            if am_pm == '오후' and hour != 12:
                                hour += 12
                            elif am_pm == '오전' and hour == 12:
                                hour = 0
                            
                            timestamp = f"{hour:02d}:{minute:02d}:{second:02d}"
                        else:
                            # 다른 형식의 타임스탬프 시도 (']' 앞부분을 타임스탬프로 간주)
                            bracket_end = line.find(']')
                            if bracket_end > 0:
                                timestamp_part = line[1:bracket_end]
                                message = line[bracket_end+1:].strip()
                                # 가능하면 타임스탬프 추출 시도
                                time_match = re.search(r'(\d{2}):(\d{2}):(\d{2})', timestamp_part)
                                if time_match:
                                    timestamp = time_match.group(0)
                
                logs.append({
                    "timestamp": timestamp,
                    "message": message,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
            
            return logs[:500]  # 최대 500개
        except Exception as e:
            print(f"로그 내용 파싱 오류: {e}")
            return []
    
    def extract_sensor_data_from_logs(self, logs: List[Dict[str, Any]], farm_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        로그에서 센서 데이터 추출하여 AI 분석용 형식으로 변환 (농장별 필터링 지원)
        
        Args:
            logs: 로그 리스트
            farm_id: 특정 농장 ID (None이면 모든 농장 데이터 추출, 로그에 farm_id 정보가 없으면 무시)
        """
        import re
        from datetime import datetime, timedelta
        
        sensor_data_list = []
        base_date = datetime.now().date()
        
        for log in logs:
            message = log.get('message', '')
            timestamp_str = log.get('timestamp', '')
            
            # 타임스탬프 파싱
            try:
                if timestamp_str and ':' in timestamp_str:
                    time_parts = timestamp_str.split(':')
                    if len(time_parts) >= 2:
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        second = int(time_parts[2]) if len(time_parts) > 2 else 0
                        timestamp = datetime.combine(base_date, datetime.min.time().replace(hour=hour, minute=minute, second=second))
                    else:
                        timestamp = datetime.now()
                else:
                    timestamp = datetime.now()
            except:
                timestamp = datetime.now()
            
            # 로그에서 farm_id 추출 (스마트팜 X번 형태로 저장된 경우)
            log_farm_id = None
            farm_match = re.search(r'스마트팜\s*(\d+)', message)
            if farm_match:
                log_farm_id = int(farm_match.group(1))
            elif 'farm_id' in log:
                log_farm_id = log.get('farm_id')
            
            # farm_id 필터링: 특정 농장 ID가 지정되었고, 로그에 farm_id가 있으면 필터링
            if farm_id is not None and log_farm_id is not None:
                if log_farm_id != farm_id:
                    continue  # 다른 농장 데이터는 스킵
            
            # 센서 데이터 추출
            sensor_data = {
                'timestamp': timestamp.isoformat(),
                'farm_id': log_farm_id if log_farm_id else (farm_id if farm_id else 1),  # 로그의 farm_id 우선 사용
                'humidity': None,
                'temperature': None,
                'light': None,
                'soil_moisture': None,
                'power_on': 1,
                'connected': 1
            }
            
            # 형식 1: 웹 표준 형식 우선 파싱: "센서데이터 습도:55.2% 온도:22.1℃ 채광:65.3% 토양습도:48.5%"
            if '센서데이터' in message:
                # 새 형식: 습도:값% 온도:값℃ 채광:값% 토양습도:값% (4개 센서 모두 포함되어야 함)
                humidity_match = re.search(r'습도:(\d+\.?\d*)\s*%', message)
                if humidity_match:
                    sensor_data['humidity'] = float(humidity_match.group(1))
                
                temp_match = re.search(r'온도:(\d+\.?\d*)\s*[℃°C]', message)
                if temp_match:
                    sensor_data['temperature'] = float(temp_match.group(1))
                
                light_match = re.search(r'채광:(\d+\.?\d*)\s*%', message)
                if light_match:
                    sensor_data['light'] = float(light_match.group(1))
                
                # 토양습도: 공백 포함/미포함 모두 지원 (토양습도: 또는 토양 습도:)
                soil_match = re.search(r'토양\s*습도:(\d+\.?\d*)\s*%', message)
                if soil_match:
                    sensor_data['soil_moisture'] = float(soil_match.group(1))
                
                # 새 형식은 4개 센서가 모두 있어야 완전한 데이터로 간주
                # 하나라도 없으면 해당 로그는 스킵 (다음 else 블록의 기존 형식도 시도하지 않음)
                if not all([sensor_data['humidity'] is not None,
                           sensor_data['temperature'] is not None,
                           sensor_data['light'] is not None,
                           sensor_data['soil_moisture'] is not None]):
                    continue  # 다음 로그로 이동
            # 형식 2: 실시간 데이터 저장 형식 (공백 없이 연결된 형식): "온도: 21.8°C습도: 26.7%채광: 1.3%토양 습도: 0.1%"
            elif '온도:' in message and '습도:' in message and ('채광:' in message or '토양' in message):
                # 실시간 데이터 형식: 온도:값°C습도:값%채광:값%토양 습도:값%
                # 온도 추출 (°C 또는 ℃ 모두 지원)
                temp_match = re.search(r'온도:\s*(\d+\.?\d*)\s*[℃°C]', message)
                if temp_match:
                    sensor_data['temperature'] = float(temp_match.group(1))
                
                # 습도 추출
                humidity_match = re.search(r'습도:\s*(\d+\.?\d*)\s*%', message)
                if humidity_match:
                    sensor_data['humidity'] = float(humidity_match.group(1))
                
                # 채광 추출
                light_match = re.search(r'채광:\s*(\d+\.?\d*)\s*%', message)
                if light_match:
                    sensor_data['light'] = float(light_match.group(1))
                
                # 토양 습도 추출 (공백 포함/미포함 모두 지원)
                soil_match = re.search(r'토양\s*습도:\s*(\d+\.?\d*)\s*%', message)
                if soil_match:
                    sensor_data['soil_moisture'] = float(soil_match.group(1))
                
                # 4개 센서가 모두 있어야 완전한 데이터로 간주
                if not all([sensor_data['humidity'] is not None,
                           sensor_data['temperature'] is not None,
                           sensor_data['light'] is not None,
                           sensor_data['soil_moisture'] is not None]):
                    continue  # 다음 로그로 이동
            else:
                # 기존 형식 지원 (하위 호환성): "습도 값 낮음 (45.5%)", "습도 정상 복귀 (낮음 → 정상, 현재값: 55.2%)"
                humidity_match = re.search(r'습도[^()]*\([^)]*?(\d+\.?\d*)\s*%', message)
                if humidity_match:
                    sensor_data['humidity'] = float(humidity_match.group(1))
                
                temp_match = re.search(r'온도[^()]*?\([^)]*?(\d+\.?\d*)\s*℃', message)
                if temp_match:
                    sensor_data['temperature'] = float(temp_match.group(1))
                
                light_match = re.search(r'채광[^()]*?\([^)]*?(\d+\.?\d*)\s*%', message)
                if light_match:
                    sensor_data['light'] = float(light_match.group(1))
                
                soil_match = re.search(r'토양습도[^()]*?\([^)]*?(\d+\.?\d*)\s*%', message)
                if soil_match:
                    sensor_data['soil_moisture'] = float(soil_match.group(1))
            
            # 센서 데이터가 하나라도 있으면 추가
            if any([sensor_data['humidity'] is not None, sensor_data['temperature'] is not None, 
                   sensor_data['light'] is not None, sensor_data['soil_moisture'] is not None]):
                sensor_data_list.append(sensor_data)
        
        return sensor_data_list
    
    def add_logs_from_json(self, logs_json: str) -> bool:
        """JSON 형식의 로그 추가"""
        try:
            logs = json.loads(logs_json)
            
            if not self.use_db:
                # 메모리 모드: 리스트에 추가
                for log in logs:
                    log_entry = {
                        'timestamp': log.get('timestamp', datetime.now().strftime("%H:%M:%S")),
                        'message': log.get('message', ''),
                        'date': log.get('date', datetime.now().strftime("%Y-%m-%d")),
                        'log_type': log.get('log_type', 'info')
                    }
                    self.logs_list.append(log_entry)
                
                # 최대 1000개까지만 유지
                if len(self.logs_list) > 1000:
                    self.logs_list = self.logs_list[-1000:]
                
                return True
            
            # DB 모드
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for log in logs:
                timestamp = log.get('timestamp', datetime.now().strftime("%H:%M:%S"))
                message = log.get('message', '')
                date = log.get('date', datetime.now().strftime("%Y-%m-%d"))
                log_type = log.get('log_type', 'info')
                
                cursor.execute('''
                    INSERT INTO logs (timestamp, message, date, log_type)
                    VALUES (?, ?, ?, ?)
                ''', (timestamp, message, date, log_type))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"JSON 로그 추가 오류: {e}")
            return False

