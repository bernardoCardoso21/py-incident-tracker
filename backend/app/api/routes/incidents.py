import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Incident, IncidentCreate, IncidentPublic, IncidentsPublic, IncidentStatus, IncidentUpdate, Message

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("/", response_model=IncidentsPublic)
def read_incidents(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve incidents.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Incident)
        count = session.exec(count_statement).one()
        statement = (
            select(Incident).order_by(col(Incident.created_at).desc()).offset(skip).limit(limit)
        )
        incidents = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Incident)
            .where(Incident.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Incident)
            .where(Incident.owner_id == current_user.id)
            .order_by(col(Incident.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        incidents = session.exec(statement).all()

    return IncidentsPublic(data=incidents, count=count)


@router.get("/{id}", response_model=IncidentPublic)
def read_incident(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get incident by ID.
    """
    incident = session.get(Incident, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not current_user.is_superuser and (incident.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return incident


@router.post("/", response_model=IncidentPublic)
def create_incident(
    *, session: SessionDep, current_user: CurrentUser, incident_in: IncidentCreate
) -> Any:
    """
    Create new incident.
    """
    incident = Incident.model_validate(incident_in, update={"owner_id": current_user.id})
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident


@router.put("/{id}", response_model=IncidentPublic)
def update_incident(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    incident_in: IncidentUpdate,
) -> Any:
    """
    Update an incident.
    """
    incident = session.get(Incident, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not current_user.is_superuser and (incident.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = incident_in.model_dump(exclude_unset=True)
    incident.sqlmodel_update(update_dict)
    # Auto-set resolved_at when status changes to RESOLVED
    if "status" in update_dict:
        if update_dict["status"] == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now(timezone.utc)
        else:
            incident.resolved_at = None
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident


@router.delete("/{id}")
def delete_incident(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an incident.
    """
    incident = session.get(Incident, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not current_user.is_superuser and (incident.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(incident)
    session.commit()
    return Message(message="Incident deleted successfully")
