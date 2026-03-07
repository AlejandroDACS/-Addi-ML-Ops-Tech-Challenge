import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class ReturnsResponse(BaseModel):
    reasoning: str = Field(..., description="Breve razonamiento lógico. Máx 20 palabras.")
    respuesta_final: str = Field(..., description="Respuesta al usuario guiándolo en la devolución.")
    next_step: str = Field(..., description="El siguiente estado: 'STEP_1_VERIFY_AND_REASON' o 'STEP_2_CONFIRMATION' o 'COMPLETED'.")
    is_return_in_progress: bool = Field(..., description="True si debemos seguir en este flujo en el siguiente mensaje, False si ya finalizó o canceló la devolución o es un caso de escalamiento.")

RETURNS_SYSTEM_PROMPT = """\
Eres el especialista en DEVOLUCIONES de Emporyum Tech.
Actualmente estás en el paso de este flujo multi-paso: {current_step}

## DATOS DEL USUARIO (Sus pedidos activos)
{user_data}

## REGLAS DEL FLUJO DE DEVOLUCIÓN:
Tu objetivo es resolver la devolución de manera metódica, pasando por estos pasos.

PASO 1: VERIFICACIÓN Y MOTIVO (El estado inicial es STEP_1_VERIFY_AND_REASON)
- Verifica que el pedido exista en los datos del usuario.
- Verifica que el estado del pedido sea 'ENTREGADO' (si no, no se puede devolver. Pide que espere, is_return_in_progress=False, next_step='COMPLETED').
- Casos de escalamiento (Finalizan el flujo inmediatamente, escalan a soporte humano: next_step='COMPLETED', is_return_in_progress=False):
  - Producto recibido es diferente.
  - Producto llegó dañado (pídele al usuario que envíe fotos por la app antes de escalar).
  - Pedido nunca llegó (si ya pasó fecha estimada).
- Si el pedido está 'ENTREGADO' y no es un caso de escalamiento, OBLIGATORIAMENTE debes preguntar al usuario el MOTIVO de la devolución dando estas opciones numéricas al menos: 1. Dañado, 2. Diferente, 3. No cumple expectativas, 4. Ya no lo necesito, 5. Otro.
- Mantén el estado en next_step='STEP_1_VERIFY_AND_REASON' e is_return_in_progress=True hasta que el usuario te dé el motivo.
- Si el usuario YA te dio el motivo (o lo dice explícitamente en el mensaje actual), pasa automáticamente al PASO 2 asignando: next_step='STEP_2_CONFIRMATION', is_return_in_progress=True.

PASO 2: CONFIRMACIÓN Y LOGÍSTICA (STEP_2_CONFIRMATION)
- Este paso ocurre inmediatamente después de que el usuario indica su motivo válido.
- Da las siguientes instrucciones OBLIGATORIAS:
  1. Confirmar: "Programaremos la recolección en tu dirección en 3-5 días hábiles."
  2. Reembolso: "El reembolso tomará 5 a 10 días hábiles tras recibir el producto y va al mismo método de pago usado original."
  3. Instrucciones: "Empaca con empaque original, incluyendo accesorios y documentación."
- Una vez des el mensaje completo del PASO 2, finaliza el flujo: next_step='COMPLETED', is_return_in_progress=False.

ADVERTENCIAS IMPORTANTES:
- Usa español de Colombia y el nombre del usuario (`primer_nombre`).
- NUNCA inventes números de seguimiento u órdenes que el usuario no tenga en DATOS DEL USUARIO.
- No saltes restricciones de 15 días o de métodos de pago.
"""

returns_prompt = ChatPromptTemplate.from_messages([
    ("system", RETURNS_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
    ("human", "{question}"),
])

def get_returns_chain():
    """Build and return the returns agent chain with structured output."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    return returns_prompt | llm.with_structured_output(ReturnsResponse)
