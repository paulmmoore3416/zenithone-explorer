"""
ZenithOne Explorer - Configuration Management
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "ZenithOne Explorer"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    
    # Security
    secret_key: str = "change-this-to-a-random-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    password_min_length: int = 8
    
    # Database
    database_url: str = "sqlite:///./backend/data/database.db"
    database_echo: bool = False
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_default: int = 100
    rate_limit_admin: int = 200
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    cors_credentials: bool = True
    
    # Podman
    podman_socket: str = "unix:///run/user/1000/podman/podman.sock"
    container_max_cpu: int = 2
    container_max_memory: int = 1024
    
    # Ollama / Qwen2.5
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:latest"
    ai_enabled: bool = True
    
    # Monitoring
    metrics_interval: int = 5
    metrics_retention_days: int = 90
    log_level: str = "INFO"
    log_file: str = "backend/data/logs/application.log"
    
    # Subsystems
    jes_max_jobs: int = 1000
    jes_spool_size: int = 10737418240
    cics_max_transactions: int = 10000
    cics_timeout: int = 30
    db2_max_connections: int = 100
    db2_cache_size: int = 536870912
    tso_max_sessions: int = 50
    tso_timeout: int = 1800
    
    # Workload Manager
    workload_max_concurrent: int = 100
    workload_default_timeout: int = 3600
    workload_queue_size: int = 1000
    
    # UI
    ui_host: str = "0.0.0.0"
    ui_port: int = 3000
    ui_theme: str = "dark"
    ui_refresh_interval: int = 5
    
    # Email (Optional)
    email_enabled: bool = False
    email_host: Optional[str] = None
    email_port: int = 587
    email_user: Optional[str] = None
    email_password: Optional[str] = None
    email_from: str = "noreply@zenitone.local"
    
    # Backup
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"
    backup_retention_days: int = 30
    backup_path: str = "./backup"
    
    # Development
    dev_mode: bool = True
    reload: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency injection for settings."""
    return settings
