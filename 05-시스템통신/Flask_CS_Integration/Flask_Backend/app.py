from flask import Flask, render_template, request, redirect, session, jsonify
from functools import wraps
import json
import os
import datetime
import time

app = Flask(__name__)
app.secret_key = "secret123"

# ============================================================
#  사용자 계정
# ============================================================
users = [
    {"id": 1, "userid": "admin", "password": "1234", "role": "admin", "name": "관리자"},
    {"id": 2, "userid": "user", "password": "1111", "role": "user", "name": "일반사용자"}
]

# ============================================================
#  창고
# ============================================================
warehouses = [
    {"id": 1, "name": "냉동창고", "type": "냉동", "capacity": 10, "current_items": [], "temperature": 0.0, "mode": "freeze"},
    {"id": 2, "name": "냉장창고", "type": "냉장", "capacity": 15, "current_items": [], "temperature": 0.0, "mode": "cold"},
    {"id": 3, "name": "일반창고", "type": "일반", "capacity": 20, "current_items": [], "temperature": 0.0, "mode": "normal"}
]

# ============================================================
# 물품 및 요청
# ============================================================
items = []
reservations = []
takeouts = []

next_item_id = 1
next_reservation_id = 1
next_takeout_id = 1

# ============================================================
#  PLC/C# 연동용 상태
# ============================================================

sensor_data = {
    "temp": 0.0,
    "hum": 0.0,
    "vib": 0.0,
    "pres": 0.0,
    "DI0": False,
    "DI1": False,
    "DI2": False,
    "DI3": False
}


control_command = {
    "warehouse_power": "off",
    "mode": "normal",
    "emergency_power": False,
    "sprinkler": False
}

# ============================================================
#  정상화 및 이벤트 상태 (C# 연동용)
# ============================================================
normalize_requested = False

event_flags = {
    "fire_event": False,
    "vib_event": False,
    "pressure_event": False,
    "blackout_event": False,
}

door_event = {
    "normal": False,
    "cold": False,
    "freeze": False,
}

# ============================================================
# 로그인 데코레이터
# ============================================================
emergency_power_start_time = 0
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "role" not in session:
                return redirect("/")
            if role and session["role"] != role:
                return redirect("/")
            return f(*args, **kwargs)
        return decorated
    return decorator

# ============================================================
#  로그인 / 로그아웃 / 대시보드
# ============================================================
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userid = request.form.get("userid")
        password = request.form.get("password")

        user = next((u for u in users if u["userid"] == userid and u["password"] == password), None)
        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]
            
            if user["role"] == "admin":
                return redirect("/admin/dashboard")
            else:
                return redirect("/user/dashboard")
        else:
            return render_template("login.html", error="아이디 또는 비밀번호가 잘못되었습니다.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/user")
def user_redirect():
    return redirect("/user/dashboard")

@app.route("/user/dashboard")
@login_required("user")
def user_dashboard():
    uid = session["user_id"]
    return render_template("user_dashboard.html", 
                           my_items=get_my_items(uid), 
                           logs=get_user_logs(uid))

# ============================================================
# ============================================================
#  Helper Functions
# ============================================================
# ============================================================
#  Helper Functions
# ============================================================
def get_my_items(uid):
    my_list = []
    for i in items:
        if i["owner_id"] == uid:
            # 창고 이름 찾기
            w = next((w for w in warehouses if w["type"] == i["warehouse_type"]), None)
            i_copy = i.copy()
            i_copy["warehouse_name"] = w["name"] if w else "알 수 없음"
            
            # 남은 기간 계산
            if i.get("end_time"):
                try:
                    end_dt = datetime.datetime.strptime(i["end_time"], "%Y-%m-%d %H:%M")
                    now = datetime.datetime.now()
                    diff = end_dt - now
                    i_copy["remaining_days"] = diff.days if diff.days >= 0 else 0
                except:
                    i_copy["remaining_days"] = None
            else:
                i_copy["remaining_days"] = None
                
            my_list.append(i_copy)
    return my_list

