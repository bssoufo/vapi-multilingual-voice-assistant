import requests
import json
import logging
from typing import Optional, Dict, Any, List

# If using logging_config.py
# from vapi_dental_clinic.utils.logging_config import setup_logging
# setup_logging() # Call it once, perhaps in __init__.py of the main package or in main.py

logger = logging.getLogger(__name__)

class VapiClientError(Exception):
    """Custom exception for VAPI client errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_content: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_content = response_content

    def __str__(self):
        return f"{super().__str__()} (Status: {self.status_code}, Response: {self.response_content})"


class VapiClient:
    """
    Client for interacting with the Vapi API.
    """
    def __init__(self, base_url: str, api_key: str):
        if not base_url:
            raise ValueError("Base URL cannot be empty.")
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"VapiClient initialized for URL: {self.base_url}")

    def _request(self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        logger.debug(f"Request: {method} {url} Payload: {payload}")
        try:
            response = requests.request(method, url, headers=self.headers, json=payload)
            response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            error_content = None
            try:
                error_content = http_err.response.json()
                logger.error(f"HTTP error: {http_err} - Status: {http_err.response.status_code} - Response: {json.dumps(error_content, indent=2)}")
            except json.JSONDecodeError:
                error_content = http_err.response.text
                logger.error(f"HTTP error: {http_err} - Status: {http_err.response.status_code} - Response: {error_content}")
            raise VapiClientError(
                f"HTTP error occurred while {method}ing {url}",
                status_code=http_err.response.status_code,
                response_content=error_content
            ) from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error: {req_err} while {method}ing {url}")
            raise VapiClientError(f"Request error occurred: {req_err}") from req_err
        except Exception as e:
            logger.error(f"Unexpected error: {e} while {method}ing {url}")
            raise VapiClientError(f"An unexpected error occurred: {e}") from e

    def get_entities(self, endpoint_plural: str) -> List[Dict[str, Any]]:
        """Fetches a list of entities (e.g., assistants, squads)."""
        logger.info(f"Fetching all entities from '{endpoint_plural}'...")
        # VAPI returns a list directly for GET /assistant or GET /squad, not nested under a key.
        entities = self._request("GET", endpoint_plural)
        if not isinstance(entities, list):
            logger.warning(f"Expected a list from GET /{endpoint_plural}, got {type(entities)}. Data: {entities}")
            # Depending on API, might need to return entities.get("data", []) or similar
            # For Vapi, it seems it's a direct list. If it's an error, _request would raise.
            # If it's an empty list, that's fine. If it's not a list but not an error, that's odd.
            # For robustness, ensure it's a list or handle appropriately.
            # Assuming VAPI is consistent and returns a list or error.
            return [] if entities is None else entities # Handle case where API might return null on no entities
        return entities


    def get_entity_by_name(self, endpoint_plural: str, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific entity by its name."""
        logger.info(f"Searching for {endpoint_plural[:-1]} with name '{name}'...")
        try:
            entities = self.get_entities(endpoint_plural)
            for entity in entities:
                if isinstance(entity, dict) and entity.get("name") == name:
                    logger.info(f"Found existing {endpoint_plural[:-1]} '{name}' with ID: {entity['id']}")
                    return entity
            logger.info(f"{endpoint_plural[:-1].capitalize()} '{name}' not found.")
            return None
        except VapiClientError as e:
            # Log and re-raise or handle if not finding is not an error for this specific context
            logger.error(f"Error checking for existing {endpoint_plural[:-1]} '{name}': {e}")
            # Depending on desired behavior, you might want to return None or re-raise
            # For this context, returning None seems appropriate if the entity is not found due to an API issue during listing.
            return None


    def create_entity(self, endpoint_singular: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new entity."""
        entity_name = payload.get("name", "Unknown Entity")
        logger.info(f"Creating {endpoint_singular} '{entity_name}'...")
        response_data = self._request("POST", endpoint_singular, payload=payload)
        logger.info(f"{endpoint_singular.capitalize()} '{entity_name}' created successfully with ID: {response_data.get('id')}")
        return response_data

    def update_entity(self, endpoint_singular: str, entity_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing entity."""
        # VAPI does not allow 'name' field in PATCH payload for assistants/squads
        payload_copy = payload.copy()
        if "name" in payload_copy:
            del payload_copy["name"]

        logger.info(f"Updating {endpoint_singular} with ID '{entity_id}'...")
        url_path = f"{endpoint_singular}/{entity_id}"
        response_data = self._request("PATCH", url_path, payload=payload_copy)
        logger.info(f"{endpoint_singular.capitalize()} ID '{entity_id}' updated successfully.")
        return response_data