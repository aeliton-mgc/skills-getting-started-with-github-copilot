import importlib

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client():
    # Arrange: reset in-memory app state before each test
    importlib.reload(app_module)
    return TestClient(app_module.app)


def test_get_activities_returns_activities(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"

    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity(client):
    # Arrange
    email = "daniel@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity}"

    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_remove_missing_participant_returns_404(client):
    # Arrange
    email = "absent@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
