# Bold Bot - Agente ReACT para WhatsApp

Este proyecto implementa un agente conversacional basado en el paradigma ReACT (Reason and Act) para interactuar con clientes a través de WhatsApp. El agente está diseñado para BOLD, una clínica especializada en restauración capilar.

## Funcionalidades Principales

- **Interacción ReACT:** El agente sigue un ciclo de Pensamiento-Acción-Observación para determinar la mejor respuesta.
- **Consulta de Información:** Utiliza una herramienta interna (`info_agent`) para obtener información específica sobre BOLD y sus servicios.
- **Envío de Mensajes:** Puede enviar mensajes de texto y, en casos específicos (cuando el cliente decide iniciar el tratamiento), mensajes con imágenes.
- **Integración con WhatsApp:** Se conecta a la API de WhatsApp Business a través de un webhook.

## Tecnologías Utilizadas

- **Python:** Lenguaje principal de programación.
- **FastAPI:** Framework web para construir la API y el webhook.
- **OpenAI API:** Para la generación de respuestas del agente.
- **Saptiva API:** (Posiblemente otra API de IA, basada en `get_responses.py`).
- **python-dotenv:** Para gestionar variables de entorno.

## Estructura del Proyecto

```
bold-bot/
├── agents/                # Lógica de los agentes (ReACT, Informativo)
│   ├── __init__.py
│   ├── main.py            # Agente ReACT principal
│   └── informativo.py     # Agente para consultas de información
├── AI/                    # Interacción con modelos de IA
│   ├── __init__.py
│   └── get_responses.py   # Funciones para llamar a OpenAI/Saptiva
├── utils/                 # Utilidades generales
│   ├── __init__.py
│   ├── parse_messages.py  # Parseo de webhooks de WhatsApp
│   └── send_message.py    # Envío de mensajes de WhatsApp
├── .env                   # Archivo para variables de entorno (¡No subir a Git!)
├── app.py                 # Aplicación FastAPI principal (Webhook)
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Este archivo
```

## Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd bold-bot
    ```

2.  **Crear un entorno virtual e instalar dependencias:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Crear el archivo `.env`:**
    Crea un archivo llamado `.env` en la raíz del proyecto y añade las siguientes variables:
    ```env
    WEBHOOK_TOKEN=<TU_WEBHOOK_TOKEN_DE_WHATSAPP>
    WHATSAPP_TOKEN=<TU_TOKEN_DE_ACCESO_PERMANENTE_DE_WHATSAPP>
    WHATSAPP_PHONE_NUMBER_ID=<ID_DEL_NÚMERO_DE_TELÉFONO_DE_WHATSAPP>
    OPENAI_API_KEY=<TU_API_KEY_DE_OPENAI>
    SAPTIVA_API_KEY=<TU_API_KEY_DE_SAPTIVA> # Si aplica
    SAPTIVA_API_URL=<URL_DE_LA_API_DE_SAPTIVA> # Si aplica
    ```
    - Reemplaza los valores `<...>` con tus credenciales reales.
    - Asegúrate de que este archivo esté en tu `.gitignore`.

## Ejecución

Para iniciar la aplicación FastAPI:

```bash
uvicorn app:app --reload --port 8000
```

La API estará disponible en `http://localhost:8000`.

Necesitarás configurar un webhook en la plataforma de desarrolladores de Meta (WhatsApp Business API) que apunte a la URL pública de tu servidor donde se ejecuta esta aplicación (por ejemplo, usando ngrok durante el desarrollo) en la ruta `/webhook`. Asegúrate de usar el mismo `WEBHOOK_TOKEN` que definiste en tu archivo `.env`.