def get_warehouse_data():
    # 창고 데이터에 소유자 이름 추가하여 가공
    display_warehouses = []
    for w in warehouses:
        w_copy = w.copy()
        
        # 용량 퍼센트 계산
        current_count = len(w["current_items"])
        capacity = w["capacity"]
        w_copy["percent"] = int((current_count / capacity) * 100) if capacity > 0 else 0
        
        items_list = []
        for item in w["current_items"]:
            owner = next((u for u in users if u["id"] == item["owner_id"]), None)
            items_list.append({
                "name": item["name"],
                "owner_name": owner["name"] if owner else "알 수 없음"
            })
        w_copy["items_list"] = items_list
        display_warehouses.append(w_copy)
    return display_warehouses

def get_user_logs(uid):
    # 메모리 상의 로그 (예약/반출 목록)
    user_logs = []
    for r in reservations:
        if r["user_id"] == uid:
            user_logs.append({
                "type": "reservation",
                "item": r["item_name"],
                "status": r["status"],
                "time": "N/A"
            })
    for t in takeouts:
        if t["user_id"] == uid:
            user_logs.append({
                "type": "takeout",
                "item": t["item_name"],
                "status": t["status"],
                "time": "N/A"
            })
    return user_logs

def get_file_logs_for_user(uid):
    # 파일(logs.txt)에서 해당 사용자의 로그만 필터링
    user_name = next((u["name"] for u in users if u["id"] == uid), None)
    if not user_name:
        return []
    
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if user_name in line: # 간단히 이름으로 필터링
                    logs.append(line.strip())
    return list(reversed(logs)) # 최신순

# ============================================================
# 사용자 → 꺼내기 페이지
# ============================================================
@app.route("/user/takeout")
@login_required("user")
def user_takeout():
    uid = session["user_id"]
    # 출고 가능한 물품만 필터링 (이미 요청중이거나 출고된 물품 제외)
    my_items = [i for i in get_my_items(uid) if i.get("can_takeout", True)]
    
    pending_requests = [t for t in takeouts if t["user_id"] == uid and t["status"] == "pending"]
    for r in pending_requests:
        item = next((i for i in items if i["id"] == r["item_id"]), None)
        if item:
            w = next((w for w in warehouses if w["type"] == item["warehouse_type"]), None)
            r["warehouse_name"] = w["name"] if w else "알 수 없음"
        else:
            r["warehouse_name"] = "알 수 없음"
    file_logs = get_file_logs_for_user(uid)
    
    return render_template("user_takeout.html", my_items=my_items, pending_requests=pending_requests, logs=file_logs)

@app.route("/user/reserve", methods=["GET","POST"])
@login_required("user")
def user_reserve():
    global next_reservation_id
    uid = session["user_id"]

    if request.method == "POST":
        data = request.get_json(force=True) if request.is_json else request.form
        item_name = data.get("item")
        wtype = data.get("type")

        if not item_name or not wtype:
            return jsonify({"error": "물품 또는 창고 누락"}), 400

        # 창고 용량 확인
        target_warehouse = next((w for w in warehouses if w["type"] == wtype), None)
        if target_warehouse:
            if len(target_warehouse["current_items"]) >= target_warehouse["capacity"]:
                return jsonify({"error": f"{wtype}창고가 가득 찼습니다! (용량 초과)"}), 400

        reservations.append({
            "id": next_reservation_id,
            "item_name": item_name,
            "user_id": uid,
            "warehouse_type": wtype,
            "start_time": data.get("start_time", ""),
            "end_time": data.get("end_time", ""),
            "status": "pending"
        })
        next_reservation_id += 1
        
        # 로그 파일에 기록 (요청 시점)
        user = next((u for u in users if u["id"] == uid), None)
        start = data.get("start_time", "").replace("T", " ")
        end = data.get("end_time", "").replace("T", " ")
        write_log(f"예약 요청: {user['name']} - {item_name} ({wtype}, {start} ~ {end})", "info")

        return jsonify({"success": True}) if request.is_json else redirect("/user/reserve")

    # GET 요청 시 데이터 전달
    pending_requests = [r for r in reservations if r["user_id"] == uid and r["status"] == "pending"]
    file_logs = get_file_logs_for_user(uid)
    
    return render_template("user_reserve.html", pending_requests=pending_requests, logs=file_logs)

