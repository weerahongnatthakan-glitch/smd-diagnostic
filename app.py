from __future__ import annotations

from flask import Flask, request, render_template_string, Response
import json
import csv
import io
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

DATA_DIR = Path("DATA")
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"


def load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(history):
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def add_case(record):
    history = load_history()
    history.append(record)
    save_history(history)


def confidence_color(confidence: int) -> str:
    if confidence >= 80:
        return "#15803d"  # เขียว
    if confidence >= 60:
        return "#ca8a04"  # เหลือง
    return "#b91c1c"      # แดง


def count_titles(history):
    counts = {}
    for item in history:
        title = item.get("title", "ไม่ระบุ")
        counts[title] = counts.get(title, 0) + 1
    return counts


def to_bool(value: str) -> bool:
    return value == "y"


HTML = """
<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SMD v0.5</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f3f4f6;
      margin: 0;
      padding: 0;
      color: #222;
    }
    .container {
      max-width: 860px;
      margin: 24px auto;
      padding: 16px;
    }
    .card {
      background: white;
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 6px 18px rgba(0,0,0,0.08);
      margin-bottom: 20px;
    }
    .topbar {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }
    .btn {
      background: #111827;
      color: white;
      border: none;
      padding: 12px 18px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 15px;
      text-decoration: none;
      display: inline-block;
    }
    .btn:hover {
      opacity: 0.9;
    }
    h1, h2, h3 {
      margin-top: 0;
    }
    .muted {
      color: #666;
      font-size: 14px;
    }
    .question {
      margin: 18px 0;
      padding: 14px;
      background: #f9fafb;
      border-radius: 12px;
    }
    label {
      display: block;
      margin: 6px 0;
      cursor: pointer;
    }
    button {
      background: #111827;
      color: white;
      border: none;
      padding: 12px 18px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 15px;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin-top: 14px;
    }
    .stat-box {
      background: #f9fafb;
      border-radius: 14px;
      padding: 16px;
      text-align: center;
    }
    .stat-box .num {
      font-size: 28px;
      font-weight: bold;
      margin-top: 6px;
    }
    .result-box {
      background: #f9fafb;
      border-left: 6px solid {{ result_color if result_color else '#111827' }};
      padding: 14px;
      border-radius: 10px;
      margin-top: 16px;
    }
    .tag {
      display: inline-block;
      background: #e5e7eb;
      padding: 6px 10px;
      border-radius: 999px;
      margin-right: 8px;
      margin-bottom: 8px;
      font-size: 13px;
    }
    ul {
      padding-left: 20px;
    }
    .footer {
      text-align: center;
      color: #777;
      font-size: 13px;
      margin-top: 20px;
    }
    .pill {
      display: inline-block;
      color: white;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 13px;
      margin-top: 8px;
    }
  </style>
</head>
<body>
  <div class="container">

    <div class="card">
      <h1>Smart Maintenance Diagnostic</h1>
      <div class="muted">SMD v0.5 • ผู้ช่วยวิเคราะห์อาการเสียของอาคาร</div>

      <div class="stats">
        <div class="stat-box">
          <div>เคสทั้งหมด</div>
          <div class="num">{{ total_cases }}</div>
        </div>
        <div class="stat-box">
          <div>แอร์ไม่เย็น</div>
          <div class="num">{{ not_cold_count }}</div>
        </div>
        <div class="stat-box">
          <div>แอร์ตัดบ่อย</div>
          <div class="num">{{ trip_count }}</div>
        </div>
        <div class="stat-box">
          <div>น้ำหยด</div>
          <div class="num">{{ leak_count }}</div>
        </div>
      </div>
    </div>

    <div class="topbar">
      <a class="btn" href="/">หน้าแรก</a>
      <a class="btn" href="/history">ประวัติเคส</a>
      <a class="btn" href="/export/csv">Export CSV</a>
    </div>

    <div class="card">
      <h2>เลือกอาการ</h2>

      <form method="post" action="/diagnose">
        <div class="question">
          <strong>หมวด:</strong>
          <label><input type="radio" name="category" value="ac" checked> แอร์</label>
        </div>

        <div class="question">
          <strong>อาการ:</strong>
          <label><input type="radio" name="symptom" value="not_cold" required> แอร์ไม่เย็น</label>
          <label><input type="radio" name="symptom" value="trip_often"> แอร์ตัดบ่อย</label>
          <label><input type="radio" name="symptom" value="water_leak"> น้ำหยด</label>
        </div>

        <div class="question">
          <strong>1) พัดลมคอยล์เย็นเป่าลมออกมาหรือไม่?</strong>
          <label><input type="radio" name="fan_running" value="y" required> ใช่</label>
          <label><input type="radio" name="fan_running" value="n"> ไม่ใช่</label>
        </div>

        <div class="question">
          <strong>2) แรงลมอ่อนผิดปกติหรือไม่?</strong>
          <label><input type="radio" name="weak_air" value="y" required> ใช่</label>
          <label><input type="radio" name="weak_air" value="n"> ไม่ใช่</label>
        </div>

        <div class="question">
          <strong>3) มีน้ำแข็งเกาะที่คอยล์เย็นหรือไม่?</strong>
          <label><input type="radio" name="coil_iced" value="y" required> ใช่</label>
          <label><input type="radio" name="coil_iced" value="n"> ไม่ใช่</label>
        </div>

        <div class="question">
          <strong>4) คอมเพรสเซอร์ด้านนอกทำงานหรือไม่?</strong>
          <label><input type="radio" name="compressor_running" value="y" required> ใช่</label>
          <label><input type="radio" name="compressor_running" value="n"> ไม่ใช่</label>
        </div>

        <button type="submit">วิเคราะห์</button>
      </form>
    </div>

    {% if result %}
    <div class="card">
      <h2>ผลวิเคราะห์</h2>
      <div class="result-box">
        <h3>{{ result.title }}</h3>
        <p><strong>ความมั่นใจ:</strong> {{ result.confidence }}%</p>
        <span class="pill" style="background: {{ result_color }};">
          ระดับความมั่นใจ
        </span>
      </div>

      <h3>สาเหตุที่เป็นไปได้</h3>
      <ul>
        {% for item in result.causes %}
          <li>{{ item }}</li>
        {% endfor %}
      </ul>

      <h3>จุดตรวจเช็คก่อน</h3>
      <ul>
        {% for item in result.checks %}
          <li>{{ item }}</li>
        {% endfor %}
      </ul>

      <h3>เครื่องมือที่ใช้</h3>
      {% for item in result.tools %}
        <span class="tag">{{ item }}</span>
      {% endfor %}

      {% if result.notes %}
      <h3>หมายเหตุ</h3>
      <ul>
        {% for item in result.notes %}
          <li>{{ item }}</li>
        {% endfor %}
      </ul>
      {% endif %}
    </div>
    {% endif %}

    <div class="footer">
      SMD Prototype • Built with Python + Flask
    </div>
  </div>
</body>
</html>
"""

