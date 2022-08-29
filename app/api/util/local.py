from dotenv import load_dotenv, dotenv_values
import os

def load_local_env_vars():
    environment = os.getenv("ENVIRONMENT", None)

    if environment is None or environment == "local":
        load_dotenv("local.env")