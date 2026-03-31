import logging
from fastapi import FastAPI, Request, Response, HTTPException
from config import WHATSAPP_VERIFY_TOKEN
from state_manager import state_manager
from agent import get_agent_response
from whatsapp_client import send_message, mark_as_read
from itp_calculator import calcular_precio
from memory_store import add_rule, deactivate_rule, update_rule, get_recent_rules, find_rule

def handle_admin_command(command: str, sender: str) -> str:
    cmd = command.strip()
    
    if cmd.startswith("/admin guardar_regla:"):
        contenido = cmd.replace("/admin guardar_regla:", "").strip()
        rule = add_rule("operational_rule", contenido[:50], contenido, prioridad="alta")
        return f"✅ Regla guardada. ID: {rule['memory_id'][:8]}..."
    
    elif cmd.startswith("/admin corregir_regla:"):
        parts = cmd.replace("/admin corregir_regla:", "").strip().split("=>")
        if len(parts) == 2:
            titulo = parts[0].strip()
            nuevo = parts[1].strip()
            if update_rule(titulo, nuevo):
                return f"✅ Regla actualizada: {titulo}"
            return f"❌ No encontré la regla: {titulo}"
    
    elif cmd.startswith("/admin desactivar_regla:"):
        titulo = cmd.replace("/admin desactivar_regla:", "").strip()
        if deactivate_rule(titulo):
            return f"✅ Regla desactivada: {titulo}"
        return f"❌ No encontré la regla: {titulo}"
    
    elif cmd.startswith("/admin ver_regla:"):
        query = cmd.replace("/admin ver_regla:", "").strip()
        rules = find_rule(query)
        if rules:
            r = rules[0]
            return f"📋 {r['titulo']}\n{r['contenido']}\nID: {r['memory_id'][:8]}... | v{r['version']} | {'✅' if r['activa'] else '❌'}"
        return f"❌ No encontré reglas para: {query}"
    
    elif cmd.strip() == "/admin ultimas_reglas":
        rules = get_recent_rules(5)
        if not rules:
            return "No hay reglas guardadas."
        lines = ["📋 Últimas reglas:"]
        for r in rules:
            lines.append(f"- {r['titulo']} ({r['tipo']}) {'✅' if r['activa'] else '❌'}")
        return "\n".join(lines)
    
    elif cmd.startswith("/admin guardar_caso:"):
        contenido = cmd.replace("/admin guardar_caso:", "").strip()
        rule = add_rule("case_pattern", contenido[:50], contenido, prioridad="alta")
        return f"✅ Caso guardado. ID: {rule['memory_id'][:8]}..."
    
    elif cmd.startswith("/admin mensaje:"):
        parts = cmd.replace("/admin mensaje:", "").strip().split("|", 1)
        if len(parts) == 2:
            numero = parts[0].strip()
            mensaje = parts[1].strip()
            send_message(numero, mensaje)
            return f"✅ Mensaje enviado a {numero}"
    
    elif cmd.startswith("/admin pago_confirmado:"):
        expediente = cmd.replace("/admin pago_confirmado:", "").strip()
        return f"✅ Pago confirmado para expediente: {expediente}"
    
    return "❌ Comando no reconocido. Comandos disponibles: guardar_regla, corregir_regla, desactivar_regla, ver_regla, ultimas_reglas, guardar_caso, mensaje, pago_confirmado"

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Transfer Auto MVP Webhook")

@app.get("/")
async def root():
    return {"status": "ok", "service": "Transfer Auto Agent MVP"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Endpoint para la verificación del webhook de Meta."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return Response(content=challenge, media_type="text/plain")
        else:
            raise HTTPException(status_code=403, detail="Verification token mismatch")
    
    raise HTTPException(status_code=400, detail="Missing parameters")

@app.post("/webhook")
async def handle_webhook(request: Request):
    """Endpoint principal para recibir mensajes de WhatsApp."""
    try:
        body = await request.json()
        
        # Verificar si es un evento de mensaje de WhatsApp
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # Filtrar statuses (no son mensajes)
                    if "statuses" in value:
                        continue
                        
                    # Filtrar mensajes vacíos
                    if "messages" not in value or not value["messages"]:
                        continue
                        
                    for message in value["messages"]:
                        # Filtrar ecos del propio bot
                        phone_number_id = value.get("metadata", {}).get("phone_number_id", "")
                        sender_phone = message.get("from", "")
                        if phone_number_id and sender_phone == phone_number_id:
                            logger.info(f"Ignorando echo message del bot: {sender_phone}")
                            continue
                            
                        # Filtrar mensajes no soportados
                        if message.get("type") not in ["text", "image", "document", "audio", "interactive"]:
                            logger.info(f"Ignorando mensaje de tipo no soportado: {message.get('type')}")
                            continue
                            
                        await process_message(message, phone_number_id, body)
                            
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error"}

async def process_message(message: dict, phone_number_id: str, body: dict = None):
    """Procesa un mensaje individual entrante."""
    if body is None:
        body = {}
        
    phone = message.get("from")
    message_id = message.get("id")
    msg_type = message.get("type")
    
    if not phone or not message_id:
        return
        
    # 1. Marcar como leído
    mark_as_read(message_id)
    
    # 2. Obtener estado actual
    user_state = state_manager.get_state(phone)
    
    # 3. Extraer contenido del mensaje
    content = ""
    if msg_type == "text":
        content = message["text"]["body"]
    elif msg_type == "interactive":
        interactive = message["interactive"]
        if interactive["type"] == "list_reply":
            content = interactive["list_reply"]["title"]
        elif interactive["type"] == "button_reply":
            content = interactive["button_reply"]["title"]
    elif msg_type in ["image", "document"]:
        # Manejo básico de documentos para el MVP
        doc_id = message[msg_type].get("id")
        content = f"[El usuario ha enviado un {msg_type} con ID: {doc_id}]"
        
        # Registrar en el estado
        docs = user_state.get("documentos_recibidos", [])
        docs.append(f"{msg_type}_{doc_id}")
        state_manager.update_state(phone, {"documentos_recibidos": docs})
    else:
        content = f"[Mensaje no soportado de tipo: {msg_type}]"
        
    logger.info(f"Received message from {phone}: {content}")
    
    # Extraer contexto de sesión del backend (inyectado en cada request)
    session_context = {
        "modo_usuario": body.get("session", {}).get("modo_usuario", "operativo_transfer_auto"),
        "user_id": body.get("session", {}).get("user_id", phone),
        "plan_activo": body.get("session", {}).get("plan_activo", "operativo"),
        "uso_mes_actual": body.get("session", {}).get("uso_mes_actual", {}),
        "limites_mes": body.get("session", {}).get("limites_mes", {}),
        "es_admin": body.get("session", {}).get("es_admin", False),
        "numero_autorizado": body.get("session", {}).get("numero_autorizado", False)
    }

    # Detectar comandos admin
    if session_context.get("es_admin") and content.startswith("/admin"):
        response_text = handle_admin_command(content, phone)
        send_message(phone, response_text)
        return
    
    # 4. Añadir al historial
    state_manager.add_message(phone, "user", content)
    
    # 5. Llamar al agente IA
    history = state_manager.get_history(phone)
    agent_response = get_agent_response(history, user_state, session_context)
    
    logger.info(f"Agent response: {agent_response}")
    
    # 6. Procesar output del agente
    
    # 6.1 Actualizar estado con datos detectados
    datos_detectados = agent_response.get("datos_detectados", {})
    if datos_detectados:
        state_manager.update_state(phone, datos_detectados)
        
    # 6.2 Actualizar estado del expediente
    nuevo_estado = agent_response.get("estado_actual")
    if nuevo_estado:
        state_manager.update_state(phone, {"expediente_estado": nuevo_estado})
        
    # 6.3 Ejecutar acciones especiales
    siguiente_accion = agent_response.get("siguiente_accion")
    
    if siguiente_accion == "calcular_precio":
        # Obtener datos actualizados
        current_state = state_manager.get_state(phone)
        marca = current_state.get("marca", "")
        modelo = current_state.get("modelo", "")
        ano = current_state.get("ano_matriculacion", 2015)
        ccaa = current_state.get("comunidad_autonoma", "Madrid")
        
        # Calcular
        precio_desglose = calcular_precio(marca, modelo, ano, ccaa)
        
        # Actualizar estado
        state_manager.update_state(phone, {"precio_desglose": precio_desglose})
        
        # Inyectar el resultado en el mensaje del agente (reemplazar placeholders si existen)
        # En un sistema real, se volvería a llamar al agente con el precio calculado,
        # pero para el MVP podemos inyectarlo directamente si el agente dejó un placeholder
        msg_text = agent_response.get("respuesta_agente", "")
        if "XXX" in msg_text:
            msg_text = msg_text.replace("XXX", str(precio_desglose["total"]))
            agent_response["respuesta_agente"] = msg_text
            
    elif siguiente_accion == "enviar_enlace_pago":
        msg_text = agent_response.get("respuesta_agente", "")
        if "[LINK PAGO" in msg_text:
            # Generar link mock para el MVP
            link = f"https://pago.transferauto.es/checkout/{phone}"
            msg_text = msg_text.replace("[LINK PAGO / WHATSAPP FLOW]", link).replace("[LINK PAGO]", link)
            agent_response["respuesta_agente"] = msg_text
            
    elif siguiente_accion == "derivar_humano":
        # En el MVP, simplemente registramos
        logger.warning(f"Derivando a humano el expediente de {phone}")
        state_manager.update_state(phone, {"notas_internas": "Derivado a humano"})
    
    # 7. Enviar respuesta al usuario
    respuesta_texto = agent_response.get("respuesta_agente", "Lo siento, no he podido procesar tu solicitud.")
    logger.info(f"Enviando respuesta a {phone}: {respuesta_texto}")
    
    # Añadir respuesta del bot al historial
    state_manager.add_message(phone, "assistant", respuesta_texto)
    
    # Enviar por WhatsApp
    send_message(phone, respuesta_texto)
