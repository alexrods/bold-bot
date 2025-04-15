import os
import logging
from fastapi import FastAPI, Request, HTTPException, Response, BackgroundTasks
from utils.parse_messages import parse_whatsapp_webhook
from utils.send_message import send_text_message, send_image_message
from agents.main import react_agent
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

WEBHOOK_TOKEN = os.environ["WEBHOOK_TOKEN"]

app = FastAPI()

# Globales para historial y sesiones de imágenes
conv_history = {}
image_request_sessions = {}
completed_image_sessions = {}  # Aquí se almacenan los usuarios que ya completaron la solicitud de imágenes

def start_image_request_session(user_id):
    """
    Inicia una sesión de solicitud de imágenes para el usuario.
    Se solicitan las imágenes en el siguiente orden:
      - Frente, Posterior, Perfil Derecho, Perfil Izquierdo, Arriba, Atrás Arriba.
    """
    required_images = ["Frente", "Posterior", "Perfil Derecho", "Perfil Izquierdo", "Arriba", "Atrás Arriba"]
    image_request_sessions[user_id] = {
        "pending": required_images.copy(),  # Imágenes pendientes de ser solicitadas
        "collected": {}  # Se almacenarán las URL de las imágenes recibidas: ej { "Frente": url, ... }
    }
    logger.info(f"Image request session started for user {user_id}")

def image_request_agent(message, user_id):
    """
    Agente encargado de procesar las imágenes recibidas durante el proceso de valoración.
    Se solicita secuencialmente la siguiente lista de fotos: Frente, Posterior, Perfil Derecho,
    Perfil Izquierdo, Arriba, Atrás.
    """
    session = image_request_sessions.get(user_id)
    if not session:
        logger.error(f"No hay sesión de solicitud de imágenes para el usuario {user_id}")
        return

    # Verificar si aún hay imágenes pendientes en la sesión
    if not session["pending"]:
        send_text_message(user_id, "Gracias, un especialista evaluara tu caso y nos pondremos en contacto contigo.")
        # Marcar la sesión como completada para evitar reinicios futuros.
        completed_image_sessions[user_id] = session["collected"]
        del image_request_sessions[user_id]
        return

    # La imagen esperada es la primera en la lista pendiente
    expected_label = session["pending"][0]

    if message.is_image():
        # Se asume que message posee el método get_image_url() para obtener la URL de la imagen recibida
        image_url = message.get_image_url()
        session["collected"][expected_label] = image_url
        logger.info(f"Received image for {expected_label} from user {user_id}: {image_url}")
        session["pending"].pop(0)  # Eliminar la imagen actual de la lista pendiente

        if session["pending"]:
            next_label = session["pending"][0]
            send_text_message(user_id, f"Por favor, envía la foto de: {next_label}.")
            logger.info(f"Requested image for {next_label} from user {user_id}")
        else:
            send_text_message(user_id, "Gracias, un especialista evaluara tu caso y nos pondremos en contacto contigo.")
            logger.info(f"Image request session completed for user {user_id}")
            # Marcar la sesión como completada para evitar volver a pedir imágenes
            completed_image_sessions[user_id] = session["collected"]
            del image_request_sessions[user_id]
    else:
        # Si se recibe texto (o mensaje no imagen) se recuerda al usuario la imagen que se necesita
        send_text_message(user_id, f"Recuerda, por favor envía la foto correspondiente a: {expected_label}.")

def process_message(message, user_id):
    """
    Procesa los mensajes recibidos y mantiene el historial de conversación.
    
    - Si hay una sesión activa de solicitud de imágenes, se usa image_request_agent.
    - Caso contrario, se procesa el mensaje normalmente con react_agent.
    - Además, si react_agent detecta interés en valoración y el usuario no completó previamente el envío,
      se envía una imagen de ejemplo y se inicia la sesión para solicitar las fotos.
    """
    global conv_history, image_request_sessions, completed_image_sessions

    # Inicializar historial del usuario si no existe
    if user_id not in conv_history:
        conv_history[user_id] = []

    # Si hay sesión activa de solicitud de imágenes, priorizar esa lógica
    if user_id in image_request_sessions:
        if message.is_image():
            image_request_agent(message, user_id)
            return
        else:
            current_session = image_request_sessions[user_id]
            if current_session["pending"]:
                expected_label = current_session["pending"][0]
                send_text_message(user_id, f"Recuerda, por favor envía la foto de: {expected_label}.")
            return

    # Procesar mensajes de texto en el flujo normal
    if message.type == "text":
        user_input = message.text["body"]

        # Comando para reiniciar la conversación
        if user_input.strip().upper() == "RESET":
            conv_history[user_id] = []
            if user_id in image_request_sessions:
                del image_request_sessions[user_id]
            if user_id in completed_image_sessions:
                del completed_image_sessions[user_id]
            send_text_message(user_id, "Se ha reiniciado la conversación. ¿En qué puedo ayudarte?")
            return

        logger.info(f"Received text message from {user_id}: {user_input}")

        # Llamar a react_agent pasando el historial de conversación
        agent_result = react_agent(user_input, conv_history.get(user_id, []))
        logger.info(f"Agent result: {agent_result}")

        # Actualizar historial de conversación del usuario
        conv_history[user_id].append({
            "user": user_input,
            "assistant": agent_result.get("final_response", "")
        })
        if len(conv_history[user_id]) > 10:
            conv_history[user_id] = conv_history[user_id][-10:]

        # Enviar respuesta de texto
        send_text_message(user_id, agent_result.get("final_response", ""))
        logger.info(f"Text message sent to {user_id}")

        # Si el agente detecta interés en la valoración, se activa send_image
        # Solo se inicia el flujo de imágenes si el usuario aún no completó el proceso anteriormente
        if agent_result.get("send_image", False) and user_id not in completed_image_sessions:
            # Enviar imagen de ejemplo antes de iniciar la sesión de solicitud
            send_image_message(user_id)
            logger.info(f"Example image sent to {user_id} for valuation instructions.")
            # Iniciar sesión de solicitud de imágenes
            start_image_request_session(user_id)
            first_label = image_request_sessions[user_id]["pending"][0]
            send_text_message(user_id, f"Para continuar con tu valoración, por favor envía la foto de: {first_label}.")
            logger.info(f"Image request initiated for user {user_id}, requesting {first_label}")

    elif message.is_image():
        # Procesar imágenes recibidas que no pertenezcan a una sesión activa de solicitud
        logger.info(f"Received image message from {user_id}")
        response_text = "Hemos recibido tu imagen. ¿En qué puedo ayudarte?"
        conv_history[user_id].append({
            "user": "[IMAGEN]",
            "assistant": response_text
        })
        send_text_message(user_id, response_text)
    else:
        # Mensajes de tipo no soportado
        logger.info(f"Received unsupported message type from {user_id}")
        response_text = "Por el momento solo puedo procesar mensajes de texto. ¿En qué puedo ayudarte?"
        conv_history[user_id].append({
            "user": "[MENSAJE NO SOPORTADO]",
            "assistant": response_text
        })
        send_text_message(user_id, response_text)

@app.get("/webhook")
async def verify_token(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")

    if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain", status_code=200)
    else:
        raise HTTPException(status_code=403, detail="Verification token mismatch")
    
@app.post("/webhook")
async def receive_whatsapp_message(request: Request, background_tasks: BackgroundTasks):
    """
    Procesa el webhook de WhatsApp distinguiendo entre actualizaciones de estado y mensajes nuevos.
    Los mensajes se procesan en segundo plano mediante la función process_message.
    """
    try:
        data = await request.json()
        logger.info(f"Received webhook data: {data}")

        # Se ignoran las actualizaciones de estado (statuses)
        if 'entry' in data and len(data['entry']) > 0:
            entry = data['entry'][0]
            if 'changes' in entry and len(entry['changes']) > 0:
                value = entry['changes'][0].get('value', {})
                if 'statuses' in value:
                    logger.info("Recibido webhook de estado (status update)")
                    return Response(status_code=200)
        
        message = parse_whatsapp_webhook(data)
        user_id = message.get_recipient_number()
        logger.info(f"Processing message from {user_id}: {message}")

        background_tasks.add_task(process_message, message, user_id)
        return Response(status_code=200)

    except Exception as e:
        logger