@app.route("/api/user_status")
@login_required("user")
def api_user_status():
    uid = session["user_id"]
    return jsonify({
        "my_items": get_my_items(uid),
        "warehouses": get_warehouse_data(),
        "logs": get_user_logs(uid)
    })

# ============================================================
# 사용자 → 꺼내기 요청 API
# ============================================================
@app.route("/api/takeouts", methods=["GET", "POST"])
@login_required("user")
def api_takeouts():
    global next_takeout_id
    uid = session["user_id"]

    if request.method == "GET":
        # 사용자의 반출 요청 목록 반환
        user_takeouts = [t for t in takeouts if t["user_id"] == uid]
        return jsonify(user_takeouts)

    # POST 요청 처리
    data = request.get_json(force=True)
    item_id = data.get("item_id")

    item_obj = next((i for i in items if i["id"] == item_id and i["owner_id"] == uid), None)
    if not item_obj:
        return jsonify({"error": "권한 없음"}), 400

    item_obj["can_takeout"] = False

    takeouts.append({
        "id": next_takeout_id,
        "item_id": item_id,
        "user_id": uid,
        "status": "pending",
        "item_name": item_obj["name"]
    })
    next_takeout_id += 1

    # 로그 파일에 기록 (요청 시점)
    user = next((u for u in users if u["id"] == uid), None)
    write_log(f"반출 요청: {user['name']} - {item_obj['name']}", "info")

    return jsonify({"success": True, "item_name": item_obj["name"]})

# ============================================================
# 관리자 화면
# ============================================================
@app.route("/admin/dashboard")
@login_required("admin")
def admin_dashboard():
    wdata = get_warehouse_data()
    pending_requests = [r for r in reservations if r["status"] == "pending"] + \
                       [t for t in takeouts if t["status"] == "pending"]
    for r in pending_requests:
        r["user"] = next(u["userid"] for u in users if u["id"] == r["user_id"])
    return render_template("admin_dashboard.html", warehouses=wdata, pending_requests=pending_requests)

@app.route("/admin/warehouses")
@login_required("admin")
def admin_warehouses():
    # 헬퍼 함수 사용하여 데이터 가져오기 (percent 포함됨)
    display_warehouses = get_warehouse_data()
    return render_template("admin_warehouses.html", warehouses=display_warehouses)

@app.route("/admin/reservations")
@login_required("admin")
def admin_reservations():
    all_requests = []

    for r in reservations:
        user = next((u for u in users if u["id"] == r["user_id"]), None)
        all_requests.append({
            "id": r["id"],
            "type": "reservation",
            "item_name": r["item_name"],
            "warehouse_type": r.get("warehouse_type", ""),
            "start_time": r.get("start_time", ""),
            "end_time": r.get("end_time", ""),
            "user": user["userid"] if user else "Unknown",
            "status": r["status"]
        })

    for t in takeouts:
        user = next((u for u in users if u["id"] == t["user_id"]), None)
        item = next((i for i in items if i["id"] == t["item_id"]), None)
        w_name = ""
        if item:
             w = next((w for w in warehouses if w["type"] == item["warehouse_type"]), None)
             w_name = w["name"] if w else ""

        all_requests.append({
            "id": t["id"],
            "type": "takeout",
            "item_name": t["item_name"],
            "item_id": t.get("item_id", ""),
            "warehouse_type": w_name,
            "start_time": "-",
            "end_time": "-",
            "user": user["userid"] if user else "Unknown",
            "status": t["status"]
        })

    return render_template("admin_reservations.html", requests=all_requests)

