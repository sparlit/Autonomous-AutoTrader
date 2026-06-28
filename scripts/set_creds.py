import getpass
from src.python.hive.security import CredentialManager

def setup_credentials():
    print("\n" + "="*40)
    print("🌌 PHOENIX GAUNTLET: CREDENTIAL VAULT SETUP")
    print("="*40 + "\n")

    account_id = input("MT5 Account Number: ")
    password = getpass.getpass("MT5 Password: ")
    server = input("MT5 Server (e.g. ICMLive-1): ")

    vault = CredentialManager()
    vault.save_credentials(account_id, password, server)

    print("\n" + "="*40)
    print("✅ Credentials encrypted and saved to vault.")
    print("The system will now auto-login on startup.")
    print("="*40 + "\n")

if __name__ == "__main__":
    setup_credentials()
