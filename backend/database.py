"""
Simple in-memory database for Sprint 1 MVP.
Replace with PostgreSQL + Neo4j in Sprint 2.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid


# In-memory storage
onboarding_sessions: Dict[str, dict] = {}
users: Dict[str, dict] = {}
terms: Dict[str, dict] = {}


def create_onboarding_session(session_id: str, adoption_level: str) -> dict:
    """Store onboarding session"""
    session = {
        "sessionId": session_id,
        "adoptionLevel": adoption_level,
        "createdAt": datetime.now().isoformat(),
    }
    onboarding_sessions[session_id] = session
    return session


def get_onboarding_session(session_id: str) -> Optional[dict]:
    """Get onboarding session"""
    return onboarding_sessions.get(session_id)


def create_user(user_data: dict) -> dict:
    """Create a new user"""
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        **user_data,
    }
    users[user_id] = user
    return user


def get_user_by_email(email: str) -> Optional[dict]:
    """Find user by email"""
    for user in users.values():
        if user["email"] == email:
            return user
    return None


def create_term(term_data: dict, user_id: str) -> dict:
    """Create a new term"""
    term_id = str(uuid.uuid4())
    term = {
        "id": term_id,
        "createdBy": user_id,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        **term_data,
    }
    terms[term_id] = term
    return term


def get_terms_by_user(user_id: str) -> List[dict]:
    """Get all terms for a user"""
    return [term for term in terms.values() if term["createdBy"] == user_id]


def get_term_by_name_and_user(name: str, user_id: str) -> Optional[dict]:
    """Check if term with this name already exists for user"""
    for term in terms.values():
        if term["createdBy"] == user_id and term["name"].lower() == name.lower():
            return term
    return None
