from fastapi import APIRouter, HTTPException
from app.services.paint_service import PaintService
router = APIRouter()
@router.get("/history")
def history(limit: int = 50):
    with PaintService() as s: return {"items": s.history(limit)}
@router.get("/history/{run_id}")
def history_detail(run_id: int):
    with PaintService() as s:
        item = s.run_detail(run_id)
        if not item: raise HTTPException(404, detail=f"编号 {run_id} 不存在")
        return item
