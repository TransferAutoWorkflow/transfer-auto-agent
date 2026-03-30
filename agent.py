import json
import logging
import os
from openai import OpenAI
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Inicializar cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def build_system_prompt() -> str:
    """Lee el system prompt desde el archivo."""
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading system prompt: {e}")
        return "Eres Asistentia, el agente experto en tramitación administrativa de vehículos en España de Transfer Auto."

def get_agent_response(messages: list, user_state: dict) -> dict:
    """
    Llama a la API de OpenAI y devuelve la respuesta estructurada.
    """
    system_prompt = build_system_prompt()
    
    # Añadir el estado actual al system prompt para dar contexto al modelo
    context_prompt = f"""
{system_prompt}

ESTADO ACTUAL DEL EXPEDIENTE:
```json
{json.dumps(user_state, ensure_ascii=False, indent=2)}
```

INSTRUCCIÓN OBLIGATORIA:
Debes responder SIEMPRE con un objeto JSON válido que cumpla esta estructura exacta:
{{
  "mensaje_usuario": "string",
  "estado_actual": "string",
  "datos_detectados": {{}},
  "datos_faltantes": ["string"],
  "siguiente_accion": "string",
  "prioridad": "alta|media|baja",
  "validacion": {{"ok": true, "errores": []}}
}}
"""

    api_messages = [{"role": "system", "content": context_prompt}]
    
    # Añadir historial (limitado a los últimos 10 mensajes para no exceder contexto)
    for msg in messages[-10:]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
        
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=api_messages,
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from OpenAI: {e}")
        # Fallback de emergencia
        return {
            "mensaje_usuario": "Lo siento, ha habido un error técnico. ¿Puedes repetir tu último mensaje?",
            "estado_actual": user_state.get("expediente_estado", "inicio"),
            "datos_detectados": {},
            "datos_faltantes": [],
            "siguiente_accion": "esperar_respuesta",
            "prioridad": "media",
            "validacion": {"ok": True, "errores": []}
        }
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return {
            "mensaje_usuario": "En este momento nuestros sistemas están ocupados. Por favor, inténtalo de nuevo en unos minutos.",
            "estado_actual": user_state.get("expediente_estado", "inicio"),
            "datos_detectados": {},
            "datos_faltantes": [],
            "siguiente_accion": "esperar_respuesta",
            "prioridad": "media",
            "validacion": {"ok": True, "errores": []}
        }
