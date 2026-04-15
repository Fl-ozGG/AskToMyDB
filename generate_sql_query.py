from pydantic import BaseModel
import sqlglot
from sqlglot import exp
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=OPENAI_API_KEY)


class SQLGuardError(Exception):
    pass

class Intent(BaseModel):
    intent: str
    accuracy: float
    action: str


def generate_sql_query_from_llm(intent: Intent):

    intent_type = intent.intent
    action = intent.action
    
   
    system_prompt = """Eres un experto en SQL. 
    
        Tu tabla es: ventas
        Columnas: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
        
        REGLAS:
        1. Responde SOLO con el SQL query. Sin explicaciones.
        2. Sin comentarios SQL.
        3. Usa nombres de columna exactos.
        4. No añadas LIMIT (se agregará automáticamente).
        5. La respuesta debe ser SQL válido y ejecutable.
        """
    
    specific_prompts = {
        "TEMPORAL": f"""Genera un SELECT que analice cambios entre períodos de tiempo.
        
        Acción esperada: {action}
        
        Ejemplo de output esperado (no ejecutes esto, es solo referencia):
        SELECT DATE_TRUNC('month', InvoiceDate) as mes, SUM(Quantity * UnitPrice) as total_ventas FROM ventas GROUP BY DATE_TRUNC('month', InvoiceDate) ORDER BY mes DESC
        
        Ahora genera el SQL para: {action}""",
        
                "CATEGÓRICA": f"""Genera un SELECT que filtre y agrupe por categoría/producto.
                
        Acción esperada: {action}
        
        Ejemplo de output esperado:
        SELECT StockCode, Description, SUM(Quantity) as total_qty, SUM(Quantity * UnitPrice) as total_ventas FROM ventas GROUP BY StockCode, Description ORDER BY total_ventas DESC
        
        Ahora genera el SQL para: {action}""",
        
                "AGREGACIÓN": f"""Genera un SELECT que calcule totales, promedios, conteos.
                
        Acción esperada: {action}
        
        Ejemplo de output esperado:
        SELECT SUM(Quantity * UnitPrice) as total_ventas, COUNT(DISTINCT InvoiceNo) as num_invoices, AVG(Quantity) as avg_qty FROM ventas
        
        Ahora genera el SQL para: {action}""",
        
                "VARIACIÓN": f"""Genera un SELECT que calcule cambios porcentuales o diferencias.
                
        Acción esperada: {action}
        
        Nota: Si necesitas comparar períodos, usa subconsultas o WINDOW functions.
        Ahora genera el SQL para: {action}""",
        
                "RANKING": f"""Genera un SELECT que ordene y limite resultados por ranking.
                
        Acción esperada: {action}
        
        Ejemplo de output esperado:
        SELECT StockCode, Description, SUM(Quantity * UnitPrice) as total_ventas FROM ventas GROUP BY StockCode, Description ORDER BY total_ventas DESC
        
        Ahora genera el SQL para: {action}"""
    }
    
    user_prompt = specific_prompts.get(intent_type, specific_prompts["AGREGACIÓN"])
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,  
        max_tokens=500
    )
    sql_query = response.choices[0].message.content.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    return sql_query
    
ALLOWED_TABLES = {"ventas"}
MAX_LIMIT = 100

"""
    Valida que el SQL sea seguro y cumpla con restricciones.
    Checks:
    1. Solo SELECT permitido
    2. Sin operaciones de escritura (INSERT, UPDATE, DELETE, DROP, CREATE)
    3. Solo tablas autorizadas
    4. Auto-añade LIMIT si no existe
    5. Máximo 100 filas
"""

def validate_sql(sql: str) -> str:
    try:
        parsed = sqlglot.parse_one(sql)
    except Exception as e:
        raise SQLGuardError(f"Invalid SQL syntax: {e}")

    if not isinstance(parsed, exp.Select):
        raise SQLGuardError("Only SELECT queries are allowed")

    forbidden_nodes = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create)
    if parsed.find(forbidden_nodes):  # type: ignore
        raise SQLGuardError("Write operations are not allowed")

    tables = {t.name for t in parsed.find_all(exp.Table)}

    if not tables.issubset(ALLOWED_TABLES):
        raise SQLGuardError(f"Unauthorized tables: {tables - ALLOWED_TABLES}")

    limit_expr = parsed.args.get("limit")

    if limit_expr is None:
        parsed.set("limit", exp.Limit(this=exp.Literal.number(10)))

    else:
        try:
            limit_value = int(limit_expr.expression.name)
            if limit_value > MAX_LIMIT:
                parsed.set("limit", exp.Limit(this=exp.Literal.number(MAX_LIMIT)))
        except:
            parsed.set("limit", exp.Limit(this=exp.Literal.number(100)))

    if ";" in sql.strip().rstrip(";"):
        raise SQLGuardError("Multiple statements are not allowed")

    return parsed.sql()
