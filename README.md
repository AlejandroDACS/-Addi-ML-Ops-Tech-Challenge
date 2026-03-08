# Reto Técnico de IA y ML Ops

> **🚀 Solución Completada:** Este repositorio contiene la implementación final para el Reto Técnico de AI & ML Ops. Un sistema obsoleto fue refactorizado a un **Flujo de Trabajo Multi-Agente con Estado (Stateful)** impulsado por *LangGraph* y *Google Gemini 2.5 Flash*.

### 📚 Documentación Exclusiva de la Solución
Para comprender a fondo las decisiones de ingeniería, arquitectura y escalabilidad, consulta los siguientes documentos que he preparado:

1. 🧠 **[Documentación Expansiva del Proyecto](PROJECT_DOCUMENTATION.md)** - *Cómo se desarrollaron las 5 fases del proyecto.*
2. 🗺️ **[Explicación del Flujo Paso a Paso (LangGraph)](LANGGRAPH_FLOW_EXPLAINED.md)** - *Cómo se procesa la solicitud del usuario.*
3. 🏛️ **[Arquitectura y Diseño](deliverables/architecture.md)** - *Decisiones técnicas y compromisos (trade-offs).*
4. ☁️ **[Respuestas de Despliegue a Producción](deliverables/deployment_answers.md)** - *Estrategias de escalamiento para 10,000 usuarios, bases de datos y MLOps.*

---

## Resumen del Reto

**Emporyum Tech** es una plataforma de comercio electrónico colombiana que ofrece planes de pago a plazos (Compra ahora, paga después). En este reto, recibes un **prototipo funcional básico** de un asistente conversacional de IA para Emporyum Tech. El prototipo funciona de principio a fin: puedes hacerle preguntas y responderá. **Pero la calidad es deficiente.** La arquitectura es mínima, la Base de Conocimientos es superficial y las respuestas son vagas y genéricas.

Tu tarea es **mejorar significativamente la calidad y la arquitectura del asistente**. Cómo lo hagas — qué construyas, cómo lo estructures, qué decisiones de diseño tomes — depende enteramente de ti.

## Estimación de Tiempo

**6-8 horas** para una solución completa. No necesitas terminar todo — es preferible una solución parcial bien diseñada con documentación clara antes que una solución completa hecha a las prisas.

## Requisitos Previos

