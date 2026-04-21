def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert {"description", "schedule", "max_participants", "participants"}.issubset(
        data["Chess Club"].keys()
    )


def test_signup_adds_participant(client):
    email = "new.student@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400(client):
    email = "duplicate.student@mergington.edu"
    client.post("/activities/Art Club/signup", params={"email": email})

    response = client.post("/activities/Art Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "test@example.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    email = "remove.me@mergington.edu"
    client.post("/activities/Science Club/signup", params={"email": email})

    response = client.delete("/activities/Science Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Science Club"

    activities = client.get("/activities").json()
    assert email not in activities["Science Club"]["participants"]


def test_unregister_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Debate Team/signup", params={"email": "missing@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
