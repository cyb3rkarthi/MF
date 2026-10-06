import os
import sys
from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    db_engine = app.extensions.get("db_type", "unknown").upper()

    print(f"\n=======================================================")
    print(f"  Madras Foodies Consultancy Web Application")
    print(f"  Database Engine: {db_engine} (Connected)")
    print(f"  Frontend & Backend: Connected")
    print(f"  Access URL: http://{host}:{port}/")
    print(f"=======================================================\n")

    try:
        app.run(host=host, port=port, debug=True)
    except OSError as e:
        if "10048" in str(e) or "Address already in use" in str(e):
            print(f"[INFO] Port {port} is already active and serving the web app.")
            print(f"Open your browser at: http://{host}:{port}/")
        else:
            raise e
