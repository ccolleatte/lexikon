from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from models import CreateTermRequest, TermResponse, ApiResponse
import database as db

router = APIRouter(prefix="/terms", tags=["terms"])


def get_user_id_from_token(authorization: Optional[str]) -> str:
    """Extract user ID from Bearer token (simplified for Sprint 1)"""
    if not authorization or not authorization.startswith("Bearer "):
        # For Sprint 1, return a default user ID
        return "default-user-id"

    token = authorization.replace("Bearer ", "")
    # Extract user ID from fake token
    if token.startswith("fake-jwt-token-"):
        return token.replace("fake-jwt-token-", "")

    return "default-user-id"


@router.post("", status_code=201)
async def create_term(
    request: CreateTermRequest,
    authorization: Optional[str] = Header(None),
):
    """Create a new term in Quick Draft mode."""

    # Get user ID from token
    user_id = get_user_id_from_token(authorization)

    # Check for duplicate name
    existing = db.get_term_by_name_and_user(request.name, user_id)
    if existing:
        return ApiResponse(
            success=False,
            error={
                "code": "TERM_EXISTS",
                "message": "Un terme avec ce nom existe déjà dans votre ontologie",
                "details": {"name": request.name, "existingTermId": existing["id"]},
            },
        )

    # Create term
    term_data = {
        "name": request.name,
        "definition": request.definition,
        "domain": request.domain,
        "level": request.level,
        "status": request.status,
    }

    term = db.create_term(term_data, user_id)

    # Build response
    response_data = TermResponse(
        id=term["id"],
        name=term["name"],
        definition=term["definition"],
        domain=term.get("domain"),
        level=term["level"],
        status=term["status"],
        createdBy=term["createdBy"],
        createdAt=term["createdAt"],
        updatedAt=term["updatedAt"],
        nextSteps={
            "addRelations": f"/terms/{term['id']}/relations",
            "upgradeLevel": f"/terms/{term['id']}/edit?mode=ready",
            "view": f"/terms/{term['id']}",
        },
    )

    return ApiResponse(success=True, data=response_data.model_dump())


@router.get("")
async def list_terms(
    authorization: Optional[str] = Header(None),
):
    """List all terms for the current user."""

    # Get user ID from token
    user_id = get_user_id_from_token(authorization)

    # Get terms
    user_terms = db.get_terms_by_user(user_id)

    return ApiResponse(
        success=True,
        data=user_terms,
        metadata={"total": len(user_terms)},
    )