# ============================================================
# 예약 승인/거부
# ============================================================
@app.route("/api/reservations/<int:id>", methods=["PATCH"])
@login_required("admin")
def patch_reservation(id):
    global next_item_id
    data = request.get_json(force=True)
    r = next((r for r in reservations if r["id"] == id), None)
    if not r:
        return jsonify({"error": "요청 없음"}), 404

    r["status"] = data["status"]

    if data["status"] == "approved":
        w = next((w for w in warehouses if w["type"] == r["warehouse_type"]), None)
        if not w:
            return jsonify({"error": "창고 없음"}), 404
        if len(w["current_items"]) >= w["capacity"]:
            return jsonify({"error": "용량 부족"}), 400

        item_obj = {"id": next_item_id, "name": r["item_name"],
                    "owner_id": r["user_id"], "warehouse_type": r["warehouse_type"],
                    "can_takeout": True,
                    "start_time": r.get("start_time"),
                    "end_time": r.get("end_time")}
        next_item_id += 1
        items.append(item_obj)
        w["current_items"].append(item_obj)
        save_items()

    return jsonify(r)

# ============================================================
# 꺼내기 승인/거부
# ============================================================
@app.route("/api/takeouts/<int:id>", methods=["PATCH"])
@login_required("admin")
def patch_takeout(id):
    data = request.get_json(force=True)
    t = next((t for t in takeouts if t["id"] == id), None)
    if not t:
        return jsonify({"error": "요청 없음"}), 404

    t["status"] = data["status"]

    if data["status"] == "approved":
        item_obj = next((i for i in items if i["id"] == t["item_id"]), None)
        if item_obj:
            w = next((w for w in warehouses if item_obj in w["current_items"]), None)
            if w:
                w["current_items"].remove(item_obj)
            item_obj["can_takeout"] = False
            item_obj["warehouse_type"] = "출고됨"
            save_items()

    return jsonify(t)

# ============================================================
# 통합 요청 API (대시보드용)
# ============================================================


ITEMS_FILE = "items.json"

def save_items():
    try:
        with open(ITEMS_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"물품 저장 실패: {e}")

def load_items():
    global next_item_id
    try:
        if not os.path.exists(ITEMS_FILE):
            return

        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            loaded_items = json.load(f)
        
        if not loaded_items:
            return

        # items 리스트 업데이트
        items.clear()
        items.extend(loaded_items)

        # next_item_id 업데이트
        max_id = 0
        for item in items:
            if item["id"] > max_id:
                max_id = item["id"]
        next_item_id = max_id + 1

        # 창고에 물품 배치
        for w in warehouses:
            w["current_items"] = [] # 초기화
        
        for item in items:
            if item.get("can_takeout", False): # 출고 가능 = 창고에 있음
                w = next((w for w in warehouses if w["type"] == item["warehouse_type"]), None)
                if w:
                    w["current_items"].append(item)
                    
        print(f"물품 {len(items)}개 로드 완료")

    except Exception as e:
        print(f"물품 로드 실패: {e}")

# 앱 시작 시 물품 로드
load_items()

@app.route("/api/requests", methods=["GET"])
@login_required("admin")
def get_all_requests():
    all_requests = []
    
    for r in reservations:
        user = next((u for u in users if u["id"] == r["user_id"]), None)
        all_requests.append({
            "id": r["id"],
            "type": "reservation",
            "item_name": r["item_name"],
            "item": r["item_name"],
            "user": user["userid"] if user else "Unknown",
            "user_id": r["user_id"],
            "status": r["status"]
        })
    
    for t in takeouts:
        user = next((u for u in users if u["id"] == t["user_id"]), None)
        all_requests.append({
            "id": t["id"],
            "type": "takeout",
            "item_name": t["item_name"],
            "item": t["item_name"],
            "user": user["userid"] if user else "Unknown",
            "user_id": t["user_id"],
            "status": t["status"]
        })
    
    # ID 역순 정렬 (최신순)
    all_requests.sort(key=lambda x: x["id"], reverse=True)
    
    return jsonify(all_requests)



LOG_FILE = "logs.txt"

def write_log(msg, type="info"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{type.upper()}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"로그 저장 실패: {e}")

@app.route("/api/logs", methods=["GET"])
@login_required("admin")
def get_logs():
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify([])
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # 최근 로그가 위로 오도록 역순 정렬
        return jsonify([line.strip() for line in reversed(lines)])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/requests/<int:id>", methods=["PATCH"])
