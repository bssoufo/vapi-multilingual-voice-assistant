import logging
from typing import Dict, Any, Optional, List

from core.vapi_client import VapiClient, VapiClientError
from  core import config as app_config # To access agent names

logger = logging.getLogger(__name__)

class SquadService:
    ENDPOINT_PLURAL = "squad" # VAPI uses /squad for list and create, /squad/{id} for patch/delete


    def __init__(self, client: VapiClient):
        self.client = client

    def get_squad_id_by_name(self, name: str) -> Optional[str]:
        squad = self.client.get_entity_by_name(self.ENDPOINT_PLURAL, name)
        return squad["id"] if squad else None

    def _build_squad_config_payload(self, name: str, assistant_ids: Dict[str, str]) -> Dict[str, Any]:
        """Builds the payload for squad creation/update."""
        initial_agent_id = assistant_ids.get(app_config.AGENT_INITIAL_NAME)
        en_agent_id = assistant_ids.get(app_config.AGENT_EN_NAME)
        fr_agent_id = assistant_ids.get(app_config.AGENT_FR_NAME)

        if not all([initial_agent_id, en_agent_id, fr_agent_id]):
            missing = [
                n for n, i in [
                    (app_config.AGENT_INITIAL_NAME, initial_agent_id),
                    (app_config.AGENT_EN_NAME, en_agent_id),
                    (app_config.AGENT_FR_NAME, fr_agent_id)
                ] if not i
            ]
            msg = f"Cannot build squad, missing assistant IDs for: {', '.join(missing)}"
            logger.error(msg)
            raise ValueError(msg)


        initial_agent_destinations = [
            {
                "type": "assistant",
                "assistantName": app_config.AGENT_EN_NAME, # VAPI uses name here for destination, not ID
                "description": "Squad-level declaration for transfer to English agent.",
                "message": "Okay, I will transfer you to our English team now."
            },
            {
                "type": "assistant",
                "assistantName": app_config.AGENT_FR_NAME, # VAPI uses name here
                "description": "Squad-level declaration for transfer to French agent.",
                "message": "Ok je vous transfert vers un agent qui parle francais"
            }
        ]
        return {
            "name": name,
            "members": [
                {
                    "assistantId": initial_agent_id,
                    "assistantDestinations": initial_agent_destinations
                },
                {"assistantId": en_agent_id},
                {"assistantId": fr_agent_id},
            ]
        }

    def create_or_update_squad(self, name: str, assistant_ids: Dict[str, str]) -> Optional[Dict[str, Any]]:
        log_prefix = f"Squad '{name}'"
        try:
            squad_config_payload = self._build_squad_config_payload(name, assistant_ids)
            existing_id = self.get_squad_id_by_name(name)

            if existing_id:
                logger.info(f"{log_prefix} already exists with ID {existing_id}. Updating.")
                return self.client.update_entity(self.ENDPOINT_PLURAL, existing_id, squad_config_payload)
            else:
                logger.info(f"{log_prefix} does not exist. Creating.")
                return self.client.create_entity(self.ENDPOINT_PLURAL, squad_config_payload)
        except VapiClientError as e:
            logger.error(f"Failed to process {log_prefix}: {e}")
            return None
        except ValueError as ve: # From _build_squad_config_payload
            logger.error(f"Configuration error for {log_prefix}: {ve}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing {log_prefix}: {e}", exc_info=True)
            return None