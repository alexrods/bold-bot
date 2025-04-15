from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class WhatsAppMessage(BaseModel):
    messaging_product: str = "whatsapp"
    recipient_type: str = "individual"
    
    # Campos de identificación
    from_: Optional[str] = Field(None, alias='from')
    to: Optional[str] = None
    
    # Identificadores
    id: Optional[str] = None
    timestamp: Optional[str] = None
    
    # Contenido del mensaje
    type: str = None
    text: Optional[Dict[str, str]] = None
    
    # Campos adicionales para diferentes tipos de contenido
    image: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None
    audio: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None
    
    # Metadatos adicionales
    context: Optional[Dict[str, Any]] = None

    def get_recipient_number(self) -> str:
        """
        Obtiene el número de teléfono del destinatario.
        Prioriza 'to' sobre 'from_'
        """
        return self.to or self.from_
    
    def is_image(self) -> bool:
        """Verifica si el mensaje es una imagen."""
        return self.type == "image" and self.image is not None

    def get_image_url(self) -> Optional[str]:
        """Obtiene el URL de la imagen si está disponible."""
        return self.image.get("url") if self.is_image() else None
    
class SendMessagePayload(BaseModel):
    type: str
    message: str
    to: str

class SendMessagePayloadMedia(BaseModel):
    type: str
    url: str
    to: str
    filename: str

class GetMessagePayloadMedia(BaseModel):
    from_: str = Field(..., alias='from')
    id: str
    timestamp: str
    type: str
    payload: dict

class LoginPayload(BaseModel):
    username: str
    password: str

class JsonPayload(BaseModel):
    WorkItemId: str
    CLASIFICACION: str
    APROBADO: str