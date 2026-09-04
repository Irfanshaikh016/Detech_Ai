import os
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="DetectAI - AI Crime Investigation Game Launcher"
    )
    parser.add_argument(
        "--mode",
        choices=["streamlit", "backend", "web"],
        default="streamlit",
        help="Launch mode: 'streamlit' (default UI), or 'backend'/'web' (FastAPI REST server + Noir Web UI)"
    )
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Alias for --mode backend"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Alias for --mode web"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to run the selected service on"
    )

    args = parser.parse_args()

    mode = args.mode
    if args.backend or args.web:
        mode = "backend"

    root_dir = os.path.dirname(os.path.abspath(__file__))

    print("==================================================")
    print("DetectAI - Combined AI Crime Investigation Launcher")
    print("==================================================")

    if mode in ["backend", "web"]:
        backend_dir = os.path.join(root_dir, "backend")
        port = args.port or int(os.getenv("PORT", 8000))
        print(f"[DetectAI] Launching FastAPI Backend & Noir Web UI on http://127.0.0.1:{port}...")
        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port), "--reload"]
        try:
            subprocess.run(cmd, cwd=backend_dir, check=True)
        except KeyboardInterrupt:
            print("\n[DetectAI] Backend server stopped. Goodbye!")
    else:
        frontend_app = os.path.join(root_dir, "frontend", "app.py")
        port = args.port or 8501
        print(f"[DetectAI] Launching Streamlit Detective UI on http://localhost:{port}...")
        print(f"[DetectAI] Target: {frontend_app}")
        cmd = [sys.executable, "-m", "streamlit", "run", frontend_app, "--server.port", str(port)]
        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            print("\n[DetectAI] Shutting down DetectAI app. Goodbye!")

if __name__ == "__main__":
    main()
