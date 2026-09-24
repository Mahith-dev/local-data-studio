import threading
import uvicorn
import webview
import time
import os

def start_server():
    # Runs the FastAPI server on localhost:8000
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    # 1. Start backend server in a separate daemon thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)  # Allow the server half a second to initialize

    # 2. Get absolute path to the frontend HTML file
    frontend_path = os.path.abspath("frontend/index.html")

    # 3. Create and launch the native desktop application window
    window = webview.create_window(
        title="Local Data Studio",
        url=f"file://{frontend_path}",
        width=1000,
        height=750,
        resizable=True
    )
    webview.start()