HISTORY_HTML = """
<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SMD History</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f3f4f6;
      margin: 0;
      padding: 0;
      color: #222;
    }
    .container {
      max-width: 860px;
      margin: 24px auto;
      padding: 16px;
    }
    .card {
      background: white;
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 6px 18px rgba(0,0,0,0.08);
      margin-bottom: 20px;
    }
    .btn {
      background: #111827;
      color: white;
      border: none;
      padding: 12px 18px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 15px;
      text-decoration: none;
      display: inline-block;
      margin-bottom: 14px;
    }
    .history-item {
      background: #f9fafb;
      padding: 14px;
      border-radius: 12px;
      margin-bottom: 12px;
    }
    .muted {
      color: #666;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <a class="btn" href="/">กลับหน้าแรก</a>
      <a class="btn" href="/export/csv">Export CSV</a>
      <h1>ประวัติเคส</h1>

      {% if history %}
        {% for item in history|reverse %}
        <div class="history-item">
          <strong>{{ item.title }}</strong><br>
          <span class="muted">เวลา: {{ item.timestamp }}</span><br>
          <span class="muted">ความมั่นใจ: {{ item.confidence }}%</span>
          <ul>
            {% for c in item.causes %}
              <li>{{ c }}</li>
            {% endfor %}
          </ul>
        </div>
        {% endfor %}
      {% else %}
        <p>ยังไม่มีประวัติเคส</p>
      {% endif %}
    </div>
  </div>
</body>
</html>
"""


def diagnose_ac_not_cold(fan_running, weak_air, coil_iced, compressor_running):
    causes = []
    checks = []
    tools = ["แคลมป์มิเตอร์", "เทอร์โมมิเตอร์", "เกจน้ำยาแอร์"]
    notes = []
    confidence = 60

    if not fan_running:
        causes.append("พัดลมคอยล์เย็นไม่ทำงาน")
        checks.append("ตรวจมอเตอร์พัดลม / คาปาซิเตอร์ / ไฟเลี้ยงคอยล์เย็น")
        confidence = 85

    if weak_air:
        causes.append("ฟิลเตอร์อากาศตันหรือคอยล์เย็นสกปรก")
        checks.append("ล้างฟิลเตอร์และตรวจคอยล์เย็น")
        confidence = max(confidence, 80)

    if coil_iced:
        causes.append("คอยล์เย็นเป็นน้ำแข็งจากลมผ่านน้อยหรือน้ำยาแอร์ผิดปกติ")
        checks.append("ปิดเครื่องให้ละลายน้ำแข็งและตรวจระบบน้ำยา")
        confidence = max(confidence, 85)

    if not compressor_running:
        causes.append("คอมเพรสเซอร์หรือชุดคอยล์ร้อนไม่ทำงาน")
        checks.append("ตรวจไฟเข้าชุดภายนอก / คอนแทคเตอร์ / คาปาซิเตอร์ / เบรกเกอร์")
        confidence = max(confidence, 90)

    if not causes:
        causes.extend([
            "น้ำยาแอร์ต่ำ",
            "คอยล์ร้อนระบายความร้อนไม่ดี",
            "ระบบสกปรก",
        ])
        checks.extend([
            "ตรวจแรงดันน้ำยา",
            "ตรวจพัดลมคอยล์ร้อน",
            "เช็คอุณหภูมิลมเข้า-ออก",
        ])
        notes.append("กรณีนี้ควรตรวจวัดค่าหน้างานเพิ่มเพื่อยืนยัน")
        confidence = 70

    return {
        "title": "แอร์ไม่เย็น (วิเคราะห์เบื้องต้น)",
        "confidence": confidence,
        "causes": causes,
        "checks": checks,
        "tools": tools,
        "notes": notes,
    }


