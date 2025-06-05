import logging
from typing import Dict, Any, Optional, List

from core.vapi_client import VapiClient, VapiClientError

logger = logging.getLogger(__name__)

class AssistantService:
    ENDPOINT_PLURAL = "assistant" # VAPI uses /assistant for list and create, /assistant/{id} for patch/delete

    def __init__(self, client: VapiClient):
        self.client = client

    def get_assistant_id_by_name(self, name: str) -> Optional[str]:
        assistant = self.client.get_entity_by_name(self.ENDPOINT_PLURAL, name)
        return assistant["id"] if assistant else None

    def create_or_update_assistant(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        assistant_name = config.get("name")
        if not assistant_name:
            logger.error("Assistant configuration must have a 'name' field.")
            return None

        log_prefix = f"Assistant '{assistant_name}'"
        try:
            existing_id = self.get_assistant_id_by_name(assistant_name)

            if existing_id:
                logger.info(f"{log_prefix} already exists with ID {existing_id}. Updating.")
                return self.client.update_entity(self.ENDPOINT_PLURAL, existing_id, config)
            else:
                logger.info(f"{log_prefix} does not exist. Creating.")
                return self.client.create_entity(self.ENDPOINT_PLURAL, config)
        except VapiClientError as e:
            logger.error(f"Failed to process {log_prefix}: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing {log_prefix}: {e}", exc_info=True)
            return None

    def process_assistants(self, assistant_configs: List[Dict[str, Any]]) -> Dict[str, str]:
        """Processes a list of assistant configurations, returning a map of name to ID."""
        assistant_ids: Dict[str, str] = {}
        all_successful = True

        for config in assistant_configs:
            name = config["name"]
            logger.info(f"Processing assistant: {name}")
            processed_assistant = self.create_or_update_assistant(config)
            
            if processed_assistant and processed_assistant.get("id"):
                assistant_ids[name] = processed_assistant["id"]
                logger.info(f"Successfully processed assistant '{name}', ID: {assistant_ids[name]}")
            else:
                logger.error(f"Failed to process assistant '{name}'.")
                all_successful = False # Mark as not all successful, but continue processing others
        
        if not all_successful:
            # Decide on behavior: raise error, return partial, etc.
            # For now, returning what was successful. Main can check length.
            logger.warning("Not all assistants were processed successfully.")
            
        return assistant_ids