import re
import json
from AI.get_responses import openAI_response
from agents.informativo import info_agent

def react_agent(user_input, conversation_history=None):
    """
        Agente conversacional para BOLD que utiliza RAG a través de info_agent.
        
        El agente utiliza openAI_response para detectar la intención del usuario de iniciar una valoración.
        Se evalúa el mensaje del usuario para ver si expresa interés en una valoración (para injertos de cabello).
        Si se detecta la intención, se activa la bandera send_image y se añade un mensaje complementario en la respuesta.
        Se evita incluir invitaciones a visitar las clínicas, puesto que la valoración inicial se realiza vía WhatsApp.

        Args:
            user_input (str): Mensaje o consulta del usuario.
            conversation_history (list, optional): Historial de conversaciones previas.
        
        Returns:
            dict: Diccionario con la respuesta final, flag send_image y otros metadatos.
    """

    # 1. Detectar saludos casuales
    casual_greetings = [
        "hola", "hello", "hey", "buenos días", "buenas tardes", 
        "buenas noches", "saludos", "qué tal", "como estas", "cómo estás"
    ]
    is_casual_greeting = any(greet in user_input.lower() for greet in casual_greetings) and len(user_input.split()) < 5
    if is_casual_greeting and (not conversation_history or len(conversation_history) < 2):
        final_response = "¡Hola! Soy el asistente virtual de BOLD, clínica especializada en restauración capilar. ¿En qué puedo ayudarte hoy?"
        return {
            "success": True,
            "actions_taken": [],
            "final_response": final_response,
            "message_content": final_response,
            "send_image": False,
            "info_context": ""
        }

    # 2. Utilizar openAI_response para detectar la intención de valoración
    intent_sys_prompt = """
        Eres un asistente experto en detección de intenciones. 
        Analiza el siguiente mensaje del usuario y determina si expresa interés en realizar una valoración para injertos de cabello, a través de WhatsApp. 
        Responde únicamente en formato JSON con la siguiente estructura:
        {"is_valuation_interest": true} 
        o 
        {"is_valuation_interest": false}

        El mensaje es:
    """
    # Componemos el prompt para la detección de intención
    intent_prompt = intent_sys_prompt + "\n" + user_input

    # Llamar a openAI_response para detectar la intención
    intent_response_text = openAI_response(intent_prompt, user_input)
    send_image = False
    try:
        parsed_intent = json.loads(intent_response_text)
        send_image = parsed_intent.get("is_valuation_interest", False)
    except Exception as e:
        # En caso de error en el parseo, se asume que no hay intención
        send_image = False

    # 3. Construcción del contexto de conversación
    if conversation_history:
        conversation_summary = " ".join(
            [f"Usuario: {ex.get('user', '')} - Asistente: {ex.get('assistant', '')}" 
             for ex in conversation_history[-3:]]
        )
        combined_question = f"{user_input}\nContexto previo: {conversation_summary}"
    else:
        combined_question = user_input

    # 4. Llamar a info_agent para obtener la respuesta enriquecida a partir de RAG
    agent_response = info_agent(combined_question)

    # 5. Limpiar la respuesta eliminando invitaciones a visitar clínicas (ya que la valoración se realiza vía WhatsApp)
    agent_response = re.sub(r"(vis[ií]t[aá]mos? en nuestras clínicas.*?)(?=\.|$)", "", agent_response, flags=re.IGNORECASE).strip()

    # 6. Si se detectó la intención de valoración, añadir un mensaje complementario para enviar la imagen de ejemplo
    if send_image:
        agent_response += "\n\nEnvianos una serie de fotografias como las del siguiente ejemplo para valorar tu caso personal."

    return {
        "success": True,
        "actions_taken": [],
        "final_response": agent_response,
        "message_content": agent_response,
        "send_image": send_image,
        "info_context": ""
    }
