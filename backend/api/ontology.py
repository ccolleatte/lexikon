"""
Ontology API endpoints for term relations and reasoning.
Includes endpoints for creating relations, querying relations, and inferring new relations.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import logging
import time

logger = logging.getLogger(__name__)

from db.postgres import get_db, TermRelation, Term, User
from auth.middleware import get_current_user
from models import (
    CreateRelationRequest, RelationResponse, InferenceRequest, InferenceResponse,
    InferredRelation, ApiResponse
)
from services.reasoning import get_reasoning_engine

router = APIRouter(prefix="/ontology", tags=["ontology"])


@router.post("/relations", status_code=201, response_model=RelationResponse)
async def create_relation(
    request: CreateRelationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new relation between two terms.

    The relation represents a semantic link (broader, narrower, equivalent, etc.)
    Used for ontology building and knowledge graph construction.
    """
    try:
        logger.info(
            f"Creating relation: {request.source_term_id} --[{request.relation_type}]-> "
            f"{request.target_term_id} (user: {current_user.id})"
        )

        # Verify both terms exist and belong to user
        source_term = db.query(Term).filter(
            Term.id == request.source_term_id,
            Term.created_by == current_user.id
        ).first()

        if not source_term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source term not found: {request.source_term_id}"
            )

        target_term = db.query(Term).filter(
            Term.id == request.target_term_id,
            Term.created_by == current_user.id
        ).first()

        if not target_term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target term not found: {request.target_term_id}"
            )

        # Check if relation already exists
        existing = db.query(TermRelation).filter(
            TermRelation.source_term_id == request.source_term_id,
            TermRelation.target_term_id == request.target_term_id,
            TermRelation.relation_type == request.relation_type
        ).first()

        if existing:
            logger.warning(f"Relation already exists: {existing.id}")
            return RelationResponse(
                id=existing.id,
                source_term_id=existing.source_term_id,
                target_term_id=existing.target_term_id,
                relation_type=existing.relation_type,
                confidence=existing.confidence,
                created_by=existing.created_by,
                created_at=existing.created_at.isoformat()
            )

        # Create relation
        relation = TermRelation(
            id=str(uuid.uuid4()),
            source_term_id=request.source_term_id,
            target_term_id=request.target_term_id,
            relation_type=request.relation_type,
            confidence=request.confidence,
            created_by=current_user.id,
            metadata=request.metadata
        )

        db.add(relation)
        db.commit()
        db.refresh(relation)

        logger.info(f"Relation created: {relation.id}")

        return RelationResponse(
            id=relation.id,
            source_term_id=relation.source_term_id,
            target_term_id=relation.target_term_id,
            relation_type=relation.relation_type,
            confidence=relation.confidence,
            created_by=relation.created_by,
            created_at=relation.created_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating relation: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create relation"
        )


@router.post("/infer", response_model=InferenceResponse)
async def infer_relations(
    request: InferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Infer new relations for a term using reasoning rules.

    Applies reasoning rules (transitive, symmetric, equivalence, inverse)
    to discover implicit relations in the ontology.

    Returns: New inferred relations with confidence scores and rule attribution.
    """
    start_time = time.time()

    try:
        logger.info(
            f"Inferring relations for term {request.term_id} "
            f"(rules: {request.rules}, user: {current_user.id})"
        )

        # Verify term exists and belongs to user
        term = db.query(Term).filter(
            Term.id == request.term_id,
            Term.created_by == current_user.id
        ).first()

        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Term not found: {request.term_id}"
            )

        # Get reasoning engine and infer
        reasoner = get_reasoning_engine(db)
        inferred_relations = reasoner.infer_relations(
            term_id=request.term_id,
            rules=request.rules or ['transitive', 'symmetric', 'equivalence', 'inverse'],
            max_depth=request.max_depth,
            confidence_threshold=request.confidence_threshold
        )

        # Enrich with term names
        inferred_enriched = []
        for rel in inferred_relations:
            target_term = db.query(Term).filter(
                Term.id == rel['target_term_id']
            ).first()

            if target_term:
                inferred_enriched.append(InferredRelation(
                    target_term_id=rel['target_term_id'],
                    target_term_name=target_term.name,
                    relation_type=rel['relation_type'],
                    confidence=rel['confidence'],
                    rule=rel['rule'],
                    depth=rel['depth']
                ))

        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        logger.info(
            f"Inference completed: {len(inferred_enriched)} relations inferred "
            f"(term: {request.term_id}, user: {current_user.id})"
        )

        return InferenceResponse(
            term_id=request.term_id,
            inferred_relations=inferred_enriched,
            rules_applied=request.rules or ['transitive', 'symmetric', 'equivalence', 'inverse'],
            total_inferred=len(inferred_enriched),
            execution_time_ms=round(execution_time, 2)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inferring relations: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference failed. Please try again."
        )


@router.get("/relations/{term_id}")
async def get_term_relations(
    term_id: str,
    direction: str = "outgoing",  # outgoing, incoming, both
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all direct relations for a term.

    Args:
        term_id: The term to query
        direction: Relation direction (outgoing, incoming, both)

    Returns: List of relations with term details
    """
    try:
        logger.info(f"Getting {direction} relations for term {term_id} (user: {current_user.id})")

        # Verify term belongs to user
        term = db.query(Term).filter(
            Term.id == term_id,
            Term.created_by == current_user.id
        ).first()

        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Term not found"
            )

        # Get relations
        reasoner = get_reasoning_engine(db)
        relations = reasoner.get_term_relations(term_id, direction)

        # Format response
        results = []
        for rel in relations:
            target = db.query(Term).filter(Term.id == rel.target_term_id).first()
            source = db.query(Term).filter(Term.id == rel.source_term_id).first()

            if target and source:
                results.append({
                    'id': rel.id,
                    'source_id': rel.source_term_id,
                    'source_name': source.name,
                    'target_id': rel.target_term_id,
                    'target_name': target.name,
                    'relation_type': rel.relation_type,
                    'confidence': rel.confidence,
                    'created_at': rel.created_at.isoformat()
                })

        return ApiResponse(
            success=True,
            data=results,
            metadata={'total': len(results), 'direction': direction}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting relations: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve relations"
        )


@router.delete("/relations/{relation_id}", status_code=204)
async def delete_relation(
    relation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a relation (only creator can delete)."""
    try:
        logger.info(f"Deleting relation {relation_id} (user: {current_user.id})")

        relation = db.query(TermRelation).filter(
            TermRelation.id == relation_id,
            TermRelation.created_by == current_user.id
        ).first()

        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relation not found or unauthorized"
            )

        db.delete(relation)
        db.commit()

        logger.info(f"Relation {relation_id} deleted")
        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting relation: {type(e).__name__}: {str(e)}", exc_info=True)
        raise
