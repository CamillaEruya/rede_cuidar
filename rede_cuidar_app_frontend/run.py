import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("FRONTEND_HOST", "127.0.0.1"),
        port=int(os.getenv("FRONTEND_PORT", "8000")),
        reload=True,
    )
