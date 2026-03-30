# Cómo renovar el WHATSAPP_TOKEN en Meta for Developers

## Diagnóstico

El token temporal de WhatsApp Cloud API **expira cada 24 horas**. Cuando expira, el agente recibe los mensajes pero no puede enviar respuestas (error 401 Unauthorized).

**Solución permanente recomendada:** Generar un token de acceso permanente (System User Token) que no expira.

---

## OPCIÓN A — Token permanente (recomendado para producción)

### Paso 1: Crear un System User en Business Manager

1. Ve a [business.facebook.com](https://business.facebook.com)
2. En el menú lateral, selecciona **Configuración del negocio** (Business Settings)
3. Ve a **Usuarios** → **Usuarios del sistema**
4. Haz clic en **Agregar** y crea un usuario de tipo **Admin**
5. Dale un nombre (ej: `transfer-auto-agent`)

### Paso 2: Asignar activos al System User

1. Con el System User seleccionado, haz clic en **Agregar activos**
2. Selecciona **Apps** → elige tu app de WhatsApp
3. Activa el permiso **Control total** (Full control)
4. Haz clic en **Guardar cambios**

### Paso 3: Generar el token permanente

1. Con el System User seleccionado, haz clic en **Generar nuevo token**
2. Selecciona tu app de la lista
3. En los permisos, activa:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
4. En **Caducidad del token**, selecciona **Nunca** (Never)
5. Haz clic en **Generar token**
6. **Copia el token inmediatamente** — no se vuelve a mostrar

### Paso 4: Actualizar la variable de entorno en Render

1. Ve a [dashboard.render.com](https://dashboard.render.com)
2. Selecciona el servicio `transfer-auto-agent`
3. Ve a **Environment** en el menú lateral
4. Busca la variable `WHATSAPP_TOKEN`
5. Haz clic en el icono de edición (lápiz)
6. Pega el nuevo token permanente
7. Haz clic en **Save Changes**
8. Render hará un redeploy automático en ~1 minuto

---

## OPCIÓN B — Renovar el token temporal (solución rápida)

Si solo necesitas volver a funcionar ahora mismo y no tienes acceso a Business Manager:

### Paso 1: Obtener nuevo token temporal

1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. Selecciona tu app
3. En el menú lateral, ve a **WhatsApp** → **API Setup** (o **Configuración de la API**)
4. En la sección **Temporary access token**, haz clic en el botón de copiar
5. Este token es válido por **24 horas**

### Paso 2: Actualizar en Render

1. Ve a [dashboard.render.com](https://dashboard.render.com)
2. Selecciona el servicio `transfer-auto-agent`
3. Ve a **Environment**
4. Edita la variable `WHATSAPP_TOKEN` con el nuevo token
5. Guarda — Render redesplegará automáticamente

---

## Verificación

Tras actualizar el token, verifica que funciona enviando un mensaje de prueba al número de WhatsApp. Si el agente responde, el token está activo.

También puedes verificar desde la terminal:

```bash
curl -s -X POST "https://transfer-auto-agent.onrender.com/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{"id": "TEST","changes": [{"value": {"messaging_product": "whatsapp","metadata": {"display_phone_number": "34600000000","phone_number_id": "1097986553388736"},"contacts": [{"profile": {"name": "Test"},"wa_id": "34600000001"}],"messages": [{"from": "34600000001","id": "test_001","timestamp": "1234567890","text": {"body": "Hola"},"type": "text"}]},"field": "messages"}]}]
  }'
```

Si devuelve `{"status":"ok"}` y el usuario recibe una respuesta en WhatsApp, el token está funcionando.

---

## Nota importante

El error exacto que causó la interrupción fue:

```
Error validating access token: Session has expired on Monday, 30-Mar-26 16:00:00 PDT.
OAuthException code 190, error_subcode 463
```

Esto confirma que era un token temporal de 24h. **Para producción, usa siempre el System User Token permanente (Opción A).**
