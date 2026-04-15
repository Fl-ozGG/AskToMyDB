from pydantic import BaseModel
from anthropic import Anthropic
from openai import OpenAI
import os 
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class LLMResponse(BaseModel):
    data: str


client = OpenAI(api_key=OPENAI_API_KEY)


def ask_to_agent(query: str):
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "clasificar_pregunta",
                "description": "Clasificador de intención y extractor de entidades para análisis de datos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "description": "Categoría de análisis: TEMPORAL (comparativa periodos), CATEGÓRICA (producto/región), AGREGACIÓN (totales/promedios), VARIACIÓN (deltas %), RANKING (top/bottom).",
                            "enum": ["TEMPORAL", "CATEGÓRICA", "AGREGACIÓN", "VARIACIÓN", "RANKING"]
                        },
                        "entidades": {
                            "type": "object",
                            "description": "Diccionario con entidades clave. Ej: {período_actual: 'marzo'} para TEMPORAL; {métrica: 'ventas', limit: 5} para RANKING."
                        },
                        "confianza": {
                            "type": "number",
                            "description": "Nivel de certeza de 0 a 1."
                        },
                        "accion": {
                            "type": "string",
                            "description": "Resumen breve de la operación detectada."
                        }
                    },
                    "required": ["intent", "entidades", "confianza", "accion"]
                }
            }
        }
    ]

    response = client.chat.completions.create(
        model="gpt-5.4-nano-2026-03-17",  # O "gpt-4o" para mayor precisión
        messages=[
            {"role":"system","content":"Clasifica la consulta en TEMPORAL, CATEGÓRICA, AGREGACIÓN, VARIACIÓN o RANKING. Devuelve JSON."}
            ,{"role": "user", "content": f"Clasifica: {query}"}],
        tools=tools,
        tool_choice={
            "type": "function",
            "function": {"name": "clasificar_pregunta"},
        },  # Fuerza el uso de la herramienta
    )

    # Extraemos la llamada a la función
    tool_call = response.choices[0].message.tool_calls[0]

    # OpenAI devuelve los argumentos como un string JSON, hay que parsearlo
    import json

    resultado = json.loads(tool_call.function.arguments)

    return resultado
