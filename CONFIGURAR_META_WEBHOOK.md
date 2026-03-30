# Configuración del Webhook en Meta for Developers

Sigue estos pasos exactos para conectar el agente IA de Transfer Auto con tu número de WhatsApp Business API.

## 1. Configurar el Webhook

1. Ve a [Meta for Developers](https://developers.facebook.com/) e inicia sesión.
2. Selecciona tu aplicación de Transfer Auto.
3. En el menú lateral izquierdo, ve a **WhatsApp** > **Configuration** (Configuración).
4. En la sección "Webhook", haz clic en el botón **Edit** (Editar).
5. Rellena los campos con los siguientes datos:
   - **Callback URL**: `https://transfer-auto-agent.onrender.com/webhook`
   - **Verify Token**: `ASISTENTIA TRANSFERAUTO AGENT`
6. Haz clic en **Verify and Save** (Verificar y guardar).

*Nota: Si el botón dice "Verify and Save", el sistema hará una petición a Render. Si todo está correcto, la ventana se cerrará sin errores.*

## 2. Suscribirse a los eventos

1. En la misma página de Configuración, debajo de donde acabas de configurar el webhook, verás una sección llamada **Webhook fields** (Campos del webhook).
2. Haz clic en **Manage** (Administrar).
3. Busca el campo llamado `messages` en la lista.
4. Haz clic en **Subscribe** (Suscribirse) en la fila de `messages`.
5. Haz clic en **Done** (Listo).

## 3. Test de funcionamiento

Para verificar que todo funciona correctamente, envía un mensaje de WhatsApp desde tu teléfono personal al número de WhatsApp Business configurado (el que tiene el ID `1097986553388736`).

**Mensaje de prueba:**
> Hola

**Respuesta esperada del agente:**
> Hola 👋 Soy Asistentia, de Transfer Auto.
> 
> ¿Qué trámite necesitas realizar?
> 
> 1️⃣ Cambio de titularidad
> 2️⃣ Notificación de venta
> 3️⃣ Baja de vehículo
> 4️⃣ Otro trámite
> 
> Escribe el número 👇

Si recibes esta respuesta, ¡el sistema está 100% operativo en producción!
