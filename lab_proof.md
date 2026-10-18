# Lab Proof – Meal Planner Refactoring (Path 2)

- **Original:** `meal_planner_starter.ipynb`
- **Refactored:** `meal_planner_refactored.ipynb`
- **Analysis (16 issues, priorities, before/after):** `refactoring_notes.md`
- **Summary:** `lab_summary.md`

## Evidence
| Test | Before | After |
|---|---|---|
| Valid input | Plan generated, all checks passed | Same result |
| Missing .env | `TypeError: str expected, not NoneType` (one cell later) | `[config] OPENAI_API_KEY not found…` |
| API/network error | Uncaught crash | `[generate] <ErrorType>: … Check your API key…` |
| Email password | Typed in notebook | Read from `.env` |

Screenshots: `screenshots/`

