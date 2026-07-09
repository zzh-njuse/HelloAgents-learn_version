import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from learn_agent_api.db.models import Workspace
from learn_agent_api.schemas.workspace import WorkspaceCreate


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "workspace"


def list_workspaces(db: Session, skip: int = 0, limit: int = 100) -> list[Workspace]:
    result = db.execute(select(Workspace).order_by(Workspace.created_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all())


def get_workspace(db: Session, workspace_id: str) -> Workspace | None:
    return db.get(Workspace, workspace_id)


def create_workspace(db: Session, payload: WorkspaceCreate) -> Workspace:
    base_slug = slugify(payload.slug or payload.name)
    slug = base_slug
    suffix = 2

    while db.execute(select(Workspace.id).where(Workspace.slug == slug)).scalar_one_or_none():
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    workspace = Workspace(
        name=payload.name.strip(),
        slug=slug,
        description=payload.description.strip() if payload.description else None,
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace
