"""
Terms API endpoints with BOLA (Broken Object Level Authorization) fix.
Requires ownership verification for all term access.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

from db.postgres import get_db, Term, User
from auth.middleware import get_current_user
from models import CreateTermRequest, TermResponse, ApiResponse

router = APIRouter(prefix="/terms", tags=["terms"])


@router.post("", status_code=201)
async def create_term(
    request: CreateTermRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new term in Quick Draft mode.

    Note: Terms currently don't require project_id (nullable for MVP).
    Will require project_id in future versions.
    """
    try:
        logger.info(f"Creating term '{request.name}' for user {current_user.id}")

        # Check for duplicate name within user's terms
        existing = db.query(Term).filter(
            Term.name == request.name,
            Term.created_by == current_user.id
        ).first()

        if existing:
            logger.warning(f"Term '{request.name}' already exists for user {current_user.id}")
            return ApiResponse(
                success=False,
                error={
                    "code": "TERM_EXISTS",
                    "message": "Un terme avec ce nom existe déjà dans votre ontologie",
                    "details": {"name": request.name, "existingTermId": existing.id},
                },
            )

        # Create term
        term = Term(
            id=str(uuid.uuid4()),
            name=request.name,
            definition=request.definition,
            domain=request.domain,
            level=request.level,
            status=request.status,
            created_by=current_user.id,
            project_id=None,  # TODO: Make required in future versions
        )

        db.add(term)
        db.commit()
        db.refresh(term)

        logger.info(f"Term '{term.id}' created successfully")

        # Build response
        response_data = TermResponse(
            id=term.id,
            name=term.name,
            definition=term.definition,
            domain=term.domain,
            level=term.level,
            status=term.status,
            createdBy=term.created_by,
            createdAt=term.created_at.isoformat(),
            updatedAt=term.updated_at.isoformat(),
            nextSteps={
                "addRelations": f"/terms/{term.id}/relations",
                "upgradeLevel": f"/terms/{term.id}/edit?mode=ready",
                "view": f"/terms/{term.id}",
            },
        )

        return ApiResponse(success=True, data=response_data.model_dump())

    except Exception as e:
        logger.error(f"Error creating term: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.get("")
async def list_terms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all terms for the current user."""

    try:
        logger.info(f"Listing terms for user {current_user.id}")

        # Get all terms created by current user
        user_terms = db.query(Term).filter(
            Term.created_by == current_user.id
        ).all()

        return ApiResponse(
            success=True,
            data=[
                {
                    "id": term.id,
                    "name": term.name,
                    "definition": term.definition,
                    "domain": term.domain,
                    "level": term.level,
                    "status": term.status,
                    "createdBy": term.created_by,
                    "createdAt": term.created_at.isoformat(),
                    "updatedAt": term.updated_at.isoformat(),
                }
                for term in user_terms
            ],
            metadata={"total": len(user_terms)},
        )

    except Exception as e:
        logger.error(f"Error listing terms: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.get("/{term_id}")
async def get_term(
    term_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific term by ID with ownership verification (BOLA fix)."""

    try:
        logger.info(f"Getting term {term_id} for user {current_user.id}")

        # ✅ BOLA FIX: Verify ownership before returning
        term = db.query(Term).filter(
            Term.id == term_id,
            Term.created_by == current_user.id  # ← Critical: Ownership check
        ).first()

        if not term:
            logger.warning(f"Term {term_id} not found or unauthorized for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Term not found"
            )

        return ApiResponse(
            success=True,
            data={
                "id": term.id,
                "name": term.name,
                "definition": term.definition,
                "domain": term.domain,
                "level": term.level,
                "status": term.status,
                "createdBy": term.created_by,
                "createdAt": term.created_at.isoformat(),
                "updatedAt": term.updated_at.isoformat(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting term {term_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.put("/{term_id}")
async def update_term(
    term_id: str,
    request: CreateTermRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a term with ownership verification (BOLA fix)."""

    try:
        logger.info(f"Updating term {term_id} for user {current_user.id}")

        # ✅ BOLA FIX: Verify ownership before updating
        term = db.query(Term).filter(
            Term.id == term_id,
            Term.created_by == current_user.id  # ← Critical: Ownership check
        ).first()

        if not term:
            logger.warning(f"Term {term_id} not found or unauthorized for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Term not found"
            )

        # Update fields
        term.name = request.name
        term.definition = request.definition
        term.domain = request.domain
        term.level = request.level
        term.status = request.status

        db.commit()
        db.refresh(term)

        logger.info(f"Term {term_id} updated successfully")

        return ApiResponse(
            success=True,
            data={
                "id": term.id,
                "name": term.name,
                "definition": term.definition,
                "domain": term.domain,
                "level": term.level,
                "status": term.status,
                "createdBy": term.created_by,
                "createdAt": term.created_at.isoformat(),
                "updatedAt": term.updated_at.isoformat(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating term {term_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.delete("/{term_id}", status_code=204)
async def delete_term(
    term_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a term with ownership verification (BOLA fix)."""

    try:
        logger.info(f"Deleting term {term_id} for user {current_user.id}")

        # ✅ BOLA FIX: Verify ownership before deleting
        term = db.query(Term).filter(
            Term.id == term_id,
            Term.created_by == current_user.id  # ← Critical: Ownership check
        ).first()

        if not term:
            logger.warning(f"Term {term_id} not found or unauthorized for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Term not found"
            )

        db.delete(term)
        db.commit()

        logger.info(f"Term {term_id} deleted successfully")

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting term {term_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise
