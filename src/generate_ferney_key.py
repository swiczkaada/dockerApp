from cryptography.fernet import Fernet

def generate_fernet_key():
    key = Fernet.generate_key()
    print(f"Clé Fernet générée : {key.decode()}")

if __name__ == "__main__":
    generate_fernet_key()
