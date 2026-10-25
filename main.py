
import json
from pathlib import Path


def load_products(file_path):
    """Load product data from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        print("SUCCESS: load_products - File loaded.")
        return data

    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"load_products: File not found: {file_path}. "
            "Check the filename and folder."
        ) from error

    except json.JSONDecodeError as error:
        raise ValueError(
            f"load_products: Invalid JSON at line {error.lineno}, "
            f"column {error.colno}."
        ) from error


def validate_products(data):
    """Check that each product has the required fields."""
    if not isinstance(data, dict) or not isinstance(
        data.get("products"), list
    ):
        raise ValueError(
            "validate_products: Expected a JSON object "
            "containing a products list."
        )

    required_fields = {"id", "name", "category", "price", "features"}

    for index, product in enumerate(data["products"]):
        if not isinstance(product, dict):
            raise ValueError(
                f"validate_products: Product {index + 1} must be an object."
            )

        missing = required_fields - product.keys()
        if missing:
            raise ValueError(
                f"validate_products: Product {index + 1} "
                f"is missing: {', '.join(sorted(missing))}."
            )

        if not isinstance(product["price"], (int, float)) or isinstance(
            product["price"], bool
        ) or product["price"] < 0:
            raise ValueError(
                f"validate_products: Invalid price for {product['id']}."
            )

        if not all(
            isinstance(product[field], str) and product[field].strip()
            for field in ("id", "name", "category")
        ):
            raise ValueError(
                f"validate_products: Invalid text fields in product {index + 1}."
            )

        if not isinstance(product["features"], list) or not all(
            isinstance(feature, str) for feature in product["features"]
        ):
            raise ValueError(
                f"validate_products: Features must be a list of strings "
                f"for {product['id']}."
            )

    print(
        f"SUCCESS: validate_products - "
        f"{len(data['products'])} products validated."
    )
    return data["products"]


def create_description(product):
    """Create a simple description without calling an external API."""
    features = ", ".join(product["features"])
    return (
        f"{product['name']} is a product in the {product['category']} "
        f"category, priced at {product['price']:.2f}. "
        f"Key features include: {features}."
    )


def process_products(products):
    """Generate descriptions for all validated products."""
    results = []

    for product in products:
        results.append({
            "id": product["id"],
            "name": product["name"],
            "description": create_description(product)
        })

    return results


def save_results(results, file_path):
    """Save processed products to a JSON file."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=2, ensure_ascii=False)
        print(f"SUCCESS: save_results - Results saved to {file_path}.")

    except OSError as error:
        raise OSError(
            f"save_results: Could not write to {file_path}: {error}"
        ) from error


def main():
    """Coordinate the workflow."""
    input_path = Path(__file__).with_name("products.json")
    output_path = Path(__file__).with_name("results.json")

    try:
        data = load_products(input_path)
        products = validate_products(data)
        results = process_products(products)
        save_results(results, output_path)
        print(f"Workflow completed: {len(results)} products processed.")

    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"WORKFLOW ERROR: {error}")


if __name__ == "__main__":
    main()
