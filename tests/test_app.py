import pytest

from app import create_app
from app.models import Artisan, db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client


def csrf_token(client):
    response = client.get("/")
    html = response.get_data(as_text=True)
    marker = 'name="csrf_token" value="'
    return html.split(marker, 1)[1].split('"', 1)[0]


def test_index_is_available(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ANYAMA" in response.data
    assert response.headers["X-Frame-Options"] == "DENY"


def test_artisan_submission_persists(client):
    response = client.post("/artisans", data={
        "csrf_token": csrf_token(client),
        "name": "Awa Kouassi",
        "job": "Couturière",
        "neighborhood": "Anyama Centre",
        "phone": "07 00 00 00 00",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Awa Kouassi" in response.data
    with client.application.app_context():
        assert Artisan.query.filter_by(name="Awa Kouassi").count() == 1


def test_invalid_submission_is_rejected(client):
    response = client.post("/artisans", data={
        "csrf_token": csrf_token(client),
        "name": "<script>alert(1)</script>",
        "job": "x",
        "neighborhood": "x",
        "phone": "abc",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"<script>alert(1)</script>" not in response.data
    with client.application.app_context():
        assert Artisan.query.count() == 0


def test_honeypot_does_not_create_record(client):
    response = client.post("/artisans", data={
        "csrf_token": csrf_token(client), "website": "bot", "name": "Bot User",
        "job": "Test", "neighborhood": "Anyama", "phone": "0700000000",
    })
    assert response.status_code == 302
    with client.application.app_context():
        assert Artisan.query.count() == 0
