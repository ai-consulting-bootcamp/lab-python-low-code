"""Offline notebook regression checks. Run: python -m unittest discover -s tests -v."""
import ast
import contextlib
import csv
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_definitions(path, namespace):
    """Execute definitions only, never notebook downloads or top-level API calls."""
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if path.name == "good_practice.ipynb" and "def fake_create(" in source:
            break  # Remaining cells are examples/checkpoints, not production definitions.
        try:
            tree = ast.parse(source)
        except SyntaxError:  # Legacy notebook includes pip/magic commands.
            continue
        tree.body = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
        if tree.body:
            exec(compile(tree, f"{path.name}/cell-{index}", "exec"), namespace)


class PracticeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import base64
        import csv
        import inspect
        import math
        import time
        import traceback
        from functools import wraps
        from PIL import Image
        cls.new = dict(base64=base64, csv=csv, inspect=inspect, math=math, time=time,
                       traceback=traceback, wraps=wraps, Image=Image, BytesIO=io.BytesIO,
                       Path=Path, json=json, REQUIRED_KEYS={"title", "description", "features", "keywords"})
        load_definitions(ROOT / "good_practice.ipynb", cls.new)
        cls.old = dict(cls.new)
        load_definitions(ROOT / "legacy" / "bad_practice.ipynb", cls.old)
        cls.listing = {"title": "Blue shirt", "description": "An everyday blue shirt.",
                       "features": ["Blue", "Short sleeves"], "keywords": "shirt, blue"}

    def setUp(self):
        self.product = {"id": 1, "productDisplayName": "Blue shirt", "articleType": "Shirts",
                        "baseColour": "Blue", "gender": "Unisex", "usage": "Casual",
                        "image": self.new["Image"].new("RGB", (8, 8), "blue")}
        self.requests = []

        def create(**request):
            self.requests.append(request)
            return SimpleNamespace(output_text=json.dumps(self.listing))
        self.client = SimpleNamespace(responses=SimpleNamespace(create=create))
        self.old["client"] = self.client

    def failure(self, function, *args, kind=None, context=None):
        with self.assertRaises(self.new["WorkflowError"]) as caught:
            self.new[function](*args)
        error = caught.exception
        self.assertEqual(error.function, function)
        if kind:
            self.assertEqual(error.error_type, kind)
        message = str(error)
        for marker in ("Function:", "Error:", "Context:", "source=", "Suggestion:"):
            self.assertIn(marker, message)
        if context:
            self.assertIn(context, message)
        self.assertIsNotNone(error.__cause__)
        return error

    def test_valid_listing_matches_original(self):
        self.assertEqual(self.old["generate_listing"](self.product),
                         self.new["generate_listing"](self.product, self.client))
        self.assertEqual(self.requests[0], self.requests[1])

    def test_valid_batch_matches_original(self):
        import pandas as pd
        with contextlib.redirect_stdout(io.StringIO()):
            previous = self.old["process_products"](pd.DataFrame([self.product]), n=1, delay=0)
        current = self.new["process_products"]([self.product], self.client, n=1, delay=0)
        self.assertEqual(previous, current)

    def test_missing_file_reports_path_and_repair(self):
        with tempfile.TemporaryDirectory() as directory:
            self.failure("load_local_products", Path(directory) / "absent.json",
                         kind="FileNotFoundError", context="absent.json")

    def test_permission_errors_report_destination(self):
        with patch.object(Path, "open", side_effect=PermissionError("File locked")):
            self.failure("save_json", [], "locked.json", kind="PermissionError", context="locked.json")
        with patch.object(Path, "mkdir", side_effect=PermissionError("Access denied")):
            self.failure("create_output_directory", "locked-folder", kind="PermissionError", context="permissions")

    def test_error_messages_improve_on_original(self):
        invalid = {**self.product, "image": None}
        with self.assertRaises(AttributeError) as previous:
            self.old["generate_listing"](invalid)
        current = self.failure("validate_product", invalid, 29.99, context="image")
        self.assertNotIn("Suggestion:", str(previous.exception))
        self.assertIn("product_id=1", str(current))
        self.assertIn("Suggestion:", str(current))

    def test_invalid_batch_options(self):
        for n, delay in ((-1, 0), (True, 0), (1, -1), (1, float("nan"))):
            with self.subTest(n=n, delay=delay):
                self.failure("validate_batch_options", n, delay, kind="ValueError")

    def test_invalid_json_reports_line_and_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text('{\n"id": }', encoding="utf-8")
            error = self.failure("load_local_products", path, kind="JSONDecodeError", context="JSON line 2, column 7")
            self.assertIn(str(path.name), str(error))

    def test_each_invalid_product_field_is_identified(self):
        for field in ("id", "productDisplayName", "articleType"):
            with self.subTest(field=field):
                invalid = {k: v for k, v in self.product.items() if k != field}
                self.failure("validate_product", invalid, 29.99, kind="ValueError", context=field)
        for field in ("productDisplayName", "articleType"):
            with self.subTest(empty=field):
                self.failure("validate_product", {**self.product, field: " "}, 29.99, context=field)

    def test_missing_response_fields_and_wrong_types(self):
        self.failure("validate_listing", {}, context="Missing keys")
        for field in ("title", "description", "features", "keywords"):
            with self.subTest(field=field):
                self.failure("validate_listing", {**self.listing, field: 42}, context=field)
        self.failure("parse_listing", "not JSON", kind="JSONDecodeError")

    def test_api_error_details(self):
        import httpx
        from openai import APIConnectionError, APITimeoutError, RateLimitError, AuthenticationError, InternalServerError
        request = httpx.Request("POST", "https://api.openai.com/v1/responses")
        failures = [(APIConnectionError(request=request), "internet"),
                    (APITimeoutError(request=request), "timeout")]
        for error_class, status, suggestion in ((RateLimitError, 429, "quota"),
                                                (AuthenticationError, 401, "OPENAI_API_KEY"),
                                                (InternalServerError, 500, "status code")):
            failures.append((error_class("Simulated API failure", response=httpx.Response(status, request=request), body=None), suggestion))
        for error, suggestion in failures:
            with self.subTest(error=type(error).__name__):
                def fail(**kwargs):
                    raise error
                client = SimpleNamespace(responses=SimpleNamespace(create=fail))
                wrapped = self.failure("call_listing_api", client, [], kind=type(error).__name__, context=suggestion)
                self.assertIs(wrapped.__cause__, error)

    def test_batch_continues_and_preserves_error_origin(self):
        results, errors = self.new["process_products"]([{}, self.product], self.client, n=2, delay=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(self.requests), 1)
        self.assertIn("Function: validate_product", errors[0]["error"])

    def test_file_round_trip_and_empty_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            self.new["save_json"]([self.listing], folder / "listing.json")
            self.assertEqual(self.new["load_local_products"](folder / "listing.json"), [self.listing])
            self.new["save_csv"]([], folder / "errors.csv", ["id", "error"])
            with (folder / "errors.csv").open(encoding="utf-8", newline="") as stream:
                reader = csv.DictReader(stream)
                self.assertEqual(reader.fieldnames, ["id", "error"])
                self.assertEqual(list(reader), [])


if __name__ == "__main__":
    unittest.main()
