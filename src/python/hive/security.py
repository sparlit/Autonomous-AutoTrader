import os
import json
import base64
import logging
import sys
from typing import Optional, Dict

# 11050: Windows Data Protection API (DPAPI) wrapper
# This allows encrypting data specifically for the current Windows User.

logger = logging.getLogger("AAT_Security")

try:
    import win32crypt
    HAS_DPAPI = True
except ImportError:
    HAS_DPAPI = False
    if sys.platform == "win32":
        logger.warning("⚠️ Windows detected but 'pywin32' (win32crypt) is missing. Credentials stored in config/vault.bin are NOT encrypted with DPAPI. Install pywin32 for institutional security.")
    else:
        logger.debug("Non-Windows platform. DPAPI unavailable.")

class CredentialManager:
    """11051: Secure storage for MT5 and API credentials."""
    def __init__(self, storage_path: str = "config/vault.bin"):
        self.storage_path = storage_path

    def save_credentials(self, account_id: str, password: str, server: str):
        """Encrypt and save credentials."""
        data = {
            "account": account_id,
            "password": password,
            "server": server
        }
        raw_json = json.dumps(data).encode('utf-8')

        if HAS_DPAPI:
            try:
                # DPAPI encryption: CryptProtectData
                encrypted_data = win32crypt.CryptProtectData(raw_json, "AAT_Vault", None, None, None, 0)
            except Exception as e:
                logger.error(f"DPAPI Encryption failed: {e}. Falling back to base64.")
                encrypted_data = base64.b64encode(raw_json)
        else:
            # Fallback for testing/dev environments
            encrypted_data = base64.b64encode(raw_json)

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        with open(self.storage_path, "wb") as f:
            f.write(encrypted_data)
        logger.info("Credentials secured in vault.")

    def load_credentials(self) -> Optional[Dict[str, str]]:
        """Load and decrypt credentials."""
        if not os.path.exists(self.storage_path):
            return None

        with open(self.storage_path, "rb") as f:
            encrypted_data = f.read()

        try:
            if HAS_DPAPI:
                try:
                    _, decrypted_data = win32crypt.CryptUnprotectData(encrypted_data, None, None, None, 0)
                    raw_json = decrypted_data.decode('utf-8')
                except:
                    # Try base64 fallback if DPAPI fails (might happen if saved on another machine/user or before DPAPI was working)
                    raw_json = base64.b64decode(encrypted_data).decode('utf-8')
            else:
                raw_json = base64.b64decode(encrypted_data).decode('utf-8')

            return json.loads(raw_json)
        except Exception as e:
            logger.error(f"Failed to decrypt vault: {e}")
            return None

    def clear(self):
        """Wipe the vault."""
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)
            logger.info("Vault purged.")
