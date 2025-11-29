"""
Bulk Import Service - Import terms from CSV, JSON, RDF/SKOS formats.
"""

import json
import csv
import logging
from typing import List, Dict, Optional
from io import StringIO
from sqlalchemy.orm import Session
from db.postgres import Term
import uuid

logger = logging.getLogger(__name__)


class BulkImportService:
    """Import terms from various formats."""

    def __init__(self, db: Session):
        self.db = db

    def import_from_json(
        self,
        content: str,
        user_id: str,
        mode: str = "upsert"  # create_only, update_only, upsert
    ) -> Dict:
        """Import terms from JSON array format."""
        try:
            data = json.loads(content)
            if not isinstance(data, list):
                return {'success': False, 'error': 'JSON must be an array'}

            results = self._import_terms(data, user_id, mode)
            return results

        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'Invalid JSON: {str(e)}'}
        except Exception as e:
            logger.error(f"JSON import error: {e}")
            return {'success': False, 'error': str(e)}

    def import_from_csv(
        self,
        content: str,
        user_id: str,
        mode: str = "upsert"
    ) -> Dict:
        """Import terms from CSV (name,definition,domain,level,status)."""
        try:
            reader = csv.DictReader(StringIO(content))
            terms = []

            for row in reader:
                if row.get('name') and row.get('definition'):
                    terms.append({
                        'name': row['name'],
                        'definition': row['definition'],
                        'domain': row.get('domain'),
                        'level': row.get('level', 'quick-draft'),
                        'status': row.get('status', 'draft')
                    })

            results = self._import_terms(terms, user_id, mode)
            return results

        except Exception as e:
            logger.error(f"CSV import error: {e}")
            return {'success': False, 'error': str(e)}

    def import_from_skos(
        self,
        content: str,
        user_id: str,
        mode: str = "upsert"
    ) -> Dict:
        """
        Import from SKOS RDF format (simplified).
        Extracts prefLabel and definition from Turtle/RDF.
        """
        try:
            terms = []
            lines = content.split('\n')

            # Simple SKOS parser (not full RDF, just extracts patterns)
            current_term = None

            for line in lines:
                line = line.strip()

                if 'skos:prefLabel' in line:
                    # Extract label: ... skos:prefLabel "Term Name" ;
                    match = line.split('"')[1] if '"' in line else None
                    if match:
                        current_term = {'name': match}

                elif 'skos:definition' in line and current_term:
                    # Extract definition: ... skos:definition "..."
                    match = line.split('"')[1] if '"' in line else None
                    if match:
                        current_term['definition'] = match
                        current_term['level'] = 'quick-draft'
                        current_term['status'] = 'draft'
                        terms.append(current_term)
                        current_term = None

            results = self._import_terms(terms, user_id, mode)
            return results

        except Exception as e:
            logger.error(f"SKOS import error: {e}")
            return {'success': False, 'error': str(e)}

    def _import_terms(
        self,
        terms: List[Dict],
        user_id: str,
        mode: str
    ) -> Dict:
        """Core import logic for all formats."""
        created = 0
        updated = 0
        skipped = 0
        errors = []

        for term_data in terms:
            try:
                # Validation
                if not term_data.get('name') or not term_data.get('definition'):
                    skipped += 1
                    continue

                # Check if exists
                existing = self.db.query(Term).filter(
                    Term.name == term_data['name'],
                    Term.created_by == user_id
                ).first()

                if existing:
                    if mode == 'create_only':
                        skipped += 1
                        continue

                    # Update existing
                    existing.definition = term_data['definition']
                    existing.domain = term_data.get('domain')
                    existing.level = term_data.get('level', 'quick-draft')
                    existing.status = term_data.get('status', 'draft')
                    self.db.commit()
                    updated += 1

                else:
                    if mode == 'update_only':
                        skipped += 1
                        continue

                    # Create new
                    new_term = Term(
                        id=str(uuid.uuid4()),
                        name=term_data['name'],
                        definition=term_data['definition'],
                        domain=term_data.get('domain'),
                        level=term_data.get('level', 'quick-draft'),
                        status=term_data.get('status', 'draft'),
                        created_by=user_id
                    )
                    self.db.add(new_term)
                    self.db.commit()
                    created += 1

            except Exception as e:
                skipped += 1
                errors.append({
                    'term': term_data.get('name', 'unknown'),
                    'error': str(e)
                })
                logger.error(f"Import error for {term_data.get('name')}: {e}")

        return {
            'success': True,
            'stats': {
                'created': created,
                'updated': updated,
                'skipped': skipped,
                'total': len(terms)
            },
            'errors': errors if errors else None
        }


def get_bulk_import_service(db: Session) -> BulkImportService:
    """Factory for bulk import service."""
    return BulkImportService(db)
