import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_redirect_root():
    """Test that the root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test retrieving the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that we have the expected activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert "Art Club" in data
    
    # Check the structure of an activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    response = client.post("/activities/Art Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up test@mergington.edu for Art Club"
    
    # Verify the student was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Art Club"]["participants"]

def test_signup_duplicate():
    """Test that signing up twice fails"""
    # First signup should succeed
    response = client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/Fake Club/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"