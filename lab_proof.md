# lab_proof.md: punto de entrada para el revisor

**Lab:** From hacky script to "we could ship this" (16/10) · **Path 1:** refactorizar el código propio del lab M1.05 (API, 8/10).
**Estado:** terminado y probado en local el 30/10/2026. **No enviado** (fork/PR pendiente).

## Qué mirar, en este orden

1. `lab_summary.md`: resumen de un párrafo (requisito de entrega).
2. `REFACTORING_CHECKLIST.md`: diagnóstico y prioridades (Step 2).
3. `COMPARACION_ANTES_DESPUES.md`: qué cambió, comportamiento y errores cubiertos.
4. `product_listing_generator.py`: código refactorizado. Original: `product_listing_generator_original.py`.
5. `cambios_original_vs_refactorizado.diff`: diff completo.

## Traza de ejecución (entrada → salida)

| | Archivo |
|---|---|
| Entrada | `products.json` (3 productos) + `images/` |
| Ejecución | `python product_listing_generator.py` → `capturas/03_refactorizado_con_products_json_3de3.png` |
| Salida | `listings_refactorizado.json` (copia del `listings.json` de esa ejecución, 3/3 ok) |
| Referencia previa | `listings_baseline.json` + `capturas/00_baseline_original_3de3.png` |

## Evidencias de errores

| Caso | Orden ejecutada | Evidencia | ¿Real o simulado? |
|---|---|---|---|
| Imagen inexistente | prueba unitaria de `generate_listing` | `capturas/02_error_imagen_no_encontrada.png` | Real |
| Datos inválidos (Pydantic) | `python product_listing_generator.py invalid_products.json` | `capturas/04_*` | Real |
| JSON mal formado | `python product_listing_generator.py malformed.json` | `capturas/05_error_json_mal_formado.png` | Real |
| Archivo de productos inexistente | `python product_listing_generator.py no_existe.json` | `capturas/06_error_archivo_no_existe.png` | Real |
| API (401, 429, 503) y red | errores fabricados sobre `call_model` | `capturas/07_errores_api_SIMULADOS.txt` | **Simulado** |

## Uso de IA (Prompt Discipline del lab)

- **Alumno:** diagnóstico de los defectos, prioridades, contenido de los consejos de cada error, predicciones, ejecución de todas las pruebas en su equipo y validación de los resultados.
- **Tutor de IA:** explicaciones, estructura de `format_error`, bloques de código de `generate_listing` y Pydantic/`products.json`, y su colocación final en el archivo (a petición del alumno, por tiempo). También los archivos de datos de prueba y estos documentos de evidencia.
- **Consecuencia:** el código final lo **escribió en su mayor parte la IA**; el alumno lo **dirigió, revisó y validó**. Esto no cumple del todo la regla del lab («no pedirle que produzca el artefacto final») y se declara aquí.

No se incluye ninguna clave: el `.env` no forma parte de la entrega.
