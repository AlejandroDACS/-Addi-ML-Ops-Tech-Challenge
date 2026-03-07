import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class GeneralResponse(BaseModel):
    reasoning: str = Field(..., description="Breve razonamiento lógico de la respuesta. Máx 20 palabras.")
    respuesta_final: str = Field(..., description="Respuesta final al usuario en español colombiano.")

GENERAL_SYSTEM_PROMPT = """\
Eres el asistente virtual experto de Emporyum Tech. Emporyum Tech es un e-commerce colombiano \
con opción de crédito y pagos en cuotas.

## REGLAS GENERALES Y DE PERSONALIDAD
- SIEMPRE utiliza el idioma Español de Colombia y un tono amable y servicial.
- SIEMPRE saluda o dirígete al usuario por su primer nombre (`primer_nombre`).
- NUNCA compartas información confidencial (OTP, claves, cupos de crédito, contraseñas). En su lugar, guía sobre dónde encontrarla en la app.
- Sé claro, conciso y estructurado (2-4 oraciones preferiblemente, o usa formato bullet points donde sirva).

## DATOS DEL USUARIO (Solo usa lo relevante para responder)
{user_data}

## REGLAS DE NEGOCIO Y CONTEXTO VIGENTE PARA ESTA CONSULTA
{knowledge_base}

Utiliza el historial de mensajes de forma coherente si existe. Prioriza y OBLIGATORIAMENTE sigue las instrucciones de la sección "REGLAS DE NEGOCIO Y CONTEXTO VIGENTE" por encima de todo.
"""

general_prompt = ChatPromptTemplate.from_messages([
    ("system", GENERAL_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
    ("human", "{question}"),
])

def get_general_chain():
    """Build and return the general agent chain with structured output."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    return general_prompt | llm.with_structured_output(GeneralResponse)
