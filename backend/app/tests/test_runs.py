import pytest
from app import db, seed
from app.services.paint_service import PaintService

@pytest.fixture
def svc(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with PaintService() as s:
        yield s

def _count(conn):
    return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]

def test_persisted_run_opened_by_id_matches_write(svc):
    r = svc.estimate(1, persist=True)
    assert r["run_id"] is not None
    pinned = svc.run_detail(r["run_id"])
    assert pinned is not None
    assert pinned["id"] == r["run_id"]
    assert pinned["net_m2"] == r["net_m2"] == 46.41
    assert pinned["openings_m2"] == 3.99
    assert pinned["gross_m2"] == 50.4
    assert pinned["liters"] == r["liters"] == 11.6
    assert pinned["coverage"] == 8.0
    assert pinned["coats"] == 2

def test_missing_id_fails_without_adding_rows(svc):
    before = _count(svc._c)
    assert svc.run_detail(99999) is None
    assert _count(svc._c) == before

def test_old_id_pinned_after_room_changes(svc):
    first = svc.estimate(1, persist=True)
    old_id = first["run_id"]

    # 事后改层高、增删门窗
    svc._c.execute("UPDATE rooms SET height=? WHERE id=?", (3.0, 1))
    svc._c.execute("INSERT INTO openings(room_id,kind,w,h) VALUES (1,'window',1.2,1.5)")
    svc._c.commit()

    # 旧编号仍是写入时的净面积与升数
    pinned = svc.run_detail(old_id)
    assert pinned["net_m2"] == 46.41
    assert pinned["liters"] == 11.6
    assert pinned["openings_m2"] == 3.99

    # 当场再估才反映新参数
    fresh = svc.estimate(1, persist=False)
    assert fresh["run_id"] is None
    assert fresh["net_m2"] == 48.21
    assert fresh["liters"] == 12.05

def test_new_persist_appends_without_overwriting(svc):
    first = svc.estimate(1, persist=True)
    svc._c.execute("UPDATE rooms SET height=? WHERE id=?", (3.0, 1))
    svc._c.commit()
    second = svc.estimate(1, persist=True)

    assert second["run_id"] is not None
    assert second["run_id"] != first["run_id"]
    assert svc.run_detail(first["run_id"])["liters"] == 11.6
    assert svc.run_detail(second["run_id"])["liters"] == 12.5
    rows = svc.history(limit=50)
    ids = [x["id"] for x in rows]
    assert first["run_id"] in ids and second["run_id"] in ids

def test_list_and_detail_share_liter_caliber(svc):
    r = svc.estimate(1, persist=True)
    listed = next(x for x in svc.history(limit=50) if x["id"] == r["run_id"])
    detail = svc.run_detail(r["run_id"])
    assert listed["liters"] == detail["liters"] == r["liters"]
    assert listed["net_m2"] == detail["net_m2"]
    assert listed["coverage"] == detail["coverage"]
    assert listed["coats"] == detail["coats"]