@login_required("admin")
def patch_request(id):
    global next_item_id
    data = request.get_json(force=True)
    req_type = data.get("type")
    
    if req_type == "reservation":
        r = next((r for r in reservations if r["id"] == id), None)
        if not r:
            return jsonify({"error": "요청 없음"}), 404
        
        r["status"] = data["status"]
        
        if data["status"] == "approved":
            w = next((w for w in warehouses if w["type"] == r["warehouse_type"]), None)
            if not w:
                return jsonify({"error": "창고 없음"}), 404
            if len(w["current_items"]) >= w["capacity"]:
                return jsonify({"error": "용량 부족"}), 400
            
            item_obj = {"id": next_item_id, "name": r["item_name"],
                        "owner_id": r["user_id"], "warehouse_type": r["warehouse_type"],
                        "can_takeout": True}
            next_item_id += 1
            items.append(item_obj)
            w["current_items"].append(item_obj)
            save_items() # 저장
            
            user = next((u for u in users if u["id"] == r["user_id"]), None)
            write_log(f"예약 승인: {user['name']} - {r['item_name']} ({r['warehouse_type']})", "success")
        elif data["status"] == "rejected":
            user = next((u for u in users if u["id"] == r["user_id"]), None)
            write_log(f"예약 거부: {user['name']} - {r['item_name']}", "alert")

        user = next((u for u in users if u["id"] == r["user_id"]), None)
        return jsonify({
            "id": r["id"],
            "item_name": r["item_name"],
            "user": user["userid"] if user else "Unknown",
            "status": r["status"]
        })
    
    elif req_type == "takeout":
        t = next((t for t in takeouts if t["id"] == id), None)
        if not t:
            return jsonify({"error": "요청 없음"}), 404
        
        if data["status"] == "approved":
            item_obj = next((i for i in items if i["id"] == t["item_id"]), None)
            if not item_obj:
                 write_log(f"출고 실패 (물품 없음): ID {t['item_id']}", "error")
                 return jsonify({"error": "물품을 찾을 수 없습니다."}), 404

            w = next((w for w in warehouses if item_obj in w["current_items"]), None)
            if w:
                w["current_items"].remove(item_obj)
                item_obj["can_takeout"] = False
                item_obj["warehouse_type"] = "출고됨"
                t["status"] = "approved" # 성공 시에만 상태 변경
                save_items() # 저장
                
                user = next((u for u in users if u["id"] == t["user_id"]), None)
                write_log(f"출고 승인: {user['name']} - {t['item_name']}", "success")
            else:
                write_log(f"출고 실패 (창고에 없음): {t['item_name']}", "error")
                return jsonify({"error": "창고에서 물품을 찾을 수 없습니다."}), 404
        
        elif data["status"] == "rejected":
            t["status"] = "rejected"
            # 거부 시 다시 꺼내기 가능하도록 복구해야 하나? 
            # 아니오, 요청만 거부된 것이므로 물품 상태는 그대로 (can_takeout=False로 잠겨있던걸 풀어줘야 함)
            item_obj = next((i for i in items if i["id"] == t["item_id"]), None)
            if item_obj:
                item_obj["can_takeout"] = True # 다시 요청 가능하게 복구
            
            user = next((u for u in users if u["id"] == t["user_id"]), None)
            write_log(f"출고 거부: {user['name']} - {t['item_name']}", "alert")
        
        user = next((u for u in users if u["id"] == t["user_id"]), None)
        return jsonify({
            "id": t["id"],
            "item_name": t["item_name"],
            "user": user["userid"] if user else "Unknown",
            "status": t["status"]
        })
    
    return jsonify({"error": "잘못된 요청 타입"}), 400

# ============================================================
# PLC/C# 연동 API
# ============================================================

