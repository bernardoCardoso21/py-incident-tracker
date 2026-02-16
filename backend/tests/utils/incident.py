from sqlmodel import Session

from app import crud
from app.models import Incident, IncidentCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_incident(db: Session) -> Incident:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    incident_in = IncidentCreate(title=title, description=description)
    return crud.create_incident(session=db, incident_in=incident_in, owner_id=owner_id)
