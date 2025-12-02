"""
Vocabularies API - Extraction and Bulk Import endpoints.
Feature 4: Vocabulary Extraction from documents
Feature 3: Bulk Import from multiple formats
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import logging
import time

logger = logging.getLogger(__name__)

from db.postgres import get_db, User
from auth.middleware import get_current_user
from models import (
    ExtractionRequest, ExtractionResponse, ExtractedTermItem,
    BulkImportRequest, BulkImportResponse, ImportStats, ApiResponse
)
from services.extraction import vocabulary_extractor
from services.bulk_import import get_bulk_import_service

router = APIRouter(prefix="/vocabularies", tags=["vocabularies"])


@router.post("/extract", response_model=ExtractionResponse)
async def extract_vocabulary(
    request: ExtractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Extract terms from document content using multiple patterns.

    Supported patterns:
    - parentheses: "Term (definition)"
    - bold: **Term**, <b>Term</b>
    - glossary: "Term: definition" or "Term - definition"
    - inline_definition: "le/la Term est/signifie"

    Returns: List of extracted terms with confidence scores
    """
    start_time = time.time()

    try:
        logger.info(
            f"Extracting vocabulary from document ({len(request.content)} chars, "
            f"patterns: {request.patterns or 'all'}, user: {current_user.id})"
        )

        patterns = request.patterns or [
            'parentheses', 'bold', 'glossary', 'inline_definition'
        ]

        # Extract terms
        extracted = vocabulary_extractor.extract_terms(
            text=request.content,
            patterns=patterns,
            language=request.language
        )

        # Format response
        extracted_items = [
            ExtractedTermItem(
                text=term.text,
                definition=term.definition,
                pattern=term.pattern,
                confidence=term.confidence
            )
            for term in extracted
        ]

        execution_time = (time.time() - start_time) * 1000

        logger.info(
            f"Extracted {len(extracted_items)} terms from document "
            f"(user: {current_user.id})"
        )

        return ExtractionResponse(
            extracted_terms=extracted_items,
            total=len(extracted_items),
            patterns_used=patterns,
            execution_time_ms=round(execution_time, 2)
        )

    except Exception as e:
        logger.error(f"Extraction error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vocabulary extraction failed"
        )


@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_terms(
    request: BulkImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Bulk import terms from file content.

    Supported formats:
    - json: [{"name": "Term", "definition": "...", "domain": "...", ...}]
    - csv: name,definition,domain,level,status
    - skos: RDF/SKOS Turtle format

    Import modes:
    - create_only: Only create new terms, skip existing
    - update_only: Only update existing terms, skip new
    - upsert: Create new or update existing (default)

    Returns: Import statistics (created, updated, skipped)
    """
    start_time = time.time()

    try:
        logger.info(
            f"Bulk importing terms (format: {request.format}, "
            f"mode: {request.mode}, size: {len(request.content)} bytes, "
            f"user: {current_user.id})"
        )

        # Get import service
        importer = get_bulk_import_service(db)

        # Import based on format
        if request.format == 'json':
            result = importer.import_from_json(
                content=request.content,
                user_id=current_user.id,
                mode=request.mode
            )
        elif request.format == 'csv':
            result = importer.import_from_csv(
                content=request.content,
                user_id=current_user.id,
                mode=request.mode
            )
        elif request.format == 'skos':
            result = importer.import_from_skos(
                content=request.content,
                user_id=current_user.id,
                mode=request.mode
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {request.format}"
            )

        # Check for errors
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Import failed')
            )

        stats = result.get('stats', {})
        execution_time = (time.time() - start_time) * 1000

        logger.info(
            f"Import completed: {stats['created']} created, "
            f"{stats['updated']} updated, {stats['skipped']} skipped "
            f"(user: {current_user.id})"
        )

        return BulkImportResponse(
            success=True,
            stats=ImportStats(
                created=stats['created'],
                updated=stats['updated'],
                skipped=stats['skipped'],
                total=stats['total']
            ),
            errors=result.get('errors'),
            execution_time_ms=round(execution_time, 2)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk import error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk import failed"
        )
