from typing import Any

from django.contrib.auth.models import User
from django.test import Client

from puzzle.models import PuzzleTemplate


def login_staff(client: Client) -> None:
    User.objects.create_superuser(username="admin", password="pass", email="a@b.c")
    client.login(username="admin", password="pass")


def test_admin_validate_and_export(db: Any) -> None:
    client = Client()
    login_staff(client)

    t = PuzzleTemplate.objects.create(
        size=9,
        box_h=3,
        box_w=3,
        givens=("0" * 81),
        solution=("1" * 81),
        difficulty_metric=0.3,
        difficulty_label="easy",
        source="test",
    )

    # Access change list
    resp = client.get("/admin/puzzle/puzzletemplate/")
    assert resp.status_code == 200

    # Export selected (simulate by calling action endpoint)
    resp = client.post(
        "/admin/puzzle/puzzletemplate/",
        {"action": "export_selected_json", "_selected_action": [str(t.id)]},
    )
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/json"


def test_admin_queue_import_and_summary(db: Any) -> None:
    client = Client()
    login_staff(client)

    # GET queue page
    resp = client.get("/admin/puzzle/puzzletemplate/queue/")
    assert resp.status_code == 200

    # POST import JSON
    payload = [
        {
            "size": 4,
            "box_h": 2,
            "box_w": 2,
            "givens": "0" * 16,
            "solution": "1" * 16,
            "difficulty_metric": 0.2,
            "difficulty_label": "easy",
            "source": "import-test",
        }
    ]
    resp = client.post(
        "/admin/puzzle/puzzletemplate/queue/",
        {"json": __import__("json").dumps(payload)},
        follow=True,
    )
    assert resp.status_code == 200
    assert PuzzleTemplate.objects.filter(size=4, difficulty_label="easy").exists()
