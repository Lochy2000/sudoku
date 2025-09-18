from __future__ import annotations

from typing import Any

from rest_framework import serializers

from puzzle.models import PuzzleTemplate


class PuzzleListQuerySerializer(serializers.Serializer):
    size = serializers.IntegerField(min_value=1, required=False, default=9)
    difficulty = serializers.ChoiceField(
        choices=[
            PuzzleTemplate.DIFFICULTY_EASY,
            PuzzleTemplate.DIFFICULTY_MEDIUM,
            PuzzleTemplate.DIFFICULTY_HARD,
            PuzzleTemplate.DIFFICULTY_EXPERT,
        ],
        required=False,
        default=PuzzleTemplate.DIFFICULTY_MEDIUM,
    )


class GameCreateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField(min_value=1)


class PencilMarksField(serializers.DictField):
    def to_internal_value(self, data: Any) -> dict[str, list[int]]:
        value = super().to_internal_value(data)
        # Normalize keys to str
        normalized: dict[str, list[int]] = {}
        for k, v in value.items():
            normalized[str(k)] = [int(x) for x in v]
        return normalized


class GameUpdateSerializer(serializers.Serializer):
    board_state = serializers.CharField(required=False, allow_blank=False)
    pencil_marks = PencilMarksField(
        child=serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=True),
        required=False,
    )
    time_seconds = serializers.IntegerField(min_value=0, required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # Expect context to provide puzzle size if board_state provided
        board_state = attrs.get("board_state")
        if board_state is not None:
            size = self.context.get("size")
            if not isinstance(size, int) or size <= 0:
                raise serializers.ValidationError("Internal error: missing size for validation")
            expected = size * size
            if len(board_state) != expected:
                raise serializers.ValidationError(
                    {"board_state": f"Expected length {expected} for size {size}"}
                )
        # Optional: validate pencil mark values are within range if size provided
        if "pencil_marks" in attrs and "size" in self.context:
            size = int(self.context["size"])  # type: ignore[arg-type]
            for key, marks in attrs["pencil_marks"].items():
                for m in marks:
                    if m < 1 or m > size:
                        raise serializers.ValidationError(
                            {"pencil_marks": f"Mark {m} out of range 1..{size} at cell {key}"}
                        )
        return attrs


