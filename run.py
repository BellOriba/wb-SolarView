#!/usr/bin/env python3
import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).parent
    
    uvicorn.run(
        "src.solar_api.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
        reload_dirs=[str(project_root / "src")],
        reload_includes=["*.py"],
        reload_excludes=["*.pyc", "*.pyo", "__pycache__"],
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        workers=int(os.getenv("WORKERS", "1")),
    )
