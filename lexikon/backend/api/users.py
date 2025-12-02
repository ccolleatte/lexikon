from fastapi import APIRouter, HTTPException
from models import UserProfileRequest, UserProfileResponse, ApiResponse
import database as db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/profile", status_code=201)
async def create_user_profile(request: UserProfileRequest):
    """Create or update user profile during onboarding."""

    # Check if email already exists
    existing = db.get_user_by_email(request.email)
    if existing:
        return ApiResponse(
            success=False,
            error={
                "code": "EMAIL_EXISTS",
                "message": "Cette adresse email est déjà utilisée",
                "details": {"email": request.email},
            },
        )

    # Get adoption level from session
    session = db.get_onboarding_session(request.sessionId)
    adoption_level = session["adoptionLevel"] if session else "quick-project"

    # Create user
    user_data = {
        "firstName": request.firstName,
        "lastName": request.lastName,
        "email": request.email,
        "institution": request.institution,
        "primaryDomain": request.primaryDomain,
        "language": request.language,
        "country": request.country,
        "adoptionLevel": adoption_level,
    }

    user = db.create_user(user_data)

    # Generate fake JWT token for now
    access_token = f"fake-jwt-token-{user['id']}"

    response_data = UserProfileResponse(
        id=user["id"],
        firstName=user["firstName"],
        lastName=user["lastName"],
        email=user["email"],
        institution=user.get("institution"),
        primaryDomain=user.get("primaryDomain"),
        language=user["language"],
        country=user.get("country"),
        adoptionLevel=user["adoptionLevel"],
        createdAt=user["createdAt"],
        accessToken=access_token,
        nextStep="/onboarding/preferences",
    )

    return ApiResponse(success=True, data=response_data.model_dump())
