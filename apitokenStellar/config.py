from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    IS_DEVELOPMENT_ENVIROMENT: bool = True
    DEV_EMAILS: List[str] = [""]

    SQLALCHEMY_DATABASE_URL: str

    HVAC_URL: str = "http://localhost:8200"
    HVAC_USER: str = "api"
    HVAC_PASSWORD: str = ""

    SLUG_PORJECT_RESIGN: str = ""

    STELLAR_HORIZON_URL: str = "https://horizon.stellar.org"
    STELLAR_RPC_URL: str = "https://soroban-testnet.stellar.org"
    STELLAR_NETWORK_PASSPHRASE: str = "Public Global Stellar Network ; September 2015"
    COMPLIANT_ID_CONTRACT_ID: str = (
        "CC44C6TFT3YCF2EUG54ZHIBGFOGZLH3OO4XEENTOSGIJEP76KQ6BYTAC"
    )
    STELLAR_ADMIN_SECRET_KEY: str = ""

    LOCK_FILE: str = ""
    LOCK_FILE_KYC: str = ""

    AWS_ENDPOINT_URL: str = (
        "http://localhost:4566" if IS_DEVELOPMENT_ENVIROMENT else None
    )
    AWS_REGION_NAME: str = "us-east-1"

    @field_validator("DEV_EMAILS", mode="before")
    @classmethod
    def assemble_emails(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [i.strip() for i in v.split(",")]
        return v


# Se instancia settings. Pydantic-settings intentará leer de variables de entorno y del fichero .env
# Si faltan campos obligatorios (los que no tienen default), lanzará un error al arrancar.
settings = Settings()

# Mantener compatibilidad con el resto del código que importa variables directas de config
IS_DEVELOPMENT_ENVIROMENT = settings.IS_DEVELOPMENT_ENVIROMENT
DEV_EMAILS = settings.DEV_EMAILS
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL
HVAC_URL = settings.HVAC_URL
HVAC_USER = settings.HVAC_USER
HVAC_PASSWORD = settings.HVAC_PASSWORD
SLUG_PORJECT_RESIGN = settings.SLUG_PORJECT_RESIGN

STELLAR_HORIZON_URL = settings.STELLAR_HORIZON_URL
STELLAR_RPC_URL = settings.STELLAR_RPC_URL
STELLAR_NETWORK_PASSPHRASE = settings.STELLAR_NETWORK_PASSPHRASE
COMPLIANT_ID_CONTRACT_ID = settings.COMPLIANT_ID_CONTRACT_ID
STELLAR_ADMIN_SECRET_KEY = settings.STELLAR_ADMIN_SECRET_KEY

LOCK_FILE = settings.LOCK_FILE
LOCK_FILE_KYC = settings.LOCK_FILE_KYC

EARASTELLAR_PROMOTER = 17

AWS_ENDPOINT_URL = settings.AWS_ENDPOINT_URL
AWS_REGION_NAME = settings.AWS_REGION_NAME
