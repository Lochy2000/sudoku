# Resources for Sudoku Django App

This file lists useful **libraries, tutorials, papers, and references** to guide the development of the Sudoku project.  
They are grouped by **libraries/codebases**, **theory & difficulty research**, and **tutorials & blog posts**.

---

## 🔧 Libraries & Codebases

### [Dokusan](https://github.com/unmade/dokusan)
- Python Sudoku generator & solver.
- Provides **difficulty ranking** (`avg_rank`) and **step-based techniques** (e.g., hidden singles, XY-Wing).
- Great for **9×9 puzzles** and difficulty calibration.

### [Sudoku-DLX](https://github.com/ShivanKaul/Sudoku-DLX)
- Implements **Dancing Links (DLX)** / Algorithm X solver for Sudoku.
- Supports uniqueness checks and generalized Sudoku grids.
- Useful for **validating puzzles** and supporting smaller grids (4×4, 6×6).

### [Algorithm X / DLX Explanation (Josh Berry’s blog)](https://taeric.github.io/Sudoku.html)
- Walks through **exact cover problem** and how Sudoku can be solved with DLX.
- Excellent for understanding **solver internals**.

### [py-sudoku](https://pypi.org/project/py-sudoku/)
- Python library with **m×n Sudoku** support.
- Can help for smaller grids (4×4, 6×6).

---

## 📚 Theory & Difficulty Research

### [What Makes Sudoku Easy, Medium, or Hard?](https://www.sudokulovers.com/what-makes-Sudoku-easy-medium-or-hard)
- Informal breakdown of how **techniques used** correlate to perceived difficulty.
- Useful for mapping your engine’s metrics to **user-facing labels**.

### [Conceptis: Sudoku Difficulty Levels Explained](https://www.conceptispuzzles.com/index.aspx?uri=info%2Farticle%2F2)
- Explains why **number of givens ≠ difficulty**.
- Describes how **logic decision complexity** defines puzzle difficulty.

### [Project Patti: Difficulty Comparisons Across Websites (arXiv)](https://arxiv.org/abs/2507.21137)
- Research paper comparing how different Sudoku sites define “easy” vs “hard.”
- Good for calibrating your own **difficulty thresholds**.

### [The Chaos Within Sudoku (arXiv)](https://arxiv.org/abs/1208.0370)
- Proposes a **hardness metric** based on chaotic dynamics.
- Advanced reading, but shows how difficulty can be quantified mathematically.

---

## 📝 Tutorials & Blog Posts

### [StackOverflow: Dancing Links (DLX) Algorithm Explained](https://stackoverflow.com/questions/1518335/the-dancing-links-algorithm-an-explanation-that-is-less-explanatory-but-more-o)
- Q&A style breakdown of DLX with **code insights**.
- Helpful for implementing uniqueness checks.

### [An Incomplete Review of Sudoku Solver Implementations](https://attractivechaos.wordpress.com/2011/06/19/an-incomplete-review-of-sudoku-solver-implementations/)
- Benchmarks and compares solving strategies (backtracking, DLX, optimizations).
- Good for understanding **performance trade-offs**.

### [Wikipedia: Dancing Links](https://en.wikipedia.org/wiki/Dancing_Links)
- Background on Knuth’s Algorithm X and **exact cover problems**.
- Useful as a reference when building custom solvers.

---

## ✅ How to Use These Resources

| Project Component | Recommended Resource(s) | Why |
|-------------------|--------------------------|-----|
| **9×9 Puzzle Generation & Difficulty** | Dokusan | Simple, production-ready generator with difficulty metrics. |
| **Uniqueness Checking & Solving** | Sudoku-DLX, Algorithm X tutorials | Ensure puzzles have exactly one solution. |
| **Smaller Grids (4×4, 6×6)** | py-sudoku, DLX | Handle non-standard Sudoku sizes. |
| **Difficulty Mapping** | Sudoku Lovers, Conceptis | Translate raw metrics into user-friendly labels. |
| **Advanced Difficulty Calibration** | Project Patti, Chaos Within Sudoku | Research-level insights for scaling difficulty systems. |
| **Performance Optimization** | Solver review blog, DLX references | Choose efficient solving strategies as load grows. |

---

## 📌 Next Steps

- For **MVP**: Start with **Dokusan** (9×9) + DLX (uniqueness check).  
- For **Smaller Grids**: Test **py-sudoku**, fall back to custom DLX-based generation.  
- For **Difficulty Calibration**: Use `avg_rank` thresholds from Dokusan; refine with **Conceptis/Sudoku Lovers** guidelines.  
- For **Scaling/Research**: Explore **Project Patti** & **Chaos Within Sudoku** for tuning your difficulty engine.

---
