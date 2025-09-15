from django.test import TestCase

from .models import DailyChallenge, GameSession, PuzzleTemplate


class ModelsSmokeTest(TestCase):
    def setUp(self) -> None:
        self.template = PuzzleTemplate.objects.create(
            size=9,
            box_h=3,
            box_w=3,
            givens="0" * 81,
            solution="1" * 81,
            difficulty_metric=1.0,
            difficulty_label=PuzzleTemplate.DIFFICULTY_EASY,
            source="test-engine",
        )

    def test_create_game_session_and_daily_challenge(self) -> None:
        game = GameSession.objects.create(
            user=None,
            puzzle=self.template,
            board_state="0" * 81,
            pencil_marks={},
            mistakes_count=0,
            time_seconds=0,
        )
        self.assertIsNotNone(game.id)
        self.assertEqual(game.puzzle_id, self.template.id)

        dc = DailyChallenge.objects.create(date="2025-09-15", puzzle=self.template)
        self.assertIsNotNone(dc.id)
        self.assertEqual(str(dc.date), "2025-09-15")
