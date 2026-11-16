# Comparación antes / después: product_listing_generator.py

- **Antes:** `product_listing_generator_original.py` (lab M1.05, API, 8/10).
- **Después:** `product_listing_generator.py`.
- **Diff completo:** `cambios_original_vs_refactorizado.diff` (57 líneas añadidas y 32 quitadas).

## Resumen de cambios

| Defecto (checklist) | Antes | Después |
|---|---|---|
| (2) Datos fijados en el código | Lista `products` escrita en el programa (líneas 37–44) | Los productos se leen de `products.json` con `load_products()`. Se puede indicar otro archivo: `python product_listing_generator.py otro.json` |
| Sin validación de entrada | Un precio `"doce"` llegaba hasta el prompt y fallaba con «respuesta mal formada» | Modelo Pydantic `Product` (`price > 0`, `name` no vacío…). Los productos inválidos se rechazan **antes** de llamar a Gemini (0 llamadas gastadas) |
| (3) Errores que no dicen dónde | `"imagen no encontrada: images/taza.jpg"` | `[ERROR en encode_image_to_base64] FileNotFoundError: … \| Contexto: producto 1 (Taza), archivo … \| Sugerencia: …` |
| (1) Código repetido | `result["status"] = "error"` copiado 7 veces | `status` empieza en `"error"` y solo cambia a `"ok"` si todo va bien; los mensajes los monta una sola función, `format_error()` |
| (4) Función que hace demasiado | `generate_listing` gestionaba 7 errores con 14 líneas casi iguales | Cada error ocupa una llamada a `format_error` con la función real donde ocurre (`encode_image_to_base64`, `call_model`, `parse_listing`) |
| (5) Conexión creada al abrir el archivo | Igual | **Sin cambios** (pendiente) |

## Comportamiento con datos válidos (Step 6: «funciona igual que antes»)

| | Antes (referencia, 30/10 10:3x) | Después (30/10 15:13, con `products.json`) |
|---|---|---|
| Fichas correctas | 3/3 | 3/3 |
| Campos por ficha | title, description, features, keywords | title, description, features, keywords |
| Textos | Distintos en cada ejecución (los genera la IA) | Distintos en cada ejecución (los genera la IA) |

Archivos: `listings_baseline.json` (antes) y `listings_refactorizado.json` (después).

## Errores cubiertos (criterios de verificación del lab)

| Error | Dónde se maneja | Evidencia |
|---|---|---|
| `FileNotFoundError` (imagen) | `generate_listing` → `encode_image_to_base64` | `capturas/02_error_imagen_no_encontrada.png` (real) |
| `FileNotFoundError` (archivo de productos) | arranque → `load_products` | `capturas/06_error_archivo_no_existe.png` (real) |
| `JSONDecodeError` (con línea y columna) | arranque → `load_products` | `capturas/05_error_json_mal_formado.png` (real) |
| Pydantic `ValidationError` | arranque → `Product` | `capturas/04_error_datos_invalidos_pydantic.png` + `04_salida_datos_invalidos.txt` (real) |
| Errores de la API de OpenAI/Gemini (401/400, 429, 5xx) | `generate_listing` → `call_model` | `capturas/07_errores_api_SIMULADOS.txt` (**simulado**) |
| Errores de red (conexión, tiempo agotado) | `generate_listing` → `call_model` | `capturas/07_errores_api_SIMULADOS.txt` (**simulado**) |

Referencia del formato antiguo de los errores de API: capturas del 8/10 en `Semana 1/2026-10-08/lab_api/capturas/06_error_400_clave_invalida.png` y `07_error_503_servidor_saturado.png`.

## Limitaciones conocidas

- Los errores de API y de red se han **simulado** en el entorno del tutor con el código refactorizado real; no se han provocado en el ordenador del alumno.
- Si `products.json` contiene algo que no es una lista de objetos, el programa no da un mensaje propio.
- El mensaje de `ValidationError` ocupa varias líneas e incluye enlaces de Pydantic en inglés.
- Defecto (5) pendiente: la clave y el cliente se crean al importar el archivo.
- Pasos opcionales del lab (API wrapper con reintentos y logging): no realizados.
