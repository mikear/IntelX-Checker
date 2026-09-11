"""Keyring Storage Module
Provides OS Keyring password management for API key with automatic .env fallback.
"""
import os
import logging
from typing import Optional
from dotenv import find_dotenv, set_key, load_dotenv

logger = logging.getLogger(__name__)

SERVICE_NAME = "IntelX_Checker"
API_KEY_NAME = "INTELX_API_KEY"


def get_api_key() -> str:
    """Retrieve API key first from system keyring, falling back to .env / os.environ."""
    try:
        dotenv_path = find_dotenv(filename='.env', raise_error_if_not_found=False)
        if dotenv_path:
            load_dotenv(dotenv_path)
    except Exception as e:
        logger.warning(f"Error loading .env file: {e}")

    try:
        import keyring
        key = keyring.get_password(SERVICE_NAME, API_KEY_NAME)
        if key:
            logger.info("API Key loaded from system keyring.")
            return key
    except Exception as e:
        logger.warning(f"Failed to access system keyring: {e}")

    env_key = os.getenv(API_KEY_NAME, "")
    if env_key:
        logger.info("API Key loaded from .env / environment.")
    return env_key


def set_api_key(api_key: str, dotenv_path: Optional[str] = None) -> bool:
    """Save API key to system keyring if available, and update .env file as fallback."""
    keyring_saved = False
    try:
        import keyring
        if api_key:
            keyring.set_password(SERVICE_NAME, API_KEY_NAME, api_key)
        else:
            try:
                keyring.delete_password(SERVICE_NAME, API_KEY_NAME)
            except Exception:
                pass
        keyring_saved = True
        logger.info("API Key updated in system keyring.")
    except Exception as e:
        logger.warning(f"Could not save API Key in keyring: {e}")

    try:
        if not dotenv_path:
            dotenv_path = find_dotenv(filename='.env', raise_error_if_not_found=False) or '.env'
        set_key(dotenv_path, API_KEY_NAME, api_key)
        os.environ[API_KEY_NAME] = api_key
        logger.info(f"API Key updated in .env ({dotenv_path}).")
        return True
    except Exception as e:
        logger.error(f"Error writing API Key to .env: {e}")
        return keyring_saved
