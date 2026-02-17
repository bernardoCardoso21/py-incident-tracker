import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.incident import create_random_incident
from tests.utils.comment import create_random_comment


def test_create_comment(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    data = {"content": "This is a test comment"}
    response = client.post(
        f"{settings.API_V1_STR}/incidents/{incident.id}/comments/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["content"] == data["content"]
    assert content["incident_id"] == str(incident.id)
    assert "id" in content
    assert "author_id" in content
    assert "created_at" in content


def test_read_comments(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    create_random_comment(db, incident_id=incident.id, author_id=incident.owner_id)
    create_random_comment(db, incident_id=incident.id, author_id=incident.owner_id)
    response = client.get(
        f"{settings.API_V1_STR}/incidents/{incident.id}/comments/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
    assert len(content["data"]) >= 2


def test_delete_comment(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    comment = create_random_comment(
        db, incident_id=incident.id, author_id=incident.owner_id
    )
    response = client.delete(
        f"{settings.API_V1_STR}/incidents/{incident.id}/comments/{comment.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Comment deleted successfully"


def test_delete_comment_not_found(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    response = client.delete(
        f"{settings.API_V1_STR}/incidents/{incident.id}/comments/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Comment not found"


def test_create_comment_incident_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"content": "Comment on non-existent incident"}
    response = client.post(
        f"{settings.API_V1_STR}/incidents/{uuid.uuid4()}/comments/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Incident not found"


def test_create_comment_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    incident = create_random_incident(db)
    data = {"content": "Unauthorized comment"}
    response = client.post(
        f"{settings.API_V1_STR}/incidents/{incident.id}/comments/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