def diagnose_ac_trip_often(fan_running, weak_air, coil_iced, compressor_running):
    causes = ["คอมเพรสเซอร์โอเวอร์โหลด", "คอยล์ร้อนระบายความร้อนไม่ดี", "ระบบไฟฟ้ามีปัญหา"]
    checks = [
        "ตรวจคอยล์ร้อนและพัดลมคอยล์ร้อน",
        "วัดกระแสคอมเพรสเซอร์",
        "เช็คแรงดันไฟเข้าเครื่อง",
    ]
    tools = ["แคลมป์มิเตอร์", "มัลติมิเตอร์"]
    notes = ["กรณีตัดบ่อย ควรตรวจโหลดและระบบไฟร่วมด้วย"]
    return {
        "title": "แอร์ตัดบ่อย (วิเคราะห์เบื้องต้น)",
        "confidence": 75,
        "causes": causes,
        "checks": checks,
        "tools": tools,
        "notes": notes,
    }


def diagnose_ac_water_leak(fan_running, weak_air, coil_iced, compressor_running):
    causes = ["ท่อน้ำทิ้งตัน", "ถาดน้ำทิ้งสกปรก", "คอยล์เย็นเป็นน้ำแข็งแล้วละลาย"]
    checks = [
        "ตรวจท่อน้ำทิ้งและล้างท่อ",
        "ตรวจถาดน้ำทิ้ง",
        "ตรวจฟิลเตอร์และคอยล์เย็น",
    ]
    tools = ["เครื่องล้างแอร์", "ลวด/ปั๊มล้างท่อ"]
    notes = ["ถ้าน้ำหยดร่วมกับน้ำแข็งเกาะ ให้เช็คระบบลมและน้ำยา"]
    return {
        "title": "น้ำหยดจากแอร์ (วิเคราะห์เบื้องต้น)",
        "confidence": 80,
        "causes": causes,
        "checks": checks,
        "tools": tools,
        "notes": notes,
    }


@app.route("/", methods=["GET"])
def home():
    history = load_history()
    counts = count_titles(history)

    return render_template_string(
        HTML,
        result=None,
        result_color=None,
        total_cases=len(history),
        not_cold_count=counts.get("แอร์ไม่เย็น (วิเคราะห์เบื้องต้น)", 0),
        trip_count=counts.get("แอร์ตัดบ่อย (วิเคราะห์เบื้องต้น)", 0),
        leak_count=counts.get("น้ำหยดจากแอร์ (วิเคราะห์เบื้องต้น)", 0),
    )


@app.route("/diagnose", methods=["POST"])
def diagnose():
    symptom = request.form["symptom"]

    fan_running = to_bool(request.form["fan_running"])
    weak_air = to_bool(request.form["weak_air"])
    coil_iced = to_bool(request.form["coil_iced"])
    compressor_running = to_bool(request.form["compressor_running"])

    if symptom == "not_cold":
        result = diagnose_ac_not_cold(fan_running, weak_air, coil_iced, compressor_running)
    elif symptom == "trip_often":
        result = diagnose_ac_trip_often(fan_running, weak_air, coil_iced, compressor_running)
    elif symptom == "water_leak":
        result = diagnose_ac_water_leak(fan_running, weak_air, coil_iced, compressor_running)
    else:
        result = {
            "title": "ยังไม่รองรับอาการนี้",
            "confidence": 0,
            "causes": ["ไม่มีข้อมูล"],
            "checks": [],
            "tools": [],
            "notes": [],
        }

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": result["title"],
        "confidence": result["confidence"],
        "causes": result["causes"],
    }
    add_case(record)

    history = load_history()
    counts = count_titles(history)

    return render_template_string(
        HTML,
        result=result,
        result_color=confidence_color(result["confidence"]),
        total_cases=len(history),
        not_cold_count=counts.get("แอร์ไม่เย็น (วิเคราะห์เบื้องต้น)", 0),
        trip_count=counts.get("แอร์ตัดบ่อย (วิเคราะห์เบื้องต้น)", 0),
        leak_count=counts.get("น้ำหยดจากแอร์ (วิเคราะห์เบื้องต้น)", 0),
    )


@app.route("/history", methods=["GET"])
def history():
    return render_template_string(HISTORY_HTML, history=load_history())


@app.route("/export/csv", methods=["GET"])
def export_csv():
    history = load_history()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "title", "confidence", "causes"])

    for item in history:
        writer.writerow([
            item.get("timestamp", ""),
            item.get("title", ""),
            item.get("confidence", ""),
            " | ".join(item.get("causes", [])),
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=smd_history.csv"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
อันนี้อัปไหม