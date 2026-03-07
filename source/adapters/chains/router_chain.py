import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from source.adapters.utils.knowledge_base import VALID_TOPICS

load_dotenv()

class RouterResponse(BaseModel):
    reasoning: str = Field(..., description="Breve razonamiento (max 20 palabras) de por qué se seleccionó este tema basado en el mensaje del usuario y su contexto.")
    selected_topic: str = Field(..., description=f"El tema más adecuado. Debe ser EXCEPCIONALMENTE uno de la siguiente lista exacta: {VALID_TOPICS}")

ROUTER_SYSTEM_PROMPT = """\
Eres un enrutador analítico para el asistente virtual de Emporyum Tech.
Tu única responsabilidad es leer la conversación del usuario y clasificar la *intención principal* de su último mensaje \
en una de las siguientes categorías predefinidas:

{topics_list}

REGLAS DE CLASIFICACIÓN:
1. "PRODUCTOS_Y_RECOMENDACIONES": Preguntas sobre recomendaciones de productos, disponibilidad (stock), características, precios o promociones/descuentos aplicables.
2. "PAGOS_Y_CUOTAS": Todo sobre cómo pagar, dudas sobre métodos de pago (PSE, Efecty, Tarjetas), planes de cuotas, cálculos de intereses, pagos atrasados, cupos, o pago anticipado.
3. "PEDIDOS_Y_ENVIOS": Todo sobre seguimiento de despachos ("dónde está mi pedido"), tiempos de entrega, o cancelar un pedido que no ha sido entregado.
4. "DEVOLUCIONES": Cualquier intención de hacer una devolución de dinero, retorno físico de un producto, cambios porque llegó dañado o no es lo esperado.
5. "CUENTA_Y_APP": Ayuda técnica con la aplicación móvil/web, problemas iniciando sesión, restablecer contraseña, notificaciones que no llegan, seguridad (robo, phishing) o editar perfil.
6. "FUERA_DE_ALCANCE": Preguntas de la hora, clima, consultas de cultura general que no sean de Emporyum Tech.

Analiza cuidadosamente el mensaje del usuario y el historial reciente de la conversación para entender el contexto (especialmente si es una respuesta corta a una pregunta anterior).
"""

router_prompt = ChatPromptTemplate.from_messages([
    ("system", ROUTER_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
    ("human", "{question}"),
])

def get_router_chain():
    """Build and return the router chain with structured output."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    return router_prompt | llm.with_structured_output(RouterResponse)
