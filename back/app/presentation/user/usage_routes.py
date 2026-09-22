from fastapi import APIRouter, Depends

from app.application.user.get_usage_summary import GetUsageSummary
from .dependencies import current_user_mail, token_repo, usage_repo

router = APIRouter(tags=["Usage"])


@router.get("/usage/today")
def get_today_usage(mail: str = Depends(current_user_mail), tokens=Depends(token_repo), events=Depends(usage_repo)):
    return GetUsageSummary(tokens, events).execute(mail)