# 1) C# → Flask : 센서 데이터 입력
@app.route("/sensor", methods=["POST"])
def receive_sensor():
    global sensor_data
    data = request.get_json(force=True)
    print("📡 센서 데이터 수신:", data)

    for key in ["temp", "hum", "vib", "pres", "DI0", "DI1", "DI2", "DI3", 
                "temp_normal", "hum_normal", "temp_cold", "hum_cold", "temp_freeze", "hum_freeze"]:
        if key in data:
            sensor_data[key] = data[key]
    
    # 비상 전력 가동 시 10초간 전력(pres) 400으로 고정
    if control_command["emergency_power"]:
        if time.time() - emergency_power_start_time <= 10:
            sensor_data["pres"] = 400.0
    
    # 각 창고별 온도/습도 업데이트
    # C#에서 개별 값을 보내주므로 그것을 사용
    for w in warehouses:
        if w["type"] == "일반" and "temp_normal" in data:
            w["temperature"] = data["temp_normal"]
            w["humidity"] = data.get("hum_normal", 0)
        elif w["type"] == "냉장" and "temp_cold" in data:
            w["temperature"] = data["temp_cold"]
            w["humidity"] = data.get("hum_cold", 0)
        elif w["type"] == "냉동" and "temp_freeze" in data:
            w["temperature"] = data["temp_freeze"]
            w["humidity"] = data.get("hum_freeze", 0)
        # 만약 개별 데이터가 없다면 기존 방식(전체 temp) 유지 (호환성)
        elif "temp" in data and "temp_normal" not in data:
             w["temperature"] = data["temp"]

    return jsonify({"status": "ok", "sensor_data": sensor_data})

# 2) Flask → 관리자가 설정하는 제어 명령
@app.route("/api/control", methods=["GET", "POST"])
@login_required("admin")
def api_control():
    global control_command, emergency_power_start_time

    if request.method == "POST":
        data = request.get_json(force=True)
        print("⚙️ 관리자 제어 명령:", data)

        if "warehouse_power" in data:
            control_command["warehouse_power"] = data["warehouse_power"]
        if "mode" in data:
            control_command["mode"] = data["mode"]
        if "emergency_power" in data:
            new_state = bool(data["emergency_power"])
            if new_state and not control_command["emergency_power"]:
                emergency_power_start_time = time.time()
            control_command["emergency_power"] = new_state
            # 비상 전원 켜짐 -> 정전 이벤트 해제
            if control_command["emergency_power"] and event_flags.get("blackout_event"):
                event_flags["blackout_event"] = False
                print("[FLASK] 비상 전원 가동으로 정전 이벤트 해제")

        if "sprinkler" in data:
            control_command["sprinkler"] = bool(data["sprinkler"])
            # 스프링클러 켜짐 -> 화재 이벤트 해제
            if control_command["sprinkler"] and event_flags.get("fire_event"):
                event_flags["fire_event"] = False
                print("[FLASK] 스프링클러 가동으로 화재 이벤트 해제")
                # 정상화 로직 트리거 (모든 창고)
                normalize_requested = True
                print("[FLASK] 스프링클러 가동으로 전체 창고 정상화 요청")

        return jsonify({"status": "updated", "control": control_command})

    return jsonify(control_command)

# 3) C# → Flask : 제어 명령 요청
@app.route("/get_control", methods=["GET"])
def get_control():
    return jsonify(control_command)

# 4) 관리자 → 센서 데이터 조회
@app.route("/api/sensor_data", methods=["GET"])
@login_required("admin")
def api_sensor_data():
    # 현재 창고 데이터 가져오기 (적재율 포함)
    w_data = get_warehouse_data()
    
    # 응답 데이터 구성 (기존 센서 데이터 + 적재율)
    response_data = sensor_data.copy()
    
    for w in w_data:
        if w["type"] == "냉동":
            response_data["load_freezer"] = w["percent"]
        elif w["type"] == "냉장":
            response_data["load_fridge"] = w["percent"]
        elif w["type"] == "일반":
            response_data["load_normal"] = w["percent"]
            
    return jsonify(response_data)

# ============================================================
#  추가된 C# 연동 API (MAIN_flask 포팅)
# ============================================================

