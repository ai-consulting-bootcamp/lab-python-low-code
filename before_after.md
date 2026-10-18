# Before / After — Meal Planner Refactoring

| Concern | Starter | Refactored |
|---|---|---|
| API failures | `.invoke()` outside `try` | API invocation inside guarded `generate()` |
| JSON parsing | Inline fence stripping and `json.loads` | `parse_json_response()` testable separately |
| Schema validation | Inline Pydantic construction | `validate_response()` with field-specific `ValidationError` |
| Error result | Failure omits `generation_time` | Consistent success/failure keys |
| Email credentials | Placeholder literals in notebook | Environment variables and `.env.example` |
| Email plan | Regenerates on Email button | Gradio `State` stores the displayed plan |
| Email responsibilities | Compose and send in one function | `build_email_message()` and `send_meal_plan_email()` |
| Ingredients | Repeated text formatting | `format_ingredients()` shared |
| Basic validation | Duplicate magic numbers | Reuses `MealPlan` Pydantic rules |
| Tests | Test loop makes real model calls | Offline assertions, optional clearly marked live test |

## Prioritized problems
1. Never expose live credentials in notebook or outputs.
2. Protect external API calls and return actionable diagnostics.
3. Ensure email delivers the displayed plan.

## Scope and limitations
- Static Python syntax checks completed; Pydantic validated a synthetic seven-recipe plan and rejected a six-recipe plan.
- Full notebook execution, OpenAI calls, SMTP delivery and screenshots **have not been verified** here.
- The refactored parser accepts raw JSON or a complete fenced JSON block, but not arbitrary prose surrounding JSON.
- Pydantic checks structure and counts, not nutritional truth, dietary safety, or shopping-list quantity correctness.
- Live checks should be completed in the student's environment before submission.
