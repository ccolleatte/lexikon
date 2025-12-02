"""
Analytics API - Metrics and ontology health monitoring.
Feature 6: Analytics & Metrics API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

from db.postgres import get_db, User
from auth.middleware import get_current_user
from models import ApiResponse
from services.analytics import get_analytics_service

router = APIRouter(prefix="/metrics", tags=["analytics"])


@router.get("/usage")
async def get_usage_metrics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get usage metrics for your vocabulary.

    Returns:
    - total_terms: Count of all terms
    - terms_by_level: Distribution across quick-draft, ready, expert
    - terms_by_status: Distribution across draft, ready, validated
    - total_relations: Count of all term relations
    """
    try:
        logger.info(f"Getting usage metrics for user {current_user.id} (last {days} days)")

        analytics = get_analytics_service(db)
        metrics = analytics.get_usage_metrics(current_user.id, days)

        return ApiResponse(
            success=True,
            data=metrics,
            metadata={'generated_at': 'ISO-8601 timestamp'}
        )

    except Exception as e:
        logger.error(f"Error getting usage metrics: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics"
        )


@router.get("/ontology-health")
async def get_ontology_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get ontology quality and coverage metrics.

    Returns:
    - terms_with_embeddings: Count of terms with vector embeddings
    - embedding_coverage_percent: Percentage of terms with embeddings
    - terms_with_relations: Count of terms with at least one relation
    - relation_coverage_percent: Percentage of terms with relations
    - average_relation_confidence: Mean confidence score of relations
    - distinct_domains: Number of different domains covered
    """
    try:
        logger.info(f"Getting ontology health for user {current_user.id}")

        analytics = get_analytics_service(db)
        metrics = analytics.get_ontology_metrics(current_user.id)

        return ApiResponse(
            success=True,
            data=metrics,
            metadata={'generated_at': 'ISO-8601 timestamp'}
        )

    except Exception as e:
        logger.error(f"Error getting ontology metrics: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get ontology metrics"
        )


@router.get("/growth")
async def get_growth_metrics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get growth statistics over time period.

    Returns:
    - terms_added: New terms created in period
    - relations_added: New relations created in period
    - daily_average_terms: Average terms per day
    - daily_average_relations: Average relations per day
    """
    try:
        logger.info(f"Getting growth metrics for user {current_user.id} (last {days} days)")

        analytics = get_analytics_service(db)
        metrics = analytics.get_growth_metrics(current_user.id, days)

        return ApiResponse(
            success=True,
            data=metrics,
            metadata={'period_days': days}
        )

    except Exception as e:
        logger.error(f"Error getting growth metrics: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get growth metrics"
        )


@router.get("/drift-detection")
async def detect_vocabulary_drift(
    threshold: float = 0.8,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Detect vocabulary drift - identify isolated terms with no relations.

    This helps identify terms that might need better contextualization
    or review for relevance to the ontology.

    Returns:
    - isolated_terms_count: Total count of isolated terms
    - isolated_terms: Sample of top isolated terms
    - status: 'healthy' or 'drifting'
    """
    try:
        logger.info(f"Detecting vocabulary drift for user {current_user.id}")

        analytics = get_analytics_service(db)
        metrics = analytics.detect_vocabulary_drift(current_user.id, threshold)

        return ApiResponse(
            success=True,
            data=metrics,
            metadata={'threshold': threshold}
        )

    except Exception as e:
        logger.error(f"Error detecting drift: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze vocabulary drift"
        )