- Python 3.10 o superior
- [Poetry](https://python-poetry.org/docs/#installation) para la gestión de dependencias
- Una clave API de OpenAI (GPT-4o-mini o Gemini Flash es suficiente y rentable)

## Inicio Rápido

Ejecuta la solución básica primero. Mírala funcionar. Nota los problemas.

```bash
# 1. Instalar dependencias
poetry install

# 2. Crea tu archivo .env y añade tu API key
# EXPLICACIÓN DE SEGURIDAD: El archivo .env real ha sido excluido deliberadamente
# de este repositorio (vía .gitignore) para prevenir la fuga de Claves API privadas.
# Debes generar tu propia copia local usando esta plantilla:
cp .env.example .env

# 3. Ejecutar el asistente interactivo
poetry run python tests/inline.py
```

Prueba estas conversaciones y observa las respuestas:

| Si escribes | Qué deberías notar |
|-------------|------------------------|
| `¡Hola!` | Saludo genérico, no personalizado para el usuario |
| `¿Dónde está mi pedido?` | Respuesta vaga, sin detalles específicos del pedido |
| `¿Cuánto debo en cuotas?` | Respuesta vaga, sin desglose de las cuotas |
| `Quiero devolver un producto` | Respuesta genérica de una sola oración, no hay flujo transaccional de múltiples pasos |
| `¿Qué hora es?` | Intenta responder de todas formas -- no hay manejo de temas fuera de alcance |

## Contexto del Negocio

**Emporyum Tech** es una plataforma de comercio electrónico colombiana que se distingue por ofrecer compras a plazos. Los clientes pueden comprar productos de múltiples categorías y dividir los pagos en cuotas mensuales con diferentes tasas de interés.

El negocio está organizado en 4 verticales, cada una con su propio conjunto de reglas, casos atípicos y requerimientos de datos:

- **Producto y Catálogo** (`team_product.md`): ~290 productos a través de 4 categorías (Electrónica, Hogar, Moda, Belleza). Recomendaciones de productos basadas en el historial y preferencias del usuario. 5 promociones activas con reglas específicas.

- **Pagos y Cuotas** (`team_payments.md`): 4 métodos de pago (PSE, Tarjeta de Crédito, Efecty, Bancolombia A la Mano). Planes de cuotas de 1 a 24 meses con diferentes tasas de interés. Políticas de pago atrasado y cálculos de montos.

- **Operaciones y Logística** (`team_operations.md`): Flujo de compra completo desde la navegación hasta la entrega. Rastreo de pedidos a través de 6 estados. Tiempos de entrega por ciudad. Políticas de devolución y reembolso con estrictas reglas de elegibilidad.

- **Plataforma y Cuenta** (`team_platform.md`): Gestión de cuenta, restablecimiento de contraseña, autenticación de dos factores (2FA). Características de la app y resolución de problemas técnicos. Políticas de seguridad.

Los requisitos de negocio detallados para cada área están disponibles en la carpeta `docs/stakeholder_interviews/`. Estas transcripciones de entrevistas contienen las reglas específicas, flujos, casos atípicos y campos de datos que debes considerar para diseñar la Base de Conocimientos y la arquitectura del asistente.

## Estructura del Proyecto

```
ai_ml_ops_challenge/
|
|-- README.md                            # <-- ESTÁS AQUÍ
|-- pyproject.toml                       # Dependencias nativas del proyecto
|-- .env.example                         # Plantilla para tu clave API
|-- .env                                 # Tú creas esto (no se sube a git)
|
|-- docs/
|   |-- stakeholder_interviews/          # Tus fuentes principales: requisitos de negocio
|       |-- team_product.md              #   Entrevista equipo de Producto
|       |-- team_payments.md             #   Entrevista equipo de Pagos
|       |-- team_operations.md           #   Entrevista equipo de Operaciones
|       |-- team_platform.md             #   Entrevista equipo de Plataforma
|
|-- source/
|   |-- __init__.py
|   |
|   |-- application/
|   |   |-- __init__.py
|   |   |-- state.py                     # GraphState TypedDict (no modificar)
|   |   |-- graph.py                     # Definición de Topología LangGraph
|   |
|   |-- domain/
|   |   |-- __init__.py
|   |   |-- router.py                    # Clasificador e iniciador de flujo
|   |   |-- handle_general.py            # Orquestador general
|   |   |-- handle_returns.py            # Flujo síncrono dedicado para Devoluciones
|   |
|   |-- adapters/
|   |   |-- __init__.py
|   |   |-- chains/
|   |   |   |-- __init__.py
|   |   |   |-- general_chain.py         # Prompt LLM Genérico
|   |   |   |-- router_chain.py          # Prompt LLM del Enrutador
|   |   |   |-- returns_chain.py         # Prompt LLM de Devoluciones
|   |   |-- utils/
|   |       |-- __init__.py
|   |       |-- mock_data.py             # 8 perfiles de usuario falsos (no modificar)
|   |       |-- data_filter.py           # Filtro mitigador de JSON para tokens
|   |       |-- knowledge_base.py        # Centralización de directivas de los 4 equipos
|   |
|   |-- examples/                        # Referencias de patrones del framework
|       |-- README.md
|       |-- example_kb_entry.py          #   Esquema de entrada de base de datos
|       |-- example_chain.py             #   Cadena LLM con salidas Pydantic
|       |-- example_domain_function.py   #   Patrón de función asíncrona de dominio
|       |-- example_graph.py             #   Grafo ejecutable rudimentario
|
|-- tests/
|   |-- __init__.py
|   |-- inline.py                        # CLI para probar el desarrollo dinámicamente
|
|-- deliverables/
|   |-- architecture.md                  # Documentación teórica de tu arquitectura
|   |-- deployment_answers.md            # Entregable QA para MLOps / DevOps
```

## Elementos Pre-Construidos (No Modificar)

Estos archivos son provistos y **no deben** ser modificados:

| Archivo | Descripción |
|------|-------------|
| `source/application/state.py` | Diccionario (`GraphState TypedDict`) definiendo todos los campos que fluyen por LangGraph |
| `source/adapters/utils/mock_data.py` | 8 perfiles de usuario falsos con pedidos simulados, cuotas y estados de cuenta |
| `source/adapters/utils/data_filter.py` | Utilidad vital para filtrar datos del usuario e inyectar *solo* variables autorizadas |
| `source/examples/*` | Referencias de patrones del framework |
| `docs/stakeholder_interviews/*` | Transcripciones de las 4 entrevistas de liderazgo |
| `pyproject.toml` | Dependencias nativas del proyecto |

## Problemas Originales Resueltos

Al recibir el código original, presentaba numerosos fallos críticos, los cuales fueron rediseñados. Entre los problemas abordados se encuentran:

| Problema Original | Dónde mirar |
|----------------|---------------|
| Cada pregunta recibía el mismo tratamiento genérico sin enrutamiento | `router.py`, `graph.py` |
| Las respuestas eran vagas e impersonales | `general_chain.py` |
| La Base de Conocimientos era superficial y fraccionada | `knowledge_base.py` |
| Datos sensibles del usuario eran inyectados torpemente | `data_filter.py`, `handle_general.py` |
| El Asistente olvidaba lo que se había dicho, impidiendo procesos de múltiples turnos | `handle_returns.py`, `inline.py` |

## Entregables

1. **Un asistente mejorado** -- El bot debe demostrar una calidad significativamente mejor, cubriendo orgánicamente los dominios de las entrevistas, evidenciando enrutamiento y usando datos con barreras de seguridad (guardrails).

2. **Documentación de arquitectura** (`deliverables/architecture.md`) -- Documentar con diagramas, contexto semántico y explicaciones exhaustivas de qué construiste y por qué.

3. **Respuestas de Despliegue** (`deliverables/deployment_answers.md`) -- Respuestas orientadas a producción masiva desde el lado Infra/ML Ops.

## Criterios de Evaluación

Lo que valoramos, en orden aproximado de importancia:

- **Calidad de la Base de Conocimientos** -- Transcribir efectivamente las reglas de negocio a la aplicación.
- **Arquitectura Cognitiva** -- Desglosar el problema usando enrutadores LangGraph con topología inteligente y manejo del Estado como variables de control inter-turno.
- **Calidad de Salida** -- Que el bot provea respuestas correctas usando datos simulados personales y maneje desviaciones *(Fuera de alcance)*.
- **Enfoque en Producción y MLOps** -- Respuestas sólidas y razonadas respecto a picos y caídas en `deployment_answers.md`.
- **Explicación de la Solución** -- Transparencia y exactitud técnica al describir lo desarrollado en `architecture.md`.

## Consejos Finales

1. **Lee TODOS los 4 archivos de entrevistas antes de revisar el código.** Son tu fuente primaria de requerimientos y guardrails.
2. Lee `state.py` para interiorizar qué variables circulan en el *grafo* cada vez que se avanza un paso.
3. Simple y funcional es mejor que complejo e inconcluso.

## Entrega Final

1. Asegúrate de que ejecutar `poetry run python tests/inline.py` funcione en la terminal sin arrojar errores de importación.
2. Verifica que al menos un flujo de perfil completo resuelva procesos de principio a fin.
3. Comprime toda la carpeta `ai_ml_ops_challenge/` en formato ZIP (Cambiándolo por tu nombre o asegurando que sea una carpeta segura).
4. Devuélvelo.

¡Felicidades y excelente desarrollo!
