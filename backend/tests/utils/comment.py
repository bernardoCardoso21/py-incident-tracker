import uuid

from sqlmodel import Session

from app.models import Comment
from tests.utils.utils import random_lower_string


def create_random_comment(
    db: Session, incident_id: uuid.UUID, author_id: uuid.UUID
) -> Comment:
    content = random_lower_string()
    comment = Comment(content=content, incident_id=incident_id, author_id=author_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
