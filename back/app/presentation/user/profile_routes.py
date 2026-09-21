from fastapi import APIRouter, Depends

from app.application.user.get_profile import GetProfile, ProfileNotFoundError
from app.application.user.update_profile import UpdateProfile
from .dependencies import current_user_mail, user_repo
from .errors import error_response, validation_error_response
from .profile_schemas import ProfileUpdateRequest
from .serializers import user_profile

router = APIRouter(tags=["Profile"])


@router.get("/profile")
def get_profile(mail: str = Depends(current_user_mail), users=Depends(user_repo)):
    try:
        return user_profile(GetProfile(users).execute(mail))
    except ProfileNotFoundError:
        raise error_response("Authentication required", 401)


@router.patch("/profile")
def update_profile(payload: ProfileUpdateRequest, mail: str = Depends(current_user_mail), users=Depends(user_repo)):
    try:
        user = UpdateProfile(users).execute(mail, payload.age, payload.profession, payload.displayName)
        return user_profile(user)
    except ProfileNotFoundError:
        raise error_response("Authentication required", 401)
    except ValueError as exc:
        raise validation_error_response(str(exc), {"profile": str(exc)})
