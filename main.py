import logging
from fastapi import FastAPI, Request, Response, HTTPException
from config import WHATSAPP_VERIFY_TOKEN
from state_manager import state_manager
from agent import get_agent_response
from whatsapp_client import send_message, mark_as_read
from itp_calculator import calcular_precio

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
                    
                    # Ignorar actualizaciones de estado (entregado, leído, etc.)
                    if "messages" in value:
                        for message in value["messages"]:
                            await process_message(message, value["metadata"]["phone_number_id"])
                            
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error"}

async def process_message(message: dict, phone_number_id: str):
    """Procesa un mensaje individual entrante."""
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
    
    # 4. Añadir al historial
    state_manager.add_message(phone, "user", content)
    
    # 5. Llamar al agente IA
    history = state_manager.get_history(phone)
    agent_response = get_agent_response(history, user_state)
    
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
        msg_text = agent_response.get("mensaje_usuario", "")
        if "XXX" in msg_text:
            msg_text = msg_text.replace("XXX", str(precio_desglose["total"]))
            agent_response["mensaje_usuario"] = msg_text
            
    elif siguiente_accion == "enviar_enlace_pago":
        msg_text = agent_response.get("mensaje_usuario", "")
        if "[LINK PAGO" in msg_text:
            # Generar link mock para el MVP
            link = f"https://pago.transferauto.es/checkout/{phone}"
            msg_text = msg_text.replace("[LINK PAGO / WHATSAPP FLOW]", link).replace("[LINK PAGO]", link)
            agent_response["mensaje_usuario"] = msg_text
            
    elif siguiente_accion == "derivar_humano":
        # En el MVP, simplemente registramos
        logger.warning(f"Derivando a humano el expediente de {phone}")
        state_manager.update_state(phone, {"notas_internas": "Derivado a humano"})
    
    # 7. Enviar respuesta al usuario
    respuesta_texto = agent_response.get("mensaje_usuario", "Lo siento, no he podido procesar tu solicitud.")
    
    # Añadir respuesta del bot al historial
    state_manager.add_message(phone, "assistant", respuesta_texto)
    
    # Enviar por WhatsApp
    send_message(phone, respuesta_texto)
