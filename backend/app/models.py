import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# --- Enums ---


class IncidentStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class IncidentPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentCategory(str, Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    QUESTION = "question"
    DOCUMENTATION = "documentation"


# --- User models ---


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    incidents: list["Incident"] = Relationship(
        back_populates="owner",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[Incident.owner_id]"},
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# --- Incident models ---


# Shared properties
class IncidentBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    status: IncidentStatus = Field(default=IncidentStatus.OPEN)
    priority: IncidentPriority = Field(default=IncidentPriority.MEDIUM)
    category: IncidentCategory = Field(default=IncidentCategory.BUG)


# Properties to receive on incident creation
class IncidentCreate(IncidentBase):
    assignee_id: uuid.UUID | None = None


# Properties to receive on incident update
class IncidentUpdate(IncidentBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    status: IncidentStatus | None = None  # type: ignore
    priority: IncidentPriority | None = None  # type: ignore
    category: IncidentCategory | None = None  # type: ignore
    assignee_id: uuid.UUID | None = None


# Database model, database table inferred from class name
class Incident(IncidentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(
        back_populates="incidents",
        sa_relationship_kwargs={"foreign_keys": "[Incident.owner_id]"},
    )
    assignee_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", nullable=True, ondelete="SET NULL"
    )
    assignee: User | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Incident.assignee_id]"},
    )
    resolved_at: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True),  # type: ignore
    )
    comments: list["Comment"] = Relationship(
        back_populates="incident", cascade_delete=True
    )


# Properties to return via API, id is always required
class IncidentPublic(IncidentBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    assignee_id: uuid.UUID | None = None
    created_at: datetime | None = None
    resolved_at: datetime | None = None


class IncidentsPublic(SQLModel):
    data: list[IncidentPublic]
    count: int


# --- Comment models ---


class CommentBase(SQLModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    author_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    incident_id: uuid.UUID = Field(
        foreign_key="incident.id", nullable=False, ondelete="CASCADE"
    )
    author: User | None = Relationship()
    incident: Incident | None = Relationship(back_populates="comments")


class CommentPublic(CommentBase):
    id: uuid.UUID
    author_id: uuid.UUID
    incident_id: uuid.UUID
    created_at: datetime | None = None


class CommentsPublic(SQLModel):
    data: list[CommentPublic]
    count: int


# --- Generic models ---


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
