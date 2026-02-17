import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Comment, CommentCreate, CommentPublic, CommentsPublic, Incident, Message

router = APIRouter(prefix="/incidents/{incident_id}/comments", tags=["comments"])


def _get_incident_or_404(
    session: SessionDep, current_user: CurrentUser, incident_id: uuid.UUID
) -> Incident:
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not current_user.is_superuser and (incident.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return incident


@router.get("/", response_model=CommentsPublic)
def read_comments(
    session: SessionDep,
    current_user: CurrentUser,
    incident_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    _get_incident_or_404(session, current_user, incident_id)
    count_statement = (
        select(func.count())
        .select_from(Comment)
        .where(Comment.incident_id == incident_id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Comment)
        .where(Comment.incident_id == incident_id)
        .order_by(col(Comment.created_at).asc())
        .offset(skip)
        .limit(limit)
    )
    comments = session.exec(statement).all()
    return CommentsPublic(data=comments, count=count)


@router.post("/", response_model=CommentPublic)
def create_comment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    incident_id: uuid.UUID,
    comment_in: CommentCreate,
) -> Any:
    _get_incident_or_404(session, current_user, incident_id)
    comment = Comment.model_validate(
        comment_in,
        update={"author_id": current_user.id, "incident_id": incident_id},
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@router.delete("/{comment_id}")
def delete_comment(
    session: SessionDep,
    current_user: CurrentUser,
    incident_id: uuid.UUID,
    comment_id: uuid.UUID,
) -> Message:
    _get_incident_or_404(session, current_user, incident_id)
    comment = session.get(Comment, comment_id)
    if not comment or comment.incident_id != incident_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not current_user.is_superuser and (comment.author_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(comment)
    session.commit()
    return Message(message="Comment deleted successfully")
