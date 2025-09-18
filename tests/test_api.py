from typing import Any

from django.test import Client

from puzzle.models import DailyChallenge, PuzzleTemplate


def test_api_puzzles_and_games_flow(db: Any) -> None:
    client = Client()

    # Ensure at least one template exists
    if PuzzleTemplate.objects.count() == 0:
        PuzzleTemplate.objects.create(
            size=9,
            box_h=3,
            box_w=3,
            givens=("0" * 81),
            solution=("1" * 81),
            difficulty_metric=0.5,
            difficulty_label="medium",
            source="test",
        )

    # GET puzzle
    resp = client.get("/api/puzzles/?size=9&difficulty=medium")
    assert resp.status_code == 200
    puzzle = resp.json()
    assert puzzle["size"] == 9
    template_id = puzzle["id"]

    # Create game
    resp = client.post("/api/games/", {"template_id": template_id})
    assert resp.status_code == 200
    game = resp.json()
    game_id = game["id"]

    # Fetch game
    resp = client.get(f"/api/games/{game_id}/")
    assert resp.status_code == 200
    assert resp.json()["id"] == game_id

    # Update game (save progress)
    resp = client.put(
        f"/api/games/{game_id}/",
        data={"board_state": "1" * 81, "time_seconds": 15},
        content_type="application/json",
    )
    assert resp.status_code == 200

    # Check validation
    resp = client.post(f"/api/games/{game_id}/check/")
    assert resp.status_code == 200
    assert isinstance(resp.json().get("solved"), bool)


def test_api_daily_endpoint(db: Any) -> None:
    client = Client()

    # Seed a daily challenge
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
    DailyChallenge.objects.create(date="2025-09-17", puzzle=t)

    resp = client.get("/api/daily/2025-09-17")
    assert resp.status_code == 200
    data = resp.json()
    assert data["date"] == "2025-09-17"
    assert data["puzzle"]["id"] == t.id
