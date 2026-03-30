# Transfer Auto - Agente IA MVP (WhatsApp Webhook)

Este es el MVP funcional del agente IA de Transfer Auto, diseñado para conectarse a WhatsApp Cloud API y desplegarse en Render.com.

## Requisitos Previos

1. Cuenta en [Render.com](https://render.com)
2. Cuenta en [OpenAI](https://platform.openai.com) con saldo para la API
3. Cuenta en [Meta for Developers](https://developers.facebook.com) con una app de WhatsApp configurada

## Instrucciones de Despliegue en Render

1. Sube este código a un repositorio de GitHub.
2. En Render, crea un nuevo **Web Service** y conéctalo a tu repositorio.
3. Render detectará automáticamente el archivo `render.yaml` y configurará el servicio.
4. En la pestaña **Environment** de tu servicio en Render, configura las siguientes variables:
   - `OPENAI_API_KEY`: Tu clave de API de OpenAI.
   - `WHATSAPP_TOKEN`: El token de acceso permanente de tu app de Meta.
   - `WHATSAPP_PHONE_NUMBER_ID`: El ID del número de teléfono de WhatsApp.
   - `WHATSAPP_VERIFY_TOKEN`: Un token inventado por ti (ej. `transfer_auto_secreto_123`).
   - `HONORARIOS_BASE`: (Opcional) Por defecto 99.
   - `RECARGO_URGENCIA`: (Opcional) Por defecto 50.

## Configuración en Meta for Developers

1. Ve a tu app en Meta for Developers > WhatsApp > Configuración de la API.
2. En la sección **Webhooks**, haz clic en **Configurar**.
3. URL de devolución de llamada (Callback URL): `https://tu-app-en-render.onrender.com/webhook`
4. Token de verificación: El mismo que pusiste en `WHATSAPP_VERIFY_TOKEN`.
5. Haz clic en **Verificar y guardar**.
6. En la sección de Webhooks, haz clic en **Administrar** y suscríbete al evento `messages`.

## Pruebas

1. Envía un mensaje de WhatsApp al número configurado.
2. El agente debería responder con el menú inicial.
3. Puedes ver los logs en el panel de Render para depurar cualquier problema.

## Estructura del Proyecto

- `main.py`: Webhook de FastAPI.
- `agent.py`: Integración con OpenAI y lógica del agente.
- `state_manager.py`: Gestión del estado de la conversación por usuario.
- `itp_calculator.py`: Lógica de cálculo de precios e impuestos.
- `whatsapp_client.py`: Cliente para enviar mensajes por WhatsApp API.
- `config.py`: Carga de variables de entorno.
- `system_prompt.txt`: El prompt maestro del agente.
