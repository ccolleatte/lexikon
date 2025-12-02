from fastapi import APIRouter, HTTPException
from models import (
    AdoptionLevelRequest,
    AdoptionLevelResponse,
    ApiResponse,
)
import database as db

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/adoption-level")
async def save_adoption_level(request: AdoptionLevelRequest):
    """Save the user's selected adoption level during onboarding."""

    # Store in database
    session = db.create_onboarding_session(request.sessionId, request.adoptionLevel)

    # Get features based on level
    features_map = {
        "quick-project": [
            "Setup en 30 minutes",
            "Export quand terminé",
            "Gratuit, pas de validation obligatoire",
        ],
        "research-project": [
            "Collaboration avec pairs",
            "Validation experte optionnelle",
            "Export multi-formats (RDF, JSON-LD, CSV)",
        ],
        "production-api": [
            "API REST complète",
            "Webhooks & GraphQL",
            "SLA 99.9% uptime",
        ],
    }

    recommended_tier_map = {
        "quick-project": "free",
        "research-project": "pro",
        "production-api": "team",
    }

    response_data = AdoptionLevelResponse(
        adoptionLevel=request.adoptionLevel,
        sessionId=request.sessionId,
        nextStep="/onboarding/profile",
        recommendedTier=recommended_tier_map[request.adoptionLevel],
        features=features_map[request.adoptionLevel],
    )

    return ApiResponse(success=True, data=response_data.model_dump())
