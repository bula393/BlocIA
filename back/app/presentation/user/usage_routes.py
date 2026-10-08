from fastapi import APIRouter, Depends, Query

from app.application.user.get_usage_summary import GetUsageSummary
from .dependencies import current_user_mail, token_repo, usage_repo
from app.infrastructure.database import get_database
from app.infrastructure.usage_analytics_repository import UsageAnalyticsRepository

router = APIRouter(tags=["Usage"])


@router.get("/usage/today")
def get_today_usage(mail: str = Depends(current_user_mail), tokens=Depends(token_repo), events=Depends(usage_repo)):
    return GetUsageSummary(tokens, events).execute(mail)


@router.get("/usage/dashboard")
def get_usage_dashboard(
    mail: str = Depends(current_user_mail),
    database=Depends(get_database),
    limit: int = Query(default=40, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return UsageAnalyticsRepository(database).dashboard(mail, limit, offset)


@router.get("/usage/limits")
def get_usage_limits(mail: str = Depends(current_user_mail), database=Depends(get_database)):
    return UsageAnalyticsRepository(database).current_lock(mail)
