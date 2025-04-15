import os
from typing import Optional
from utils.models import WhatsAppMessage



def parse_whatsapp_webhook(webhook_data: dict) -> Optional[WhatsAppMessage]:
    """
    Parsea los datos del webhook de WhatsApp y extrae el primer mensaje.
    
    Args:
        webhook_data (dict): Datos completos recibidos del webhook de WhatsApp
    
    Returns:
        Optional[WhatsAppMessage]: Objeto de mensaje parseado o None si no se encuentra
    """
    print("WEBHOOK DATA:", webhook_data)
    try:
        # Verificar que sea un evento de WhatsApp Business
        if webhook_data.get('object') != 'whatsapp_business_account':
            print("No es un evento de WhatsApp Business")
            return None

        # Navegar por la estructura anidada del webhook
        for entry in webhook_data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # Buscar mensajes en el payload
                if 'messages' in value and value['messages']:
                    # Tomar el primer mensaje y parsearlo
                    mensaje_data = value['messages'][0]
                    
                    # Validar y crear objeto WhatsAppMessage
                    mensaje = WhatsAppMessage(**mensaje_data)
                    print("MESSAGE: ", mensaje)
                    return mensaje

    except Exception as e:
        print(f"Error parseando webhook: {e}")
        return None

