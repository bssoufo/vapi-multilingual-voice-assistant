import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
BASE_URL = "https://api.vapi.ai"

if not VAPI_API_KEY:
    raise ValueError("VAPI_API_KEY not found in .env file or environment variables.")

# --- Unique name for agents en squad ---
AGENT_INITIAL_NAME = "LanquageDetector"
AGENT_EN_NAME = "EnglishAgent"
AGENT_FR_NAME = "FrenchAgent"
SQUAD_NAME = "DentalClinicSquad"

# Shared parts of configurations
_COMMON_VOICE_CONFIG = {
    "model": "eleven_multilingual_v2",
    "voiceId": "o86w79lw8Y208S2HjL2M",
    "provider": "11labs",
    "stability": 0.5,
    "similarityBoost": 0.75
}

_LANGUAGE_DETECTOR_VOICE_CONFIG = {
        "model": "eleven_multilingual_v2",
        "voiceId": "TcAStCk0faGcHdNIFX23",
        "provider": "11labs",
        "stability": 0.5,
        "similarityBoost": 0.75
}

_FRENCH_VOICE_CONFIG = {
        "model": "eleven_multilingual_v2",
        "voiceId": "o86w79lw8Y208S2HjL2M",
        "provider": "11labs",
        "stability": 0.5,
        "similarityBoost": 0.75
    }

_ENGLISH_VOICE_CONFIG = {
        "voiceId": "Elliot",
        "provider": "vapi"
    }

_COMMON_TRANSCRIBER_CONFIG= { # Explicitly named as it's fr-CA
        "model": "nova-3",
        "language": "multi",
        "provider": "deepgram"
}

_FRENCH_TRANSCRIBER_CONFIG =  {
        "language": "fr-CA",
        "provider": "azure"
    }

_ENGLISH_TRANSCRIBER_CONFIG= {
        "model": "nova-3",
        "language": "en",
        "provider": "deepgram"
    }

_COMMON_SERVER_MESSAGES = ["end-of-call-report", "speech-update", "transcript", "tool-calls", "status-update"]
_COMMON_SILENCE_TIMEOUT_SECONDS = 30

# --- Agents configuations ---

# 1. Agent Initial (Lanquage Detector)
AGENT_INITIAL_CONFIG = {
    "name": AGENT_INITIAL_NAME,
    "model": {
        "provider": "openai",
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a language detection assistant for a dental clinic. "
                    "Your role is to determine if the user prefers to speak English or French. "
                    "Based on their response, you will announce the transfer to the appropriate language agent. "
                    "If they say 'English' or similar, choose 'english'. If they say 'French', 'Français' or similar, choose 'french'. "
                    "Then, state you will transfer them to the appropriate team based on their selection."
                )
            }
        ],
    },
    "voice": _LANGUAGE_DETECTOR_VOICE_CONFIG,
    "transcriber": _COMMON_TRANSCRIBER_CONFIG,
    "firstMessage": "Hello! For English, say English. Pour le français, dites Français.",
    "serverMessages": _COMMON_SERVER_MESSAGES,
    "silenceTimeoutSeconds": _COMMON_SILENCE_TIMEOUT_SECONDS,
    "maxDurationSeconds": 600
}

# 2. English Agent
AGENT_EN_CONFIG = {
    "name": AGENT_EN_NAME,
    "model": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful and professional assistant for 'Sunshine Dental Clinic' operating in English. "
                    "Your tasks include: \n"
                    "1. Answering frequently asked questions (opening hours, location, services offered, insurance accepted).\n"
                    "2. Scheduling new appointments: Collect patient name, phone number, reason for visit, preferred date/time.\n"
                    "3. Rescheduling or canceling existing appointments.\n"
                    "4. Providing post-procedure care information.\n"
                    "Always be polite, empathetic, and efficient. Confirm details before finalizing any action. "
                    "If you are unsure about something, say you'll have a human colleague call back. "
                    "To end the call, use the 'end_conversation' function."
                )
            }
        ],
    },
    "voice": _ENGLISH_VOICE_CONFIG,
    "transcriber": _ENGLISH_TRANSCRIBER_CONFIG, # Assuming EN agent still uses fr-CA transcriber based on original
    "firstMessage": "Hello, you've reached Sunshine Dental Clinic, English support. How can I help you today?",
    "serverMessages": _COMMON_SERVER_MESSAGES,
    "silenceTimeoutSeconds": _COMMON_SILENCE_TIMEOUT_SECONDS,
    "maxDurationSeconds": 1800
}

# 3. French Agent
AGENT_FR_CONFIG = {
    "name": AGENT_FR_NAME,
    "model": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Vous êtes un assistant serviable et professionnel pour la 'Clinique Dentaire Soleil' opérant en français. "
                    "Vos tâches incluent : \n"
                    "1. Répondre aux questions fréquentes (horaires d'ouverture, localisation, services offerts, assurances acceptées).\n"
                    "2. Planifier de nouveaux rendez-vous : Recueillir nom du patient, numéro de téléphone, motif de la visite, date/heure préférée.\n"
                    "3. Replanifier ou annuler des rendez-vous existants.\n"
                    "4. Fournir des informations sur les soins post-opératoires.\n"
                    "Soyez toujours poli, empathique et efficace. Confirmez les détails avant de finaliser toute action. "
                    "Si vous n'êtes pas sûr de quelque chose, dites qu'un collègue humain rappellera. "
                    "Pour terminer l'appel, utilisez la fonction 'terminer_la_conversation'."
                )
            }
        ],
    },
    "voice": _FRENCH_VOICE_CONFIG,
    "transcriber": _FRENCH_TRANSCRIBER_CONFIG,
    "firstMessage": "Bonjour, vous êtes bien à la Clinique Dentaire Soleil, support francophone. Comment puis-je vous aider aujourd'hui ?",
    "serverMessages": _COMMON_SERVER_MESSAGES,
    "silenceTimeoutSeconds": _COMMON_SILENCE_TIMEOUT_SECONDS,
    "maxDurationSeconds": 1800
}

ALL_AGENT_CONFIGS = [
    AGENT_INITIAL_CONFIG,
    AGENT_EN_CONFIG,
    AGENT_FR_CONFIG
]
