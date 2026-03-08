# Addi ML Ops Tech Challenge 
Este documento detalla exhaustivamente la transformación metodológica aplicada para resolver el "AI & ML Ops Tech Challenge". Está diseñado para actuar como el pergamino principal para entender la lógica sistémica, analizando el orden cronológico de desarrollo, los archivos que interactúan en cada fase y los algoritmos elegidos.

---

## 1. Patrones Arquitectónicos y Algoritmos Elegidos

La arquitectura defectuosa original utilizaba el Anti-Patrón *"God Object"*, enviando toda la carga cognitiva a un único nodo genérico (`handle_general.py`). La refactorización optó por el paradigma **Stateful Multi-Agent Workflow** (Flujo de Trabajo Multi-Agente con Estado), soportado por **Enrutamiento Semántico** en una máquina central gobernada por **LangGraph** y Modelos **Zero-Shot Classifier** bajo **Gemini 2.5 Flash**.

1. **Enrutamiento Determinista (Clasificador Semántico Estructurado):** Antes de conversar con el usuario, un prompt oculto obliga al LLM a leer el array de "Temas Válidos" estipulados y a aplicar `Pydantic Structured Output` para devolver un JSON estricto clasificando la intención del usuario. 
   - *¿Por qué?* Evita usar LLMs conversacionales lentos y mitiga la fuerte necesidad de RAG/Embeddings para una base de conocimientos categórica limitada como esta.
2. **Bifurcación Condicional (Grafos Condicionales):** La red evalúa las salidas del Router y dirige matemáticamente el flujo ("Si se dice X -> Ir al nodo Y"). Resuelve el problema del *"Context Stuffing"* (Falta de atención) ya que aísla instrucciones que no conciernen a esa consulta.
3. **Máquina de Estados Finitos Multiturno (Variables Persistentes GraphState):** Explotando las propiedades mutables de `state.py`, acoplamos booleanos como `is_return_in_progress` que permiten al bot recordar interacciones pasadas y romper la limitación HTTP de "Amnesia Sin Estado".

---

## 2. Desarrollo Cronológico: Flujo de Modificación, Relaciones de Archivos y Responsabilidades

La solución fue abordada de adentro hacia afuera: primero cimentando la Base de Datos o Ingeniería de Conocimiento ("Data"), para luego construir el Sistema Nervioso Inferencial ("Chains"), los Nodos Operativos ("Handlers"), y terminando en el Orquestador Central ("Graph").

### FASE 1: Ingeniería y Extracción de Datos (El Cerebro Estático)
*   **Problema:** La base original era precaria. El bot no tenía pautas operativas precisas (como límites de 15 días, o tasas del 1.5%) y no aplicaba lenguaje comercial para las sugerencias de la App de Emporyum Tech.
*   **Archivos Modificados:** 
    *   `source/adapters/utils/knowledge_base.py` **(Refactorización Extrema)**
*   **Detalle Sistémico:** Las 4 entrevistas con stakeholders en `docs/stakeholder_interviews/*` (Producto, Operaciones, Pagos, Plataforma) fueron cuidadosamente evaluadas. Las narrativas sueltas fueron traducidas a un súper-diccionario hiper-estructurado en Python (`SCENARIO_KNOWLEDGE_BASE`). Cada clave del diccionario encripta un "Dominio", sus *instrucciones obligatorias*, sus casos base, y cruza variables explícitas que el nodo a su vez buscará hidratar más tarde. 
*   **Relación Posterior:** Este diccionario es el "Oráculo" del cual los `handlers` de la Fase 3 se alimentarán dinámicamente.

### FASE 2: Clasificación de Tráfico (El Enrutador Inteligente)
*   **Problema:** Para dividir responsabilidades, se necesitaba un agente guardián inicial para decidir hacia dónde viajar.
*   **Archivos Creados/Modificados:**
    *   `source/adapters/chains/router_chain.py` **(Creado)**
    *   `source/domain/router.py` **(Creado)**
*   **Detalle Sistémico:**
    *   **En Cadena (`router_chain.py`):** Configura un esquema de análisis sintáctico (AST) a través del modelo `RouterResponse`. El sistema pasa la orden paramétrica al LLM usando inferencia probabilística fría (Temperatura 0) y recibe de vuelta el Tema correspondiente (`selected_topic`).
    *   **En Nodo (`router.py`):** Transfiere la ejecución. La subrutina inicial en el árbol revisa manualmente si la bandera local `state["is_return_in_progress"]` es verdadera. Si es así, **anula e ignora** la cadena inferencial (bypass), marcándola forzosamente para continuar hacia el agente de devoluciones, manteniendo la memoria viva. Si es falsa, continúa infiriendo desde el `router_chain` y marca hacia dónde dirigir el pase en `state["selected_agent"]`.
