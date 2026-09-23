import json, sqlite3
from datetime import datetime, timezone

# 列表摘要与按号详情共用同一套结果解析，避免升数口径分叉
_RESULT_KEYS = ("gross_m2", "openings_m2", "net_m2", "liters", "coverage", "coats")

def parse_row(row):
    if row is None:
        return None
    d = dict(row)
    try:
        result = json.loads(d.pop("result_json") or "{}")
    except json.JSONDecodeError:
        result = {}
    try:
        d["input"] = json.loads(d.pop("input_json") or "{}")
    except json.JSONDecodeError:
        d["input"] = {}
    d["result"] = result
    for k in _RESULT_KEYS:
        if k in result:
            d[k] = result[k]
    return d

def insert(conn, kind, payload, result, room_id=None):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO calc_runs(kind,room_id,input_json,result_json,created_at) VALUES (?,?,?,?,?)",
        (kind, room_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), now))
    conn.commit(); return int(cur.lastrowid)
def list_recent(conn, limit=50):
    rows = conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [parse_row(r) for r in rows]
def get(conn, run_id):
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    return parse_row(row)
