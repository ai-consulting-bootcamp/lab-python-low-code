Refactoring Checklist: Starter Code Analysis
Issues Found:
[ ] Hardcoded Secrets: EMAIL_SENDER and EMAIL_PASSWORD are hardcoded directly into the configuration cell. If this file is pushed to GitHub, those credentials are leaked.
[ ] Monolithic Function: MealPlanGenerator.generate() does too much. It builds the prompt, calls the OpenAI API, cleans the markdown formatting, parses the JSON, and validates the Pydantic model.
[ ] Fragile Parsing Logic: The code-fence stripping in generate() (content.split("```json")[1]...) assumes the model will always reply with perfectly formatted markdown blocks. If the LLM omits the fence or adds conversational text, this breaks.
[ ] Silent/Broad Failures: The generate() and send_meal_plan_email() functions rely on a catch-all except Exception as e:. If the OpenAI API rate-limits you, or if Pydantic throws a ValidationError because a recipe is missing a field, it is swallowed into a generic error string. You will know it failed, but not where or why.
[ ] Repeated Code: The exact logic to turn an ingredient list into a string (", ".join([f"{ing['quantity']} {ing['name']}" for ing in recipe['ingredients']])) is copy-pasted in both format_meal_plan_email() and format_single_recipe().
[ ] Duplicated Validation: run_basic_validation() manually checks for 7 recipes and 5 ingredients. The Pydantic models (MealPlan and Recipe) already enforce these exact rules.
Priority:
Stop the Silent Failures: Replace the broad except blocks with specific catches (ValidationError, OpenAIError) that print the exact location and reason for the failure.
Extract Helpers: Pull the repeated ingredient-formatting logic and the fragile markdown-stripping logic out into their own isolated, testable helper functions.
Modularize generate(): Break the monolithic generation method into single-responsibility steps (e.g., call_llm(), parse_response(), validate_plan()).

I refactored the meal planner according to Path 1 by separating prompt construction, API calls, response parsing, validation, formatting, and email delivery into focused helper functions. I also replaced broad exception handling with specific, actionable errors that identify the function, context, and suggested fix. The main challenge was making LLM response parsing reliable when the response was not perfectly formatted. Key learning outcomes were understanding how single-responsibility functions improve maintainability and learning how structured validation and contextual error messages make failures easier to diagnose and test.