*   **Relación Posterior:** El string emitido y anclado aquí en el estado guiará la compuerta lógica `route_to_agent` elaborada en la Fase 5.

### FASE 3: Desarrollo de Capa Modular Especializada (Los Trabajadores Multiturno)
*   **Problema Original:** Solo existía un único Agente pre-programado ("Amnésico" y genérico).
*   **Archivos Creados/Modificados:**
    *   `source/adapters/chains/returns_chain.py` **(Creado)**
    *   `source/domain/handle_returns.py` **(Creado)**
    *   `source/adapters/chains/general_chain.py` **(Refactorizado)**
    *   `source/domain/handle_general.py` **(Refactorizado)**
*   **Detalle Sistémico:**
    *   **El Experto (`handle_returns.py` y su cadena `returns_chain.py`):** Este Agente fue intrínsecamente diseñado como una Máquina de Estados Finitos para resolver la "amnesia" durante una queja interactiva de múltiples pasos. La *Base de Conocimientos* advertía que los pagos no debían ser reembolsados instantáneamente sin pedir detalles. Entonces la cadena Pydantic (`ReturnsResponse`) engrana propiedades `next_step` e iteraciones de la bandera `is_return_in_progress`. Modificando cíclicamente estas banderas, el bot no suelta el flujo y continúa haciendo preguntas ("¿Qué causó el daño?") hasta culminar en logística sin que el `Router` (Fase 2) interfiera.
    *   **El General (`handle_general.py` y su cadena `general_chain.py`):** Ahora de-saturado del peso de las Devoluciones, fue reescrito para absorber *solo* de la `SCENARIO_KNOWLEDGE_BASE` la directiva específica indicada para su Tema asignado (`state["selected_topic"]`). A nivel de `general_chain.py`, se inyectó un sistema estricto (`GeneralResponse`) forzando un razonamiento nativo al habla humana colombiana y sin desviarse del *instruction_set*.
*   **Relación Posterior:** Ambos agentes se convierten en el punto final del sistema. Son llamados condicionalmente por la Fase 5 e introducen el payload final de "Respuesta" del cual el usuario recibe un string.

### FASE 4: Capa de Protección y Mitigación de Vulnerabilidades (El Sanitizador)
*   **Problema Original:** Los datos simulados en línea de un usuario ("Su email, número de celular, historial médico, tarjetas asociadas, direcciones") pasaban indiscriminadamente al JSON masivo del *System Prompt*. Si alguien preguntaba por promociones genéricas, aún así exponían tokens con datos privados sensibles, un factor severo de "Data Leakage" en las arquitecturas MLOps.
*   **Archivos Modificados:**
    *   `source/adapters/utils/data_filter.py` **(Refactorizado)**
*   **Detalle Sistémico:** Para resolverlo, el filtro fue reprogramado. Ahora, cada Nodo en la "Fase 3", antes de construir su prompt, se comunica con esta utilidad paramétrica. Extraen temporal y dinámicamente a una memoria volátil un `dict` seguro que retiene las *propiedades base* obligatorias pero se ajusta a los `relevant_fields` listados en la `knowledge_base` (`topic`). Ej: Si son preguntas de perfil, se eliminan las órdenes; Si es envío, se elimina el saldo de pagos.
*   **Relación Posterior:** La minimización drástica recorta los tokens en un 80%, acelerando la latencia del grafo sin sacrificar validaciones asíncronas de base de datos.

### FASE 5: Re-Construcción Topográfica del Orquestador (El Cableado del Graph)
*   **Problema Original:** El sistema estaba cableado en línea recta asumiendo un único agente existente entre `fetch_data` y `END`.
*   **Archivos Modificados:**
    *   `source/application/graph.py` **(Radicalmente Refactorizado)**
*   **Detalle Sistémico:** 
    1. El inicio del grafo `fetch_user_data` fue conectado al nuevo nodo inicial ciego formulado: `router_node`.
    2. En el espacio liberado restante, se introdujo una **Compuerta de Rutas Booleana** (`add_conditional_edges`).
    3. Se programó la lógica de decisión `route_to_agent`, la cual lee pasivamente el registro de mutación escrito por la Función Nodo-Enrutador en la Fase 2 (`state.get("selected_agent")`), y levanta el puente apropiado invocando internamente ya sea las dependencias de `handle_returns` o `handle_general`.
    4. Ambos Nodos ahora dictan una ruta directa hacia el terminador de ejecución `END`.
*   **Relación Final:** Esto cerró el ciclo del ecosistema LangGraph. Una arquitectura limpia sin acoplamiento estrecho, permitiendo la adición de Nodos Especialistas ilimitados en semanas por un equipo grande, simplemente añadiendo compuertas al enrutador central sin afectar el rendimiento cross-generativo.
