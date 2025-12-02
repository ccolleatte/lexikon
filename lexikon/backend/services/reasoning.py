"""
Ontology Reasoning Service for inferring relations between terms.
Implements reasoning rules: transitive, symmetric, hierarchy, equivalence.
"""

import logging
from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session
from db.postgres import TermRelation, Term

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """Infers semantic relations using reasoning rules."""

    CONFIDENCE_DECAY = 0.9  # Each inference step reduces confidence

    def __init__(self, db: Session):
        self.db = db
        self.reasoning_rules = {
            'transitive': self._apply_transitive_rule,
            'symmetric': self._apply_symmetric_rule,
            'equivalence': self._apply_equivalence_rule,
            'inverse': self._apply_inverse_rule,
        }

    def infer_relations(
        self,
        term_id: str,
        rules: Optional[List[str]] = None,
        max_depth: int = 3,
        confidence_threshold: float = 0.75
    ) -> List[Dict]:
        """
        Infer new relations for a term using specified reasoning rules.

        Args:
            term_id: Source term to infer relations for
            rules: List of rule names to apply (default: all)
            max_depth: Maximum traversal depth (prevents infinite loops)
            confidence_threshold: Minimum confidence to include result

        Returns:
            List of inferred relations with confidence scores
        """
        if rules is None:
            rules = list(self.reasoning_rules.keys())

        inferred = []
        visited = set()

        for rule_name in rules:
            if rule_name in self.reasoning_rules:
                rule_results = self.reasoning_rules[rule_name](
                    term_id, max_depth, confidence_threshold, visited
                )
                inferred.extend(rule_results)

        # Deduplicate and keep highest confidence
        unique_inferred = {}
        for item in inferred:
            key = (item['target_term_id'], item['relation_type'])
            if key not in unique_inferred or item['confidence'] > unique_inferred[key]['confidence']:
                unique_inferred[key] = item

        return sorted(
            unique_inferred.values(),
            key=lambda x: x['confidence'],
            reverse=True
        )

    def _apply_transitive_rule(
        self,
        term_id: str,
        max_depth: int,
        confidence_threshold: float,
        visited: Set[str]
    ) -> List[Dict]:
        """
        Transitive rule: If A → B and B → C, then A → C.
        Works for: broader, narrower, part_of, has_part, related
        """
        inferred = []
        transitive_relations = {'broader', 'narrower', 'part_of', 'has_part', 'related'}

        def traverse(current_id: str, depth: int, accumulated_confidence: float):
            if depth > max_depth or current_id in visited:
                return

            visited.add(current_id)

            # Get direct relations from current term
            relations = self.db.query(TermRelation).filter(
                TermRelation.source_term_id == current_id,
                TermRelation.relation_type.in_(transitive_relations)
            ).all()

            for rel in relations:
                new_confidence = accumulated_confidence * rel.confidence * self.CONFIDENCE_DECAY

                if new_confidence >= confidence_threshold:
                    inferred.append({
                        'source_term_id': term_id,
                        'target_term_id': rel.target_term_id,
                        'relation_type': rel.relation_type,
                        'confidence': round(new_confidence, 3),
                        'rule': 'transitive',
                        'depth': depth
                    })

                # Recursively traverse
                traverse(rel.target_term_id, depth + 1, new_confidence)

        traverse(term_id, 1, 1.0)
        return inferred

    def _apply_symmetric_rule(
        self,
        term_id: str,
        max_depth: int,
        confidence_threshold: float,
        visited: Set[str]
    ) -> List[Dict]:
        """
        Symmetric rule: If A ~ B, then B ~ A.
        Works for: equivalent, related
        """
        inferred = []
        symmetric_relations = {'equivalent', 'related'}

        # Find inverse relations (where this term is the target)
        inverse_relations = self.db.query(TermRelation).filter(
            TermRelation.target_term_id == term_id,
            TermRelation.relation_type.in_(symmetric_relations)
        ).all()

        for rel in inverse_relations:
            if rel.confidence >= confidence_threshold:
                inferred.append({
                    'source_term_id': term_id,
                    'target_term_id': rel.source_term_id,
                    'relation_type': rel.relation_type,
                    'confidence': rel.confidence,
                    'rule': 'symmetric',
                    'depth': 1
                })

        return inferred

    def _apply_equivalence_rule(
        self,
        term_id: str,
        max_depth: int,
        confidence_threshold: float,
        visited: Set[str]
    ) -> List[Dict]:
        """
        Equivalence rule: If A ≡ B and B ≡ C, then A ≡ C.
        Closure over 'equivalent' relations.
        """
        inferred = []

        def find_equivalents(current_id: str, depth: int, accumulated_confidence: float):
            if depth > max_depth or current_id in visited:
                return

            visited.add(current_id)

            # Get equivalent relations
            relations = self.db.query(TermRelation).filter(
                TermRelation.source_term_id == current_id,
                TermRelation.relation_type == 'equivalent'
            ).all()

            for rel in relations:
                new_confidence = accumulated_confidence * rel.confidence * self.CONFIDENCE_DECAY

                if rel.target_term_id != term_id and new_confidence >= confidence_threshold:
                    inferred.append({
                        'source_term_id': term_id,
                        'target_term_id': rel.target_term_id,
                        'relation_type': 'equivalent',
                        'confidence': round(new_confidence, 3),
                        'rule': 'equivalence',
                        'depth': depth
                    })

                # Recursively find equivalents
                find_equivalents(rel.target_term_id, depth + 1, new_confidence)

        find_equivalents(term_id, 1, 1.0)
        return inferred

    def _apply_inverse_rule(
        self,
        term_id: str,
        max_depth: int,
        confidence_threshold: float,
        visited: Set[str]
    ) -> List[Dict]:
        """
        Inverse rule: If A is broader than B, then B is narrower than A.
        Automatically invert directional relations.
        """
        inferred = []
        inverse_mapping = {
            'broader': 'narrower',
            'narrower': 'broader',
            'part_of': 'has_part',
            'has_part': 'part_of'
        }

        # Find inverse relations (where this term is the target)
        inverse_relations = self.db.query(TermRelation).filter(
            TermRelation.target_term_id == term_id
        ).all()

        for rel in inverse_relations:
            if rel.relation_type in inverse_mapping:
                inverse_type = inverse_mapping[rel.relation_type]
                if rel.confidence >= confidence_threshold:
                    inferred.append({
                        'source_term_id': term_id,
                        'target_term_id': rel.source_term_id,
                        'relation_type': inverse_type,
                        'confidence': rel.confidence,
                        'rule': 'inverse',
                        'depth': 1
                    })

        return inferred

    def create_relation(
        self,
        source_term_id: str,
        target_term_id: str,
        relation_type: str,
        confidence: float,
        created_by: str,
        metadata: Optional[str] = None
    ) -> TermRelation:
        """Create a new relation between terms."""
        relation = TermRelation(
            id=f"rel_{source_term_id}_{target_term_id}_{relation_type}",
            source_term_id=source_term_id,
            target_term_id=target_term_id,
            relation_type=relation_type,
            confidence=confidence,
            created_by=created_by,
            metadata=metadata
        )
        self.db.add(relation)
        self.db.commit()
        self.db.refresh(relation)
        return relation

    def get_term_relations(
        self,
        term_id: str,
        direction: str = 'outgoing'  # 'outgoing', 'incoming', 'both'
    ) -> List[TermRelation]:
        """Get direct relations for a term."""
        if direction == 'outgoing':
            return self.db.query(TermRelation).filter(
                TermRelation.source_term_id == term_id
            ).all()
        elif direction == 'incoming':
            return self.db.query(TermRelation).filter(
                TermRelation.target_term_id == term_id
            ).all()
        else:  # both
            outgoing = self.db.query(TermRelation).filter(
                TermRelation.source_term_id == term_id
            ).all()
            incoming = self.db.query(TermRelation).filter(
                TermRelation.target_term_id == term_id
            ).all()
            return outgoing + incoming


# Singleton instance
def get_reasoning_engine(db: Session) -> ReasoningEngine:
    """Factory for creating reasoning engine instances."""
    return ReasoningEngine(db)