# 5) 정상화 요청 (관리자 → Flask)
@app.route("/api/normalize", methods=["POST"])
@login_required("admin")
def api_normalize():
    global normalize_requested, door_event

    data = request.get_json(force=True) or {}
    # UI sends 'warehouse', but logic might expect 'mode'. Handle both.
    mode = data.get("mode") or data.get("warehouse")

    normalize_requested = True

    # 해당 모드 문 닫기
    # UI sends 'freezer', 'fridge', 'normal'
    # door_event keys are 'freeze', 'cold', 'normal'
    target_key = None
    if mode == "freezer": target_key = "freeze"
    elif mode == "fridge": target_key = "cold"
    elif mode == "normal": target_key = "normal"
    elif mode == "freeze": target_key = "freeze"
    elif mode == "cold": target_key = "cold"

    if target_key and target_key in door_event:
        door_event[target_key] = False
        print(f"[FLASK] 정상화 요청으로 {target_key} 창고 문 이벤트 해제")

    # ★ 추가: 정상화 시 비상전원/스프링클러 및 모든 이벤트 해제
    control_command["emergency_power"] = False
    control_command["sprinkler"] = False
    
    for k in event_flags.keys():
        event_flags[k] = False

    print(f"[FLASK] 정상화 요청 수신: mode={mode} -> key={target_key} (모든 제어/이벤트 리셋)")
    return jsonify({"status": "ok", "message": "정상화 요청이 전송되었습니다."})

# 6) 정상화 상태 조회 (C# → Flask)
@app.route("/api/normalize/status", methods=["GET"])
def api_normalize_status():
    global normalize_requested
    if normalize_requested:
        normalize_requested = False
        return jsonify({"normalize": True})
    else:
        return jsonify({"normalize": False})

# 7) 이벤트 상태 조회 (C# → Flask)
firewall_active_flag = False

@app.route("/api/events/status", methods=["GET"])
def api_events_status():
    global firewall_active_flag
    
    response = event_flags.copy()
    response["firewall_active"] = firewall_active_flag
    return jsonify(response)

@app.route("/api/firewall", methods=["POST"])
# @login_required("admin") # C#에서도 호출 가능하도록 잠시 주석 처리 또는 예외 처리 필요
def api_firewall():
    global firewall_active_flag, event_flags, control_command, door_event
    
    data = request.get_json() or {}
    active = data.get("active", True) # 기본값 True
    
    firewall_active_flag = active
    
    if active:
        # 방화벽 가동 시: 모든 이벤트 해제 & 제어 리셋
        for k in event_flags.keys():
            event_flags[k] = False
            
        control_command["emergency_power"] = False
        control_command["sprinkler"] = False
        
        # 모든 문 닫기
        for k in door_event.keys():
            door_event[k] = False
            
        print("[FLASK] 방화벽 가동 (ON)")
        return jsonify({"status": "ok", "message": "방화벽이 가동되었습니다."})
    else:
        print("[FLASK] 방화벽 해제 (OFF)")
        return jsonify({"status": "ok", "message": "방화벽이 해제되었습니다."})

# 8) 이벤트 시뮬레이션 (관리자 → Flask)
@app.route("/api/events/simulate", methods=["POST"])
@login_required("admin")
def api_events_simulate():
    global event_flags
    data = request.get_json(force=True) or {}
    name = data.get("event")
    active = data.get("active")

    if name not in event_flags:
        return jsonify({"status": "error", "message": "invalid event name"}), 400

    event_flags[name] = bool(active)
    print(f"[FLASK] 이벤트 시뮬레이션: {name} -> {event_flags[name]}")
    return jsonify({"status": "ok", "event": name, "active": event_flags[name]})

# 9) 모드 상태 조회 (C# → Flask)
@app.route("/api/mode/status", methods=["GET"])
def api_mode_status():
    # control_command["mode"] 값을 반환 (normal/cold/freeze)
    return jsonify({"mode": control_command["mode"]})

# 10) 문 열림 이벤트 조회 (C# → Flask)
@app.route("/event/get", methods=["GET"])
def event_get():
    return jsonify(door_event)

# 11) 문 열림 설정 (관리자 → Flask)
@app.route("/event/set", methods=["POST"])
@login_required("admin")
def event_set():
    global door_event
    data = request.get_json(force=True) or {}
    print("[FLASK] 문 이벤트 설정 요청:", data)

    for key in door_event.keys():
        if key in data:
            door_event[key] = bool(data[key])

    return jsonify({"status": "updated", "event": door_event})

# ============================================================
# 실행
# ============================================================
if __name__ == "__main__":
    import os
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug_mode)
    # Server restart triggered for data sync
