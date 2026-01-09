"""
Backend application entry point
Allows running: python -m backend.app
"""

import sys
import uvicorn
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.core.config import settings
from backend.app.core.logging_config import setup_logging

# Setup logging
setup_logging()

if __name__ == "__main__":
    # Disable auto-reload to prevent infinite reload loops from log files
    # Manually restart server when code changes are needed
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # Disabled to prevent log file watching issues
        log_level=settings.LOG_LEVEL.lower()
    )




