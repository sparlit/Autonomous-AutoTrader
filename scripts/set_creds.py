import os
import sys
import getpass
import logging
sys.path.append(os.path.join(os.getcwd(), 'src'))
from python.hive.security import CredentialManager
logging.basicConfig(level=logging.INFO)
def set_creds():
    print("🔐 AAT Secure Credential Setup")
    acc = input("MT5 Account ID: ")
    pwd = getpass.getpass("MT5 Password: ")
    srv = input("MT5 Server: ")
    CredentialManager().save_credentials(acc, pwd, srv)
    print("✅ Credentials encrypted and saved to vault.")
if __name__ == "__main__": set_creds()
