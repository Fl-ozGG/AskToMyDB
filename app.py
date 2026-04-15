from openai import OpenAI
import os
from dotenv import load_dotenv
import json

from generate_sql_query import Intent, generate_sql_query_from_llm
from usage_logger import LLMUsage, log_usage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=OPENAI_API_KEY)


def ask_to_llm(query: str):

    intent_of_user_query, usage = get_intent(query)
    
    intent = intent_of_user_query.get("intent", "")
    accuracy = intent_of_user_query.get("accuracy", 0.0)
    action = intent_of_user_query.get("action", "")

    data_of_user_query = Intent(intent=intent, accuracy=float(accuracy), action=action)

    db_query = create_db_query(data_of_user_query)

    return intent_of_user_query


def create_db_query(intent: Intent):

    return generate_sql_query_from_llm(intent)


def get_intent(query: str):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "clasificar_pregunta",
                "description": "Clasificador de intención",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "enum": [
                                "TEMPORAL",
                                "CATEGÓRICA",
                                "AGREGACIÓN",
                                "VARIACIÓN",
                                "RANKING",
                            ],
                        },
                        "accuracy": {"type": "number"},
                        "action": {"type": "string"},
                    },
                    "required": ["intent", "accuracy", "action"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model="gpt-5.4-nano-2026-03-17",
        messages=[
            {"role": "system", "content": "Clasifica la consulta."},
            {"role": "user", "content": query},
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "clasificar_pregunta"}},
    )

    tool_call = response.choices[0].message.tool_calls[0]
    result = json.loads(tool_call.function.arguments)

    usage = LLMUsage(
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        total_tokens=response.usage.total_tokens,
    )

    log_usage("intent_classifier", usage)

    return result, usage
