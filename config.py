import os
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration"""
    DEBUG: bool = True
    DATABASE_TYPE: str = "memory"  # memory, sqlite, postgresql
    DATABASE_URL: str = "sqlite:///supermarket.db"
    LOG_LEVEL: str = "INFO"

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            DEBUG=os.getenv('DEBUG', 'True') == 'True',
            DATABASE_TYPE=os.getenv('DATABASE_TYPE', 'memory'),
            DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///supermarket.db'),
            LOG_LEVEL=os.getenv('LOG_LEVEL', 'INFO')
        )
```

### 8. **Requirements**

**requirements.txt**
```
# No external dependencies for basic version
# Add these for enhanced features:
# flask==3.0.0          # For web interface
# sqlalchemy==2.0.0     # For real database
# pytest==7.4.0         # For testing