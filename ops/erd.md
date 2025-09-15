# ERD (text)

Entities:

- PuzzleTemplate
  - id (PK)
  - size (int)
  - box_h (int)
  - box_w (int)
  - givens (text) — 1D string length size*size, '0' = empty
  - solution (text) — 1D string length size*size, values 1..size
  - difficulty_metric (float)
  - difficulty_label (easy|medium|hard|expert)
  - source (str)
  - created_at (datetime)
  - IDX(size, difficulty_label)

- GameSession
  - id (PK)
  - user_id (FK -> auth_user, nullable)
  - puzzle_id (FK -> PuzzleTemplate)
  - board_state (json) — 1D string or structured JSON
  - pencil_marks (json) — {cell_index: [ints...]}
  - mistakes_count (int)
  - time_seconds (int)
  - status (in_progress|completed|abandoned)
  - started_at (datetime)
  - updated_at (datetime)
  - completed_at (datetime, null)

- DailyChallenge
  - date (date, unique)
  - puzzle_id (FK -> PuzzleTemplate)
  - created_at (datetime)

Relationships:

- PuzzleTemplate 1 — N GameSession
- PuzzleTemplate 1 — 1 DailyChallenge (per date)
