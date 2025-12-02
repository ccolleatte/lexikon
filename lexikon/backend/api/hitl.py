"""
Human-in-the-Loop (HITL) Workflow API.
Feature 5: HITL Workflow API - Quality validation and review management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

from db.postgres import get_db, HITLReview, Term, User
from auth.middleware import get_current_user
from models import ApiResponse

router = APIRouter(prefix="/hitl", tags=["hitl"])


@router.post("/reviews", status_code=201)
async def create_review_request(
    term_id: str,
    review_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a HITL review request for quality validation.

    Review types:
    - relation_quality: Validate term relations
    - term_clarity: Validate term definition clarity
    - embedding_accuracy: Validate embedding quality
    """
    try:
        logger.info(
            f"Creating review request for term {term_id} "
            f"(type: {review_type}, user: {current_user.id})"
        )

        # Verify term exists
        term = db.query(Term).filter(Term.id == term_id).first()
        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Term not found"
            )

        # Create review
        review = HITLReview(
            id=str(uuid.uuid4()),
            term_id=term_id,
            user_id=current_user.id,
            review_type=review_type,
            status="pending"
        )

        db.add(review)
        db.commit()
        db.refresh(review)

        logger.info(f"Review request created: {review.id}")

        return ApiResponse(
            success=True,
            data={
                'review_id': review.id,
                'term_id': review.term_id,
                'status': review.status,
                'created_at': review.created_at.isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review request"
        )


@router.get("/queue")
async def get_review_queue(
    status: Optional[str] = "pending",
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get pending reviews for the current user.

    Returns: Queue of items awaiting human review
    """
    try:
        logger.info(f"Getting review queue for user {current_user.id} (status: {status})")

        query = db.query(HITLReview).filter(
            HITLReview.user_id == current_user.id
        )

        if status:
            query = query.filter(HITLReview.status == status)

        reviews = query.order_by(HITLReview.created_at).limit(limit).all()

        queue_items = []
        for review in reviews:
            term = db.query(Term).filter(Term.id == review.term_id).first()
            if term:
                queue_items.append({
                    'review_id': review.id,
                    'term_id': review.term_id,
                    'term_name': term.name,
                    'review_type': review.review_type,
                    'status': review.status,
                    'created_at': review.created_at.isoformat()
                })

        return ApiResponse(
            success=True,
            data=queue_items,
            metadata={'total': len(queue_items), 'limit': limit}
        )

    except Exception as e:
        logger.error(f"Error getting review queue: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get review queue"
        )


@router.post("/reviews/{review_id}/approve")
async def approve_review(
    review_id: str,
    feedback: Optional[str] = None,
    confidence: float = 1.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve a review item."""
    try:
        logger.info(f"Approving review {review_id} (user: {current_user.id})")

        review = db.query(HITLReview).filter(
            HITLReview.id == review_id,
            HITLReview.user_id == current_user.id
        ).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        from datetime import datetime
        review.status = "approved"
        review.feedback = feedback
        review.confidence_score = confidence
        review.reviewed_by = current_user.id
        review.reviewed_at = datetime.utcnow()

        db.commit()

        logger.info(f"Review {review_id} approved")

        return ApiResponse(
            success=True,
            data={'review_id': review.id, 'status': review.status}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving review: {type(e).__name__}: {str(e)}")
        raise


@router.post("/reviews/{review_id}/reject")
async def reject_review(
    review_id: str,
    feedback: str,
    confidence: float = 1.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reject a review item with feedback."""
    try:
        logger.info(f"Rejecting review {review_id} (user: {current_user.id})")

        review = db.query(HITLReview).filter(
            HITLReview.id == review_id,
            HITLReview.user_id == current_user.id
        ).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        from datetime import datetime
        review.status = "rejected"
        review.feedback = feedback
        review.confidence_score = confidence
        review.reviewed_by = current_user.id
        review.reviewed_at = datetime.utcnow()

        db.commit()

        logger.info(f"Review {review_id} rejected")

        return ApiResponse(
            success=True,
            data={'review_id': review.id, 'status': review.status}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting review: {type(e).__name__}: {str(e)}")
        raise


@router.get("/queue/metrics")
async def get_queue_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get HITL queue statistics."""
    try:
        from sqlalchemy import func

        pending = db.query(func.count(HITLReview.id)).filter(
            HITLReview.user_id == current_user.id,
            HITLReview.status == "pending"
        ).scalar() or 0

        approved = db.query(func.count(HITLReview.id)).filter(
            HITLReview.user_id == current_user.id,
            HITLReview.status == "approved"
        ).scalar() or 0

        rejected = db.query(func.count(HITLReview.id)).filter(
            HITLReview.user_id == current_user.id,
            HITLReview.status == "rejected"
        ).scalar() or 0

        return ApiResponse(
            success=True,
            data={
                'pending': pending,
                'approved': approved,
                'rejected': rejected,
                'total': pending + approved + rejected
            }
        )

    except Exception as e:
        logger.error(f"Error getting queue metrics: {type(e).__name__}: {str(e)}")
        raise
