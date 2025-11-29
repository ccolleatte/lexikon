"""
Vocabulary Extraction Service - Extract terms from documents using multiple patterns.
Supports parentheses, bold, glossary, and inline patterns.
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractedTerm:
    """Represents an extracted term with metadata."""
    text: str
    definition: Optional[str] = None
    pattern: str = "unknown"
    confidence: float = 0.8


class VocabularyExtractor:
    """Extract terms from documents using multiple patterns."""

    def __init__(self):
        self.patterns = {
            'parentheses': self._extract_parentheses,
            'bold': self._extract_bold,
            'glossary': self._extract_glossary_lines,
            'inline_definition': self._extract_inline_definitions
        }

    def extract_terms(
        self,
        text: str,
        patterns: Optional[List[str]] = None,
        language: str = "fr"
    ) -> List[ExtractedTerm]:
        """
        Extract terms from text using specified patterns.

        Args:
            text: Document text to process
            patterns: List of pattern names to apply (default: all)
            language: Language for stopword filtering (fr/en)

        Returns:
            List of extracted terms with confidence scores
        """
        if patterns is None:
            patterns = list(self.patterns.keys())

        extracted = []
        seen = set()

        for pattern_name in patterns:
            if pattern_name in self.patterns:
                terms = self.patterns[pattern_name](text, language)
                for term in terms:
                    # Avoid duplicates, keep highest confidence
                    if term.text.lower() not in seen or \
                       any(t.text.lower() == term.text.lower() and t.confidence < term.confidence for t in extracted):
                        extracted.append(term)
                        seen.add(term.text.lower())

        # Sort by confidence descending
        return sorted(extracted, key=lambda x: x.confidence, reverse=True)

    def _extract_parentheses(self, text: str, language: str) -> List[ExtractedTerm]:
        """
        Extract terms defined in parentheses.
        Pattern: "Term Name (definition text here)"
        """
        terms = []
        # Pattern: word followed by parenthetical definition
        pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([^)]+)\)'

        matches = re.finditer(pattern, text)
        for match in matches:
            term_text = match.group(1).strip()
            definition = match.group(2).strip()

            if term_text and definition and len(definition) > 10:
                terms.append(ExtractedTerm(
                    text=term_text,
                    definition=definition,
                    pattern='parentheses',
                    confidence=0.9
                ))

        logger.debug(f"Extracted {len(terms)} terms from parentheses")
        return terms

    def _extract_bold(self, text: str, language: str) -> List[ExtractedTerm]:
        """
        Extract bold/emphasized terms.
        Patterns: **text**, __text__, ***text***
        """
        terms = []

        # Markdown bold: **text**
        for match in re.finditer(r'\*\*([^*]+)\*\*', text):
            term_text = match.group(1).strip()
            if term_text and len(term_text) > 2:
                terms.append(ExtractedTerm(
                    text=term_text,
                    pattern='bold_markdown',
                    confidence=0.7
                ))

        # HTML bold: <b>text</b>, <strong>text</strong>
        for match in re.finditer(r'<(?:b|strong)>([^<]+)</(?:b|strong)>', text):
            term_text = match.group(1).strip()
            if term_text:
                terms.append(ExtractedTerm(
                    text=term_text,
                    pattern='bold_html',
                    confidence=0.7
                ))

        logger.debug(f"Extracted {len(terms)} bold terms")
        return terms

    def _extract_glossary_lines(self, text: str, language: str) -> List[ExtractedTerm]:
        """
        Extract from glossary-style lines.
        Pattern: "Term: definition" or "Term - definition"
        """
        terms = []
        lines = text.split('\n')

        for line in lines:
            if ':' in line or ' - ' in line:
                # Split on separator
                if ':' in line:
                    parts = line.split(':', 1)
                else:
                    parts = line.split(' - ', 1)

                if len(parts) == 2:
                    term_text = parts[0].strip()
                    definition = parts[1].strip()

                    # Basic validation
                    if term_text and definition and \
                       2 < len(term_text) < 100 and \
                       len(definition) > 5:
                        terms.append(ExtractedTerm(
                            text=term_text,
                            definition=definition,
                            pattern='glossary_line',
                            confidence=0.8
                        ))

        logger.debug(f"Extracted {len(terms)} glossary-style terms")
        return terms

    def _extract_inline_definitions(self, text: str, language: str) -> List[ExtractedTerm]:
        """
        Extract terms with inline definitions.
        Pattern: "... le Term est... " or "... the Term is..."
        """
        terms = []

        # French pattern: "le/la/les TERM est/sont"
        fr_pattern = r'(?:le|la|les)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:est|sont|'
        fr_pattern += r'peut être|signifie)'

        for match in re.finditer(fr_pattern, text):
            term_text = match.group(1).strip()
            if term_text and 2 < len(term_text) < 100:
                terms.append(ExtractedTerm(
                    text=term_text,
                    pattern='inline_fr',
                    confidence=0.6
                ))

        logger.debug(f"Extracted {len(terms)} inline-definition terms")
        return terms


# Singleton
vocabulary_extractor = VocabularyExtractor()
