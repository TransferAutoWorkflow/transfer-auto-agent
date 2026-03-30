import requests
import logging
from config import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID

logger = logging.getLogger(__name__)

BASE_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}

def send_message(phone: str, text: str) -> bool:
    """Envía un mensaje de texto simple."""
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {"body": text}
    }
    return _send_request(payload)

def send_interactive_list(phone: str, header: str, body: str, options: list) -> bool:
    """Envía un mensaje interactivo de tipo lista."""
    rows = [{"id": opt["id"], "title": opt["title"]} for opt in options]
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header} if header else None,
            "body": {"text": body},
            "footer": {"text": "Selecciona una opción"},
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Opciones disponibles",
                        "rows": rows
                    }
                ]
            }
        }
    }
    
    # Eliminar header si es None
    if not payload["interactive"]["header"]:
        del payload["interactive"]["header"]
        
    return _send_request(payload)

def send_quick_reply(phone: str, body: str, buttons: list) -> bool:
    """Envía un mensaje interactivo con botones de respuesta rápida (máx 3)."""
    btn_objects = [
        {
            "type": "reply",
            "reply": {
                "id": btn["id"],
                "title": btn["title"]
            }
        } for btn in buttons[:3]
    ]
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": btn_objects
            }
        }
    }
    return _send_request(payload)

def mark_as_read(message_id: str) -> bool:
    """Marca un mensaje entrante como leído."""
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    return _send_request(payload)

def _send_request(payload: dict) -> bool:
    """Función interna para enviar la petición a la API de Meta."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        logger.warning("WhatsApp credentials not configured. Mocking send.")
        logger.info(f"Mock send: {payload}")
        return True
        
    try:
        response = requests.post(BASE_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return False
