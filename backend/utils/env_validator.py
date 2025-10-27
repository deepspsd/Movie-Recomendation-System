"""
Environment Variable Validation
Ensures all required environment variables are set before app starts
"""

import os
import sys
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EnvValidator:
    """Validate environment variables"""
    
    REQUIRED_VARS = [
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "SECRET_KEY",
        "JWT_SECRET_KEY",
    ]
    
    OPTIONAL_VARS = {
        "TMDB_API_KEY": "TMDB integration will be limited (can use OMDB_API_KEY instead)",
        "OMDB_API_KEY": "OMDb integration will be limited (can use TMDB_API_KEY instead)",
        "REDIS_URL": "Caching will use in-memory storage",
        "API_HOST": "Will default to 0.0.0.0",
        "API_PORT": "Will default to 8000",
    }
    
    SECURITY_CHECKS = {
        "SECRET_KEY": lambda v: len(v) >= 32,
        "JWT_SECRET_KEY": lambda v: len(v) >= 32,
    }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate all environment variables"""
        errors = []
        warnings = []
        
        # Check required variables
        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                errors.append(f"[ERROR] Missing required environment variable: {var}")
            elif var in cls.SECURITY_CHECKS:
                if not cls.SECURITY_CHECKS[var](value):
                    errors.append(f"[ERROR] {var} does not meet security requirements (min 32 chars)")
        
        # Check optional variables
        for var, message in cls.OPTIONAL_VARS.items():
            if not os.getenv(var):
                warnings.append(f"[WARNING] Optional variable {var} not set: {message}")
        
        # Check for default/insecure values
        secret_key = os.getenv("SECRET_KEY", "")
        jwt_key = os.getenv("JWT_SECRET_KEY", "")
        
        if "change-this" in secret_key.lower() or "your-secret" in secret_key.lower():
            errors.append("[ERROR] SECRET_KEY appears to be a default value. Please change it!")
        
        if "change-this" in jwt_key.lower() or "your-jwt" in jwt_key.lower():
            errors.append("[ERROR] JWT_SECRET_KEY appears to be a default value. Please change it!")
        
        # Print results
        if errors:
            logger.error("Environment validation failed:")
            for error in errors:
                logger.error(error)
            return False
        
        if warnings:
            logger.warning("Environment validation warnings:")
            for warning in warnings:
                logger.warning(warning)
        
        logger.info("[OK] Environment validation passed")
        return True
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get summary of current configuration"""
        return {
            "database": {
                "host": os.getenv("DB_HOST", "not set"),
                "port": os.getenv("DB_PORT", "not set"),
                "name": os.getenv("DB_NAME", "not set"),
            },
            "api": {
                "host": os.getenv("API_HOST", "0.0.0.0"),
                "port": os.getenv("API_PORT", "8000"),
                "debug": os.getenv("DEBUG", "True"),
            },
            "external_services": {
                "tmdb_configured": bool(os.getenv("TMDB_API_KEY")),
                "omdb_configured": bool(os.getenv("OMDB_API_KEY")),
                "movie_api_available": bool(os.getenv("TMDB_API_KEY") or os.getenv("OMDB_API_KEY")),
                "redis_configured": bool(os.getenv("REDIS_URL")),
            },
            "security": {
                "secret_key_set": bool(os.getenv("SECRET_KEY")),
                "jwt_key_set": bool(os.getenv("JWT_SECRET_KEY")),
            }
        }


def validate_environment() -> bool:
    """Validate environment and exit if critical errors"""
    if not EnvValidator.validate():
        logger.critical("Critical environment configuration errors detected!")
        logger.critical("Please check your .env file and ensure all required variables are set.")
        return False
    return True


if __name__ == "__main__":
    # Run validation
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n" + "="*60)
    print("Environment Validation")
    print("="*60 + "\n")
    
    if validate_environment():
        print("\n✅ All checks passed!\n")
        print("Configuration Summary:")
        import json
        print(json.dumps(EnvValidator.get_config_summary(), indent=2))
    else:
        print("\n❌ Validation failed! Please fix the errors above.\n")
        sys.exit(1)
