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

def get_agent_response(messages: list, user_state: dict, session_context: dict = None) -> dict:
    """
    Llama a la API de OpenAI y devuelve la respuesta estructurada.
    """
    if session_context is None:
        session_context = {}
        
    system_prompt = build_system_prompt()
    
    modo = session_context.get("modo_usuario", "operativo_transfer_auto")
    uso = session_context.get("uso_mes_actual", {})
    limites = session_context.get("limites_mes", {})
    es_admin = session_context.get("es_admin", False)

    mode_instructions = f"\n\nMODO ACTIVO: {modo}\n"

    if modo == "operativo_transfer_auto":
        mode_instructions += "COMPORTAMIENTO: Solo guiar al cierre. No analizar casos. No explicar riesgos. No dar información que no lleve a contratar. Detectar trámite, recoger datos, calcular precio, llevar a pago, pedir documentación.\n"
    elif modo == "lite":
        heavy_consumidos = uso.get("analisis_heavy_consumidos", 0)
        heavy_limite = limites.get("analisis_heavy", 1)
        heavy_disponibles = max(0, heavy_limite - heavy_consumidos) if heavy_limite != -1 else -1
        mode_instructions += f"COMPORTAMIENTO: Orientar, resolver dudas, análisis básico de viabilidad, detección de riesgos simples. Análisis heavy disponibles este mes: {heavy_disponibles if heavy_disponibles != -1 else 'ilimitados'}. Si el usuario pide análisis heavy y ya no tiene disponibles, responder: 'Ya has usado tu análisis avanzado de este mes en el plan Lite. Si quieres seguir con análisis complejos ilimitados, necesitas el plan Pro. ¿Quieres que te dejemos el trámite hecho nosotros?' Siempre terminar en conversión.\n"
    elif modo == "pro":
        mode_instructions += "COMPORTAMIENTO: Análisis completo, detección de riesgos legales y administrativos, estimación de viabilidad, comparativas de operaciones, optimización fiscal, escenarios múltiples. Siempre terminar ofreciendo el paso a tramitación. Formato de análisis: incluir viabilidad (alta/media/baja/nula), riesgo_legal (alto/medio/bajo), recomendación.\n"
    elif modo == "admin":
        mode_instructions += "COMPORTAMIENTO: Modo administrador. Puedes recibir y ejecutar comandos /admin. Puedes guardar, corregir y desactivar reglas en la memoria del sistema. Puedes enviar mensajes manuales, confirmar pagos y cambiar modos de usuario (solo si numero_autorizado=true).\n"

    from memory_store import get_active_rules
    tramite = user_state.get("tramite_principal", "")
    ccaa = user_state.get("comunidad_autonoma", "")
    active_rules = get_active_rules(tramite=tramite, ccaa=ccaa, modo=modo)

    if active_rules:
        rules_text = "\n\nREGLAS ACTIVAS DEL SISTEMA:\n"
        for rule in active_rules[:10]:  # máximo 10 reglas para no saturar el contexto
            rules_text += f"- [{rule['tipo'].upper()}] {rule['titulo']}: {rule['contenido']}\n"
        full_system_prompt = system_prompt + mode_instructions + rules_text
    else:
        full_system_prompt = system_prompt + mode_instructions
    
    # Añadir el estado actual al system prompt para dar contexto al modelo
    context_prompt = f"""
{full_system_prompt}

ESTADO ACTUAL DEL EXPEDIENTE:
```json
{json.dumps(user_state, ensure_ascii=False, indent=2)}
```

INSTRUCCIÓN OBLIGATORIA:
Debes responder SIEMPRE con un objeto JSON válido que cumpla esta estructura exacta:
{{
  "respuesta_agente": "texto que el agente debe enviar al cliente",
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
            "respuesta_agente": "Hola, soy Asistentia de Transfer Auto. ¿En qué te puedo ayudar?",
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
            "respuesta_agente": "Hola, soy Asistentia de Transfer Auto. ¿En qué te puedo ayudar?",
            "estado_actual": user_state.get("expediente_estado", "inicio"),
            "datos_detectados": {},
            "datos_faltantes": [],
            "siguiente_accion": "esperar_respuesta",
            "prioridad": "media",
            "validacion": {"ok": True, "errores": []}
        }
