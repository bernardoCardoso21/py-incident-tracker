import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.incident import create_random_incident


def test_create_incident(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/incidents/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_incident(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    response = client.get(
        f"{settings.API_V1_STR}/incidents/{incident.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == incident.title
    assert content["description"] == incident.description
    assert content["id"] == str(incident.id)
    assert content["owner_id"] == str(incident.owner_id)


def test_read_incident_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/incidents/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Incident not found"


def test_read_incident_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    response = client.get(
        f"{settings.API_V1_STR}/incidents/{incident.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_incidents(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_incident(db)
    create_random_incident(db)
    response = client.get(
        f"{settings.API_V1_STR}/incidents/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_incident(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/incidents/{incident.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(incident.id)
    assert content["owner_id"] == str(incident.owner_id)


def test_update_incident_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/incidents/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Incident not found"


def test_update_incident_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/incidents/{incident.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_incident(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    response = client.delete(
        f"{settings.API_V1_STR}/incidents/{incident.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Incident deleted successfully"


def test_delete_incident_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/incidents/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Incident not found"


def test_delete_incident_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    response = client.delete(
        f"{settings.API_V1_STR}/incidents/{incident.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
