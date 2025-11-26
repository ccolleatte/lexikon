"""
Analytics & Metrics Service - Track usage and analyze ontology health.
Feature 6: Analytics & Metrics API
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.postgres import Term, TermRelation

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Track and analyze vocabulary/ontology metrics."""

    def __init__(self, db: Session):
        self.db = db

    def get_usage_metrics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """Get usage statistics for the last N days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Total terms
            total_terms = self.db.query(func.count(Term.id)).filter(
                Term.created_by == user_id
            ).scalar() or 0

            # Terms by level
            terms_by_level = self.db.query(
                Term.level,
                func.count(Term.id)
            ).filter(
                Term.created_by == user_id
            ).group_by(Term.level).all()

            level_stats = {
                'quick-draft': 0,
                'ready': 0,
                'expert': 0
            }
            for level, count in terms_by_level:
                if level:
                    level_stats[level] = count

            # Terms by status
            terms_by_status = self.db.query(
                Term.status,
                func.count(Term.id)
            ).filter(
                Term.created_by == user_id
            ).group_by(Term.status).all()

            status_stats = {
                'draft': 0,
                'ready': 0,
                'validated': 0
            }
            for status, count in terms_by_status:
                if status:
                    status_stats[status] = count

            # Relations count
            relations_count = self.db.query(func.count(TermRelation.id)).filter(
                TermRelation.created_by == user_id
            ).scalar() or 0

            return {
                'total_terms': total_terms,
                'terms_by_level': level_stats,
                'terms_by_status': status_stats,
                'total_relations': relations_count,
                'period_days': days
            }

        except Exception as e:
            logger.error(f"Error getting usage metrics: {e}")
            return {}

    def get_ontology_metrics(
        self,
        user_id: str
    ) -> Dict:
        """Get ontology quality and coverage metrics."""
        try:
            # Terms with embeddings
            terms_with_embeddings = self.db.query(func.count(Term.id)).filter(
                Term.created_by == user_id,
                Term.embedding.isnot(None)
            ).scalar() or 0

            # Terms with relations
            all_terms = self.db.query(Term.id).filter(
                Term.created_by == user_id
            ).all()

            terms_with_relations = 0
            for term in all_terms:
                rel_count = self.db.query(func.count(TermRelation.id)).filter(
                    (TermRelation.source_term_id == term.id) |
                    (TermRelation.target_term_id == term.id)
                ).scalar() or 0

                if rel_count > 0:
                    terms_with_relations += 1

            # Average confidence
            avg_confidence = self.db.query(func.avg(TermRelation.confidence)).filter(
                TermRelation.created_by == user_id
            ).scalar() or 0

            # Domains
            domain_count = self.db.query(func.count(func.distinct(Term.domain))).filter(
                Term.created_by == user_id,
                Term.domain.isnot(None)
            ).scalar() or 0

            total_terms = self.db.query(func.count(Term.id)).filter(
                Term.created_by == user_id
            ).scalar() or 1  # Avoid division by zero

            return {
                'terms_with_embeddings': terms_with_embeddings,
                'embedding_coverage_percent': round((terms_with_embeddings / total_terms) * 100, 2),
                'terms_with_relations': terms_with_relations,
                'relation_coverage_percent': round((terms_with_relations / total_terms) * 100, 2),
                'average_relation_confidence': round(avg_confidence, 3),
                'distinct_domains': domain_count,
                'total_terms': total_terms
            }

        except Exception as e:
            logger.error(f"Error getting ontology metrics: {e}")
            return {}

    def get_growth_metrics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """Get growth statistics (terms added, relations created, etc.)."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Terms added in period
            terms_added = self.db.query(func.count(Term.id)).filter(
                Term.created_by == user_id,
                Term.created_at >= cutoff_date
            ).scalar() or 0

            # Relations added in period
            relations_added = self.db.query(func.count(TermRelation.id)).filter(
                TermRelation.created_by == user_id,
                TermRelation.created_at >= cutoff_date
            ).scalar() or 0

            return {
                'period_days': days,
                'terms_added': terms_added,
                'relations_added': relations_added,
                'daily_average_terms': round(terms_added / max(days, 1), 2),
                'daily_average_relations': round(relations_added / max(days, 1), 2)
            }

        except Exception as e:
            logger.error(f"Error getting growth metrics: {e}")
            return {}

    def detect_vocabulary_drift(
        self,
        user_id: str,
        threshold: float = 0.8
    ) -> Dict:
        """
        Detect vocabulary drift - terms with low/no relations might indicate drift.
        Returns isolated terms that might need attention.
        """
        try:
            isolated_terms = []

            terms = self.db.query(Term).filter(
                Term.created_by == user_id
            ).all()

            for term in terms:
                rel_count = self.db.query(func.count(TermRelation.id)).filter(
                    (TermRelation.source_term_id == term.id) |
                    (TermRelation.target_term_id == term.id)
                ).scalar() or 0

                if rel_count == 0:
                    isolated_terms.append({
                        'term_id': term.id,
                        'term_name': term.name,
                        'status': 'isolated',
                        'relation_count': 0
                    })

            return {
                'isolated_terms_count': len(isolated_terms),
                'isolated_terms': isolated_terms[:10],  # Top 10
                'status': 'drifting' if len(isolated_terms) > threshold * len(terms) else 'healthy'
            }

        except Exception as e:
            logger.error(f"Error detecting drift: {e}")
            return {'error': str(e)}


def get_analytics_service(db: Session) -> AnalyticsService:
    """Factory for analytics service."""
    return AnalyticsService(db)
