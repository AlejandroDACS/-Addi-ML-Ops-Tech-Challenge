# Reto Técnico AI & ML Ops - Asistente de Emporyum Tech

## Resumen

**Emporyum Tech** es una plataforma colombiana de comercio electrónico que ofrece planes de pago a cuotas (compre ahora, pague después). En este reto recibes un **prototipo funcional básico** de un asistente de inteligencia artificial conversacional para Emporyum Tech. El prototipo funciona de extremo a extremo: puedes hacerle preguntas y responderá. **Pero la calidad es deficiente.** La arquitectura es mínima, la Base de Conocimientos es superficial y las respuestas son vagas y genéricas.

Tu tarea es **mejorar significativamente la calidad y arquitectura del asistente**. Cómo lo hagas — qué construyas, cómo lo estructures, qué decisiones de diseño tomes — depende enteramente de ti.

## Estimación de Tiempo

**6-8 horas** para una solución completa. No necesitas terminar todo — es preferible una solución parcial bien diseñada con documentación clara, que una solución completa hecha a las prisas.

## Prerrequisitos

- Python 3.10 o superior
- [Poetry](https://python-poetry.org/docs/#installation) para gestión de dependencias
- Una clave API de OpenAI (GPT-4o-mini o Gemini Flash es suficiente y rentable)

## Inicio Rápido

Ejecuta la solución básica primero. Mírala funcionar. Nota los problemas.

```bash
# 1. Instalar dependencias
poetry install

# 2. Crea tu archivo .env y añade tu API key
cp .env.example .env

# 3. Ejecutar el asistente interactivo
poetry run python tests/inline.py
```

Prueba estas conversaciones y observa las respuestas:

| Si escribes | Qué deberías notar |
|-------------|--------------------|
| `¡Hola!` | Saludo genérico, no personalizado para el usuario |
| `¿Dónde está mi pedido?` | Respuesta vaga, sin detalles específicos del pedido |
| `¿Cuánto debo de cuotas?` | Respuesta vaga, sin desglose de las cuotas |
| `Quiero devolver un producto` | Respuesta genérica de una sola frase, sin un flujo transaccional de pasos múltiples |
| `¿Qué hora es?` | Intenta responder de todas formas -- no hay manejo de temas fuera del alcance (*out-of-scope*) |

## Contexto de Negocio

**Emporyum Tech** es una plataforma colombiana de comercio electrónico que se diferencia por ofrecer compras a plazos (Buy Now, Pay Later). Los clientes pueden comprar productos de múltiples categorías y dividir los pagos en cuotas mensuales con diferentes tasas de interés.

El negocio está organizado en 4 verticales, cada una con su propio conjunto de reglas, casos límite (*edge cases*) y requisitos de datos:

- **Producto y Catálogo** (`team_product.md`): ~290 productos a través de 4 categorías (Electrónica, Hogar, Moda, Belleza). Recomendaciones de productos basadas en el historial del usuario y preferencias. 5 promociones activas con reglas específicas.

- **Pagos y Cuotas** (`team_payments.md`): 4 métodos de pago (PSE, Tarjeta, Efecty, Bancolombia A la Mano). Planes de cuotas de 1 a 24 meses con diferentes tasas de interés. Políticas de pago atrasado y cálculos de montos.

- **Operaciones y Logística** (`team_operations.md`): Flujo de compra completo desde la navegación hasta la entrega. Rastreo de pedidos a través de 6 estados. Tiempos de entrega por ciudad. Políticas de devolución y reembolso con reglas estrictas de elegibilidad.

- **Plataforma y Cuenta** (`team_platform.md`): Gestión de cuenta, restablecimiento de contraseña, autenticación de doble factor (2FA). Funciones de la aplicación y resolución de problemas técnicos. Políticas de seguridad.

Los requerimientos detallados de negocio para cada área están disponibles en la carpeta `docs/stakeholder_interviews/`. Estas transcripciones de entrevistas contienen las reglas específicas, flujos, casos límite y campos de datos que necesitas considerar para diseñar la Base de Conocimientos y la arquitectura del asistente.

## Estructura del Proyecto

```
ai_ml_ops_challenge/
|
|-- README.md                            # <-- ESTÁS AQUÍ
|-- pyproject.toml                       # Dependencias del proyecto
|-- .env.example                         # Plantilla para tu clave API
|-- .env                                 # Tú creas esto (no se sube a git)
|
|-- docs/
|   |-- stakeholder_interviews/          # Tus fuentes principales: requerimientos de negocio
|       |-- team_product.md              #   Entrevista al equipo de Producto
|       |-- team_payments.md             #   Entrevista al equipo de Pagos
|       |-- team_operations.md           #   Entrevista al equipo de Operaciones
|       |-- team_platform.md             #   Entrevista al equipo de Plataforma
|
|-- source/
|   |-- __init__.py
|   |
|   |-- application/
|   |   |-- __init__.py
|   |   |-- state.py                     # GraphState TypedDict (no modificar)
|   |   |-- graph.py                     # Definición de la Topología LangGraph
|   |
|   |-- domain/
|   |   |-- __init__.py
|   |   |-- router.py                    # Clasificador e inicio del flujo
|   |   |-- handle_general.py            # Orquestador general
|   |   |-- handle_returns.py            # Flujo síncrono dedicado a Devoluciones
|   |
|   |-- adapters/
|   |   |-- __init__.py
|   |   |-- chains/
|   |   |   |-- __init__.py
|   |   |   |-- general_chain.py         # Prompt del LLM Genérico
|   |   |   |-- router_chain.py          # Prompt del LLM Enrutador
|   |   |   |-- returns_chain.py         # Prompt del LLM para Devoluciones 
|   |   |-- utils/
|   |       |-- __init__.py
|   |       |-- mock_data.py             # 8 perfiles de usuarios falsos (no modificar)
|   |       |-- data_filter.py           # Filtro mitigador de JSON para tokens
|   |       |-- knowledge_base.py        # Centralización de directivas de los 4 equipos
|   |
|   |-- examples/                        # Referencias y patrones de código base
|       |-- README.md
|       |-- example_kb_entry.py          #   Esquema de entrada en la Base de Datos
|       |-- example_chain.py             #   LLM Chain con salidas Pydantic
|       |-- example_domain_function.py   #   Patrón de función dominio asíncrona
|       |-- example_graph.py             #   Grafo ejecutable rudimentario
|
|-- tests/
|   |-- __init__.py
|   |-- inline.py                        # CLI para probar dinámicamente el desarrollo
|
|-- deliverables/
    |-- architecture.md                  # Documentación teórica de tu arquitectura
    |-- deployment_answers.md            # Entregable de QA para MLOps / DevOps
```

## Elementos Pre-Construidos (No Modificar)

Estos archivos son suministrados y **no** deben ser modificados:

| Archivo | Descripción |
|------|-------------|
| `source/application/state.py` | Diccionario (`GraphState TypedDict`) que define todos los campos que fluyen a través de LangGraph |
| `source/adapters/utils/mock_data.py` | 8 perfiles de usuarios de mentira con pedidos ficticios, cuotas y estados de cuenta |
| `source/adapters/utils/data_filter.py` | Utilidad vital para filtrar los datos del usuario e inyectar *solo* variables autorizadas |
| `source/examples/*` | Patrones del framework de referencia |
| `docs/stakeholder_interviews/*` | Transcripciones de las 4 entrevistas a líderes |
| `pyproject.toml` | Dependencias del proyecto nativas |

## Problemas Originales Solucionados

Al recibir el código original, presentaba numerosas fallas críticas, las cuales fueron rediseñadas. Entre los problemas abordados se incluyen:

| Problema Original | Dónde mirar |
|---------|--------------|
| Cada pregunta recibía el mismo tratamiento genérico sin enrutamiento | `router.py`, `graph.py` |
| Las respuestas eran vagas e impersonales | `general_chain.py` |
| La Base de Conocimientos era superficial y fraccionaria | `knowledge_base.py` |
| Los datos sensibles del usuario se inyectaban torpemente | `data_filter.py`, `handle_general.py` |
| El Asistente olvidaba lo dicho no permitiendo procesos de múltiples turnos | `handle_returns.py`, `inline.py` |

## Entregables

1. **Un asistente mejorado** -- El bot debe demostrar una calidad significativamente mejor abarcando orgánicamente los dominios de las entrevistas, evidenciando enrutamiento y uso de datos con barreras.

2. **Documentación de la arquitectura** (`deliverables/architecture.md`) -- Documento con diagramas, contexto semántico y explicaciones exhaustivas de lo que construiste y por qué.

3. **Respuestas de Despliegue** (`deliverables/deployment_answers.md`) -- Respuestas orientadas a producción masiva desde el lado Infra/ML Ops .

## Criterios de Evaluación

Lo que valoramos, en aproximado orden de importancia:

- **Calidad de la Base de Conocimientos** -- Transcribir efectivamente reglas de negocio en la aplicación.
- **Arquitectura Cognitiva** -- Descomponer el problema utilizando enrutadores de LangGraph con topología inteligente y manejo del Estado (`State`) como variables de control inter-turnos.
- **Calidad de Salida** -- Que el bot ofrezca respuestas correctas usando la data simulada personal y maneje desviaciones *(Out of scope)*.
- **Enfoque de Producción y MLOps** -- Respuestas sólidas y argumentadas frente a picos y caídas en `deployment_answers.md`.
- **Explicación de la solución** -- Transparencia y exactitud técnica al describir lo desarrollado en `architecture.md`.

## Consejos Finales

1. **Lee TODOS los 4 archivos de las entrevistas antes de revisar el código.** Son tu fuente primaria de requerimientos y barreras.
2. Lee `state.py` para interiorizar qué variables circulan en el *grafo* cada vez que se avanza un paso.
3. Lo simple y funcional es mejor que lo complejo e inacabado.

## Entrega Final

1. Asegurarse de que al correr `poetry run python tests/inline.py` se ejecute la terminal sin lanzar errores de importación.
2. Verificar que al menos un flujo completo de un perfil resuelva los procesos de inicio a fin.
3. Comprimir la capeta entera `ai_ml_ops_challenge/` en formato ZIP (Cambiándole tu nombre o asegurando que sea un folder seguro).
4. Devolverlo.

¡Felicidades y excelente desarrollo!
