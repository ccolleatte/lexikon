"""
Projects API endpoints with owner verification.
Implements CRUD operations for projects with member management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

from db.postgres import get_db, Project, User, project_members, ProjectRoleEnum
from auth.middleware import get_current_user
from models import ApiResponse

router = APIRouter(prefix="/projects", tags=["projects"])


# Request/Response models
class CreateProjectRequest:
    """Request model for creating a project."""
    def __init__(self, name: str, description: Optional[str] = None, language: str = "fr", primary_domain: Optional[str] = None, is_public: bool = False):
        self.name = name
        self.description = description
        self.language = language
        self.primary_domain = primary_domain
        self.is_public = is_public


class UpdateProjectRequest:
    """Request model for updating a project."""
    def __init__(self, name: Optional[str] = None, description: Optional[str] = None, language: Optional[str] = None, primary_domain: Optional[str] = None, is_public: Optional[bool] = None):
        self.name = name
        self.description = description
        self.language = language
        self.primary_domain = primary_domain
        self.is_public = is_public


class ProjectResponse:
    """Response model for project."""
    def __init__(self, project: Project):
        self.id = project.id
        self.name = project.name
        self.description = project.description
        self.language = project.language
        self.primary_domain = project.primary_domain
        self.is_public = project.is_public
        self.owner_id = project.owner_id
        self.created_at = project.created_at.isoformat()
        self.updated_at = project.updated_at.isoformat()
        self.archived_at = project.archived_at.isoformat() if project.archived_at else None
        self.term_count = len(project.terms) if project.terms else 0
        self.member_count = len(project.members) if project.members else 1  # At least owner


@router.post("", status_code=201)
async def create_project(
    name: str,
    description: Optional[str] = None,
    language: str = "fr",
    primary_domain: Optional[str] = None,
    is_public: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new project."""
    try:
        logger.info(f"Creating project '{name}' for user {current_user.id}")

        if not name or not name.strip():
            return ApiResponse(
                success=False,
                error={
                    "code": "INVALID_INPUT",
                    "message": "Le nom du projet est obligatoire",
                },
            )

        # Create project
        project = Project(
            id=str(uuid.uuid4()),
            name=name.strip(),
            description=description,
            language=language,
            primary_domain=primary_domain,
            is_public=is_public,
            owner_id=current_user.id,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        logger.info(f"Project '{project.id}' created successfully")

        response = ProjectResponse(project)
        return ApiResponse(
            success=True,
            data={
                "id": response.id,
                "name": response.name,
                "description": response.description,
                "language": response.language,
                "primary_domain": response.primary_domain,
                "is_public": response.is_public,
                "owner_id": response.owner_id,
                "created_at": response.created_at,
                "updated_at": response.updated_at,
                "term_count": response.term_count,
                "member_count": response.member_count,
            },
        )

    except Exception as e:
        logger.error(f"Error creating project: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.get("")
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all projects for the current user (owned or member of)."""
    try:
        logger.info(f"Listing projects for user {current_user.id}")

        # Get projects where user is owner or member
        projects = db.query(Project).filter(
            (Project.owner_id == current_user.id) |
            (Project.members.any(User.id == current_user.id))
        ).all()

        response_data = []
        for project in projects:
            resp = ProjectResponse(project)
            response_data.append({
                "id": resp.id,
                "name": resp.name,
                "description": resp.description,
                "language": resp.language,
                "primary_domain": resp.primary_domain,
                "is_public": resp.is_public,
                "owner_id": resp.owner_id,
                "created_at": resp.created_at,
                "updated_at": resp.updated_at,
                "term_count": resp.term_count,
                "member_count": resp.member_count,
                "is_owner": project.owner_id == current_user.id,
            })

        return ApiResponse(
            success=True,
            data=response_data,
            metadata={"total": len(response_data)},
        )

    except Exception as e:
        logger.error(f"Error listing projects: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific project (with ownership/membership verification)."""
    try:
        logger.info(f"Getting project {project_id} for user {current_user.id}")

        # Verify access: owner or member
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")

        is_owner = project.owner_id == current_user.id
        is_member = current_user in project.members

        if not is_owner and not is_member:
            raise HTTPException(status_code=403, detail="Accès refusé")

        resp = ProjectResponse(project)
        return ApiResponse(
            success=True,
            data={
                "id": resp.id,
                "name": resp.name,
                "description": resp.description,
                "language": resp.language,
                "primary_domain": resp.primary_domain,
                "is_public": resp.is_public,
                "owner_id": resp.owner_id,
                "created_at": resp.created_at,
                "updated_at": resp.updated_at,
                "term_count": resp.term_count,
                "member_count": resp.member_count,
                "is_owner": is_owner,
                "role": "owner" if is_owner else "member",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    language: Optional[str] = None,
    primary_domain: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a project (owner only)."""
    try:
        logger.info(f"Updating project {project_id} by user {current_user.id}")

        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")

        # Verify ownership
        if project.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Seul le propriétaire peut modifier le projet")

        # Update fields
        if name is not None and name.strip():
            project.name = name.strip()
        if description is not None:
            project.description = description
        if language is not None:
            project.language = language
        if primary_domain is not None:
            project.primary_domain = primary_domain
        if is_public is not None:
            project.is_public = is_public

        db.commit()
        db.refresh(project)

        logger.info(f"Project '{project_id}' updated successfully")

        resp = ProjectResponse(project)
        return ApiResponse(
            success=True,
            data={
                "id": resp.id,
                "name": resp.name,
                "description": resp.description,
                "language": resp.language,
                "primary_domain": resp.primary_domain,
                "is_public": resp.is_public,
                "created_at": resp.created_at,
                "updated_at": resp.updated_at,
                "term_count": resp.term_count,
                "member_count": resp.member_count,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a project (owner only)."""
    try:
        logger.info(f"Deleting project {project_id} by user {current_user.id}")

        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")

        # Verify ownership
        if project.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Seul le propriétaire peut supprimer le projet")

        db.delete(project)
        db.commit()

        logger.info(f"Project '{project_id}' deleted successfully")

        return ApiResponse(success=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.post("/{project_id}/members")
async def add_project_member(
    project_id: str,
    user_id: str,
    role: str = "viewer",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a member to a project (owner only)."""
    try:
        logger.info(f"Adding member {user_id} to project {project_id} by user {current_user.id}")

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")

        # Verify ownership
        if project.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Seul le propriétaire peut gérer les membres")

        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        # Check if already a member
        if user in project.members:
            return ApiResponse(
                success=False,
                error={
                    "code": "ALREADY_MEMBER",
                    "message": "Cet utilisateur est déjà membre du projet",
                },
            )

        # Add member
        project.members.append(user)
        db.commit()

        logger.info(f"Member {user_id} added to project {project_id}")

        return ApiResponse(
            success=True,
            data={
                "user_id": user.id,
                "email": user.email,
                "role": role,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding member: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.delete("/{project_id}/members/{user_id}", status_code=204)
async def remove_project_member(
    project_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a member from a project (owner only)."""
    try:
        logger.info(f"Removing member {user_id} from project {project_id} by user {current_user.id}")

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")

        # Verify ownership
        if project.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Seul le propriétaire peut gérer les membres")

        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        # Remove member
        if user in project.members:
            project.members.remove(user)
            db.commit()
            logger.info(f"Member {user_id} removed from project {project_id}")

        return ApiResponse(success=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing member: {type(e).__name__}: {str(e)}", exc_info=True)
        raise
