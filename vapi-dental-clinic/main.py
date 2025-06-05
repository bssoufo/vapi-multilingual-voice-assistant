import logging
import json

from core import config
from core.vapi_client import VapiClient
from services.assistant_service import AssistantService
from services.squad_service import SquadService
from utils.logging_config import setup_logging # If you created this

# Setup basic logging
setup_logging() # Or: logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_setup():
    logger.info(f"Starting Vapi Dental Clinic Setup (Version: {config.AGENT_INITIAL_NAME.split('_')[-1]})...")

    # Initialize Vapi Client
    try:
        vapi_client = VapiClient(base_url=config.BASE_URL, api_key=config.VAPI_API_KEY)
    except ValueError as e:
        logger.error(f"Failed to initialize VapiClient: {e}")
        return

    # Initialize Services
    assistant_service = AssistantService(vapi_client)
    squad_service = SquadService(vapi_client)

    # --- Process Assistants ---
    logger.info("--- Processing Assistants ---")
    
    # Get all assistant configurations from config.py
    # Ensure configs are used directly from the config module
    assistant_configurations = [
        config.AGENT_INITIAL_CONFIG,
        config.AGENT_EN_CONFIG,
        config.AGENT_FR_CONFIG
    ]
    
    assistant_ids = assistant_service.process_assistants(assistant_configurations)

    if len(assistant_ids) != len(assistant_configurations):
        logger.error("Not all assistants could be processed. Halting squad creation.")
        return

    logger.info("\nAll assistants processed successfully. Proceeding to squad processing...")

    # --- Process Squad ---
    logger.info("--- Processing Squad ---")
    processed_squad = squad_service.create_or_update_squad(
        name=config.SQUAD_NAME,
        assistant_ids=assistant_ids
    )

    if processed_squad and processed_squad.get("id"):
        logger.info("\n--- Squad Processed Successfully ---")
        logger.info(f"Squad Configuration: {json.dumps(processed_squad, indent=2, ensure_ascii=False)}")
        logger.info(f"Squad ID: {processed_squad.get('id')}")
        logger.info("\nSetup complete.")
    else:
        logger.error("\nSquad processing failed.")

if __name__ == "__main__":
    run_setup()