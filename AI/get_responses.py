import os
import logging
import requests
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def openAI_response(sys_prompt, message):
    """
    Llama a la API de OpenAI para obtener una respuesta a partir de un mensaje de sistema y un mensaje de usuario.
    
    Parameters
    ----------
    sys_prompt : str
        Mensaje de sistema que se utiliza como contexto para la respuesta.
    message : str
        Mensaje del usuario que se debe responder.
    
    Returns
    -------
    str
        La respuesta a la consulta.
    """
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=512,
            temperature=0.7
        )
    
    openAI_response = response.choices[0].message.content
    return openAI_response


def saptiva_respose(sys_prompt, message):
    """
    Llama a la API de Saptiva para obtener una respuesta a partir de un mensaje de usuario y un mensaje de sistema.
    
    Parameters
    ----------
    sys_prompt : str
        Mensaje de sistema que se utiliza como contexto para la respuesta.
    message : str
        Mensaje del usuario que se debe responder.
    
    Returns
    -------
    str
        Respuesta a la pregunta del usuario.
    """
    SAPTIVA_API_KEY = os.environ['SAPTIVA_API_KEY']
    SAPTIVA_API_URL = os.environ['SAPTIVA_API_URL']
    
    headers = {
    "Authorization": f"Bearer {SAPTIVA_API_KEY}",
    "Content-Type": "application/json"
    }

    payload = {
        "modelName": "LLaMa3.3 70B",
        "newTokens": 1024,
        "sysPrompt": sys_prompt,
        "text": "",
        "userMessage": message,
        "temperature": 0.7
    }

    saptiva_response = requests.post(SAPTIVA_API_URL, json=payload, headers=headers)
    return saptiva_response.text

    
