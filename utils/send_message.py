import json
import requests
import os

from dotenv import load_dotenv

load_dotenv()

WHATSAPP_API_URL=os.environ["WHATSAPP_API_URL"]
WHATSAPP_ACCESS_TOKEN=os.environ["WHATSAPP_ACCESS_TOKEN"]

# Check if URL and TOKEN is loaded
if not WHATSAPP_API_URL:
    raise ValueError("URL not found. Please check your .env file.")
if not WHATSAPP_ACCESS_TOKEN:
    raise ValueError("TOKEN not found. Please check your .env file.")

def send_text_message(to, message):
    """
    Sends a text message via WhatsApp using the provided recipient number and message content.

    Args:
        to (str): The recipient's phone number in E.164 format.
        message (str): The text message body to be sent.

    Returns:
        dict: A dictionary with error details if an exception occurs.
    """
    try:
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        })

        headers = {
            'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", WHATSAPP_API_URL, headers=headers, data=payload)
        print(f"Response: {response.status_code} - {response.text}")
    
    except Exception as error:
        return {
            'error': True,
            'code': 305,
            'message': 'An error occurred while processing the request.'
        }

def send_image_message(to):
    """
    Sends an image message via WhatsApp using the provided recipient number and image URL.

    Args:
        to (str): The recipient's phone number in E.164 format.

    Returns:
        dict: A dictionary with error details if an exception occurs.
    """
    image_link = "https://bold-media.s3.us-west-1.amazonaws.com/bold-image.jpeg"
    try:
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {
                "link": image_link
            }
        })

        headers = {
            'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", WHATSAPP_API_URL, headers=headers, data=payload)
        print(f"Response: {response.status_code} - {response.text}")
    
    except Exception as error:
        return {
            'error': True,
            'code': 305,
            'message': 'An error occurred while processing the request.'
        }
        
