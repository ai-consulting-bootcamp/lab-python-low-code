# Refactoring Checklist — product_listing_generator.py

Lab 16/10 · Path 1 (código del lab M1.05, API del 8/10)
Diagnóstico hecho el 30/10/2026. Prioridades decididas por el alumno; el tutor ha transcrito sus palabras.

## Problemas encontrados

- [x] **(1) Código repetido:** `result["status"] = "error"` aparece 7 veces en `generate_listing` (líneas 123–143). Cualquier mejora de los mensajes hay que hacerla en 7 sitios.
- [x] **(2) Datos fijados en el código:** los productos están escritos dentro del programa (líneas 37–44). Para cambiar o añadir productos hay que editar el código.
- [x] **(3) Errores que no dicen dónde:** el `except (json.JSONDecodeError, ValueError)` (línea 141) etiqueta todo como "respuesta mal formada". Prueba: con `"price": "doce"` el mensaje culpa a la IA, aunque Gemini no llegó a recibir la petición; no indica función, campo ni solución.
- [x] **(4) Función que hace demasiado:** `generate_listing` (líneas 113–144, 32 líneas) coordina el proceso y además gestiona ella sola 7 tipos de error.
- [ ] **(5) Responsabilidades mezcladas:** la clave y la conexión con Gemini se crean al abrir el archivo (líneas 23–33). No se puede probar ninguna función sin clave, aunque no use la IA.

## Prioridad (decisión del alumno)

1. **(3) Errores que no dicen dónde:** "porque puedes tardar mucho en resolverlo si no se sabe dónde está el fallo".
2. **(4) Función que hace demasiado:** "porque una tarea cada vez, como dice el lab".
3. **(2) Datos en el código → `products.json`:** para separar los datos del programa y poder validarlos con Pydantic al entrar.

Secundarios: (1) se resuelve al centralizar los errores en (3)/(4); (5) queda pendiente si hay tiempo.

## Estado (30/10, tarde)

- Hechos: (1), (2), (3), (4). Detalle en `COMPARACION_ANTES_DESPUES.md`.
- Pendiente: (5).
