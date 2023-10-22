import subprocess


TELEGRAM_BOT_API = "6890460672:AAFa73Z84d9RGV4kH-X7RpAAX7dhfjgqnJs"
APP_ID = "23562047"
HASH_ID = "323334f1a13ccd477ae8851277bab744"


def store_secret(secret_name, secret_value):
    """
    Stores a secret in the Google Cloud Secret Manager
    """
    # Create the secret
    subprocess.run(["gcloud", "secrets", "create", secret_name, "--replication-policy", "automatic"], check=True)

    # Add the secret value
    process = subprocess.Popen(["gcloud", "secrets", "versions", "add", secret_name, "--data-file", "-"],
                               stdin=subprocess.PIPE, text=True)
    process.communicate(secret_value)


if __name__ == "__main__":
    store_secret("telegram_bot_api", TELEGRAM_BOT_API)
    store_secret("app_id", APP_ID)
    store_secret("hash_id", HASH_ID)
