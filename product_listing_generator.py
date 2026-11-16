"""
product_listing_generator.py
Lab día 8 (Ironhack): generar fichas de producto a partir de una imagen y sus datos.

Flujo: datos + imagen -> Python -> API (Gemini en modo compatible con OpenAI) -> JSON -> validación -> listings.json

Nota: el enunciado usa ChatGPT. Aquí se usa Gemini (nivel gratuito) con la misma
biblioteca `openai`, cambiando solo `base_url`, el nombre del modelo y la clave.
La clave se lee del archivo .env y nunca se escribe en el código.
"""

# 1. Cargar bibliotecas
import os
import json
import time
import base64

import openai
from dotenv import load_dotenv
from openai import OpenAI
import sys
from pydantic import BaseModel, Field, ValidationError

# 2. Leer la clave del .env (sin mostrarla)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Error controlado: sin clave no tiene sentido continuar
    raise SystemExit("ERROR: falta GEMINI_API_KEY en el archivo .env")

# 3. Crear el cliente apuntando a Gemini (Step 1)
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
MODEL = "gemini-3.5-flash-lite"

# 4. Molde de un producto y carga desde un archivo JSON (Step 2: los datos ya no están dentro del código)
PRODUCTS_FILE = "products.json"


class Product(BaseModel):
    """Cómo debe ser un producto. Pydantic rechaza el que no encaje."""
    id: int
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    category: str = Field(min_length=1)
    image_path: str = Field(min_length=1)


def load_products(path):
    """Solo carga el archivo JSON y devuelve la lista de productos, sin validarlos."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# 5. Codificar imagen a base64 (Step 3)
def encode_image_to_base64(image_path):
    """Lee la imagen en binario y la devuelve como texto base64."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


# 6. Crear el prompt (Step 4)
def create_product_listing_prompt(name, price, category):
    """Devuelve el texto de instrucciones para la IA con los datos del producto."""
    return f"""Eres un redactor con mucha experiencia, preciso y con pocas palabras, que crea copys atractivos para el consumidor y para Google. Analiza la imagen y crea una ficha de producto en español.

Datos del producto:
- Nombre: {name}
- Precio: {price:.2f} €
- Categoría: {category}

Devuelve SOLO un JSON con esta estructura:
{{
  "title": "título SEO, máximo 60 caracteres",
  "description": "descripción persuasiva de 150-200 palabras",
  "features": ["5 a 7 características"],
  "keywords": "10-15 palabras clave separadas por comas"
}}

Menciona colores, materiales y detalles que veas en la imagen."""


# 7. Llamar a la API con imagen + prompt (Step 5)
def call_model(prompt, encoded_image):
    """Envía el prompt y la imagen al modelo y devuelve el texto de la respuesta."""
    response = client.chat.completions.create(
        model=MODEL,
        timeout=60,  # si en 60 s no responde, error en lugar de esperar para siempre
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                ],
            }
        ],
    )
    return response.choices[0].message.content


# 8. Convertir la respuesta en diccionario y validarla (Step 5)
REQUIRED_FIELDS = ["title", "description", "features", "keywords"]


def parse_listing(raw_text):
    """Recorta desde la primera { hasta la última } (quita ```json ... ```) y la convierte en diccionario."""
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("la respuesta no contiene ningún JSON")
    listing = json.loads(raw_text[start:end])
    missing = [f for f in REQUIRED_FIELDS if f not in listing]
    if missing:
        raise ValueError(f"faltan campos en la respuesta: {missing}")
    return listing


# 9. Generar la ficha de UN producto, con manejo de errores (Step 6)

def format_error(function_name, error, context, suggestion):
    return f"[ERROR en {function_name}] {type(error).__name__}: {error} | Contexto: {context} | Sugerencia: {suggestion}"
def generate_listing(product):
    """Devuelve un diccionario con el producto y su ficha, o con el error ocurrido."""
    result = {"id": product["id"], "name": product["name"],
              "price": product["price"], "category": product["category"],
              "status": "error"}   # por defecto "error"; solo se cambia a "ok" si todo va bien
    context = f"producto {product['id']} ({product['name']})"
    try:
        encoded = encode_image_to_base64(product["image_path"])
        prompt = create_product_listing_prompt(product["name"], product["price"], product["category"])
        raw_text = call_model(prompt, encoded)
        result["listing"] = parse_listing(raw_text)
        result["status"] = "ok"
    except FileNotFoundError as e:
        result["error"] = format_error("encode_image_to_base64", e, f"{context}, archivo {product['image_path']}",
                                       "Comprueba que la imagen existe en la carpeta images/ y que el nombre coincide con image_path")
    except (openai.AuthenticationError, openai.BadRequestError) as e:   # 401 / 400: clave no válida o petición rechazada
        result["error"] = format_error("call_model", e, context,
                                       "Revisa que la clave esté bien escrita en el archivo .env (GEMINI_API_KEY)")
    except openai.RateLimitError as e:                                   # 429: demasiadas peticiones o sin cupo
        result["error"] = format_error("call_model", e, context,
                                       "Espera un minuto y reinténtalo; si sigue, has gastado el cupo del día: espera a mañana o revisa tu plan")
    except (openai.APITimeoutError, openai.APIConnectionError) as e:     # sin conexión o sin respuesta a tiempo
        result["error"] = format_error("call_model", e, context,
                                       "Comprueba tu conexión a internet y reinténtalo en unos minutos")
    except openai.InternalServerError as e:                              # 5xx: fallo de los servidores de Gemini
        result["error"] = format_error("call_model", e, context,
                                       "El fallo es de Gemini, no tuyo: no cambies nada y reinténtalo en unos minutos")
    except (json.JSONDecodeError, ValueError) as e:                      # respuesta sin JSON válido o con campos que faltan
        result["error"] = format_error("parse_listing", e, context,
                                       "La IA no devolvió el JSON esperado: vuelve a ejecutar; si se repite, revisa el prompt")
    return result


# 10. Procesar todos los productos y guardar los resultados (Step 6)
if __name__ == "__main__":
    # Archivo de productos: por defecto products.json; se puede indicar otro al ejecutar
    path = sys.argv[1] if len(sys.argv) > 1 else PRODUCTS_FILE
    try:
        products = load_products(path)
    except FileNotFoundError as e:
        raise SystemExit(format_error("load_products", e, f"archivo {path}",
                                      "Comprueba que el archivo existe en la carpeta del programa y que el nombre está bien escrito"))
    except json.JSONDecodeError as e:
        raise SystemExit(format_error("load_products", e, f"archivo {path}, línea {e.lineno}, columna {e.colno}",
                                      "Revisa el JSON en esa posición: suele faltar o sobrar una coma, una comilla o una llave"))

    results = []
    for raw in products:
        try:
            product = dict(Product(**raw))   # Pydantic revisa el producto en la puerta
        except ValidationError as e:
            message = format_error("Product (validación Pydantic)", e, f"producto {raw.get('id', '?')} de {path}",
                                   "Corrige en el archivo JSON los campos que se indican")
            print(f"  ERROR -> {message}")
            results.append({"id": raw.get("id"), "status": "error", "error": message})
            continue   # este producto no va a Gemini; seguimos con el siguiente
        print(f"Procesando {product['id']}: {product['name']} ...")
        result = generate_listing(product)
        if result["status"] == "ok":
            print(f"  OK -> {result['listing']['title']}")
        else:
            print(f"  ERROR -> {result['error']}")
        results.append(result)
        time.sleep(2)  # pausa entre llamadas para no saturar la API

    with open("listings.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\nTerminado: {ok}/{len(results)} fichas correctas. Guardado en listings.json")
