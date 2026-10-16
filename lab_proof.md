## Workflow

**Input:** The user selects a diet and can add cuisine themes and ingredient preferences.

**Transformation:** The application asks the AI to create a weekly meal plan. It cleans the response, reads the JSON, and validates the required fields, recipe count, ingredient count, and unique themes.

**Output:** The user receives seven dinners, one for each day, with ingredients, quantities, cooking instructions, and a shopping list.

- [x] API errors were not caught by the original try block. I moved the API call inside it and added specific error handlers with clearer messages, including the operation, error type, and suggestions.

- [x] Response cleaning was mixed with other tasks in generate(). I moved it into clean_json_response() and tested it separately.

- [x] JSON parsing and data validation were mixed with other tasks in generate(). I moved them into parse_and_validate_meal_plan().

- [x] A missing API key caused an unclear error. I added a check that stops execution and explains where to configure the key.

- [x] The recipe display did not include cooking instructions. I updated format_single_recipe() and tested its output.

- [ ] Check that shopping list quantities correctly add up repeated ingredients.
- [ ] Check that basic ingredients are not counted as main ingredients.
- [ ] Check that ingredients follow the selected diet.

## Before and after

**Before:** generate() called the AI, cleaned the response, parsed the JSON, and validated the meal plan in one method. The API call was outside the try block.

**After:** generate() coordinates separate functions for the AI request, response cleaning, and data validation. The API call is inside the try block, and specific error handlers provide clearer messages.

## Execution evidence

- Input: diet = "omnivore", themes = "random", preferences = "none".
- Configuration and workflow code: sections 2–5 of meal_planner_refactored.ipynb.
- Successful run: the saved notebook output shows Success: True,
  Recipes: 7, and Validation: {'passed': True, 'errors': []}.
- [Full output record](evidence/successful_output.json)
- Error tests: saved notebook outputs show simulated JSON,
  validation, connection, HTTP 403, and general API errors.

## Known limitations

The output passed the current structural checks, but manual review
found incorrect shopping totals. Chicken breast appears in four
recipes at 200g each (800g), while the shopping list shows 600g
and lists only two of the four dishes.

Olive oil is also counted as a main ingredient in Saturday's recipe.
Dietary compliance is not automatically checked.
Email delivery was not tested.

## First failure to monitor

I would first monitor incorrect shopping quantities because the
application could consume API credits and still return an incorrect
result marked as successful. Users could buy too much or too little
food. I would compare recipe quantities with shopping list totals
and flag any differences.

## Files

- [Refactored notebook](meal_planner_refactored.ipynb):
  code, tests, and saved execution outputs.
- [Original notebook](meal_planner_starter.ipynb):
  baseline code for comparison.
- [Output record](evidence/successful_output.json):
  complete result from a real API call.
- [Learning summary](lab_summary.md):
  approach, main challenge, and learning.