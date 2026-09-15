from fastapi import APIRouter, HTTPException, Query

from app.services.currency_service import get_rates

router = APIRouter(prefix="/api/currency", tags=["currency"])


@router.get("/rates")
def currency_rates(base: str = Query(default="USD", min_length=3, max_length=3)):
    try:
        return {"base": base.upper(), "rates": get_rates(base)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Currency provider unavailable") from exc