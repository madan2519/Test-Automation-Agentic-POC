from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import os

# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    GROQ_API_KEY: str
    JIRA_BASE_URL: str
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    SCRIPT_STORAGE_PATH: str = "./scripts"
    LOG_LEVEL: str = "INFO"
    OPENAI_API_KEY: str = None  # Optional, only needed if using OpenAI

    @field_validator("GROQ_API_KEY", "JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "OPENAI_API_KEY", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip().strip('"').strip("'")
        return v

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        extra="ignore"
    )

settings = Settings()

# Log masked settings for verification
def log_settings():
    print(f"--- Settings Loaded from {os.path.join(BASE_DIR, '.env')} ---")
    print(f"JIRA_BASE_URL: {settings.JIRA_BASE_URL}")
    print(f"JIRA_EMAIL: {settings.JIRA_EMAIL}")
    print(f"JIRA_API_TOKEN: {settings.JIRA_API_TOKEN[:5]}...{settings.JIRA_API_TOKEN[-5:]} (len: {len(settings.JIRA_API_TOKEN)})")
    print(f"GROQ_API_KEY: {settings.GROQ_API_KEY[:5]}... (len: {len(settings.GROQ_API_KEY)})")
    print(f"OPENAI_API_KEY: {settings.OPENAI_API_KEY[:5]}... (len: {len(settings.OPENAI_API_KEY)})")
    print("-------------------------------------------------")

log_settings()
