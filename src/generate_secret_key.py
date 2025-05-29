import secrets

def generate_django_secret_key():
    return secrets.token_urlsafe(50)

if __name__ == "__main__":
    print("Your new Django SECRET_KEY:")
    print(generate_django_secret_key())
