import os
import sys
import subprocess
import time

def main():
    print("==================================================")
    print("🕵️‍♂️ DetectAI - Combined AI Crime Investigation Launcher")
    print("==================================================")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_app = os.path.join(root_dir, "frontend", "app.py")
    
    print(f"[DetectAI] Launching combined application...")
    print(f"[DetectAI] Target: {frontend_app}")
    
    # Run Streamlit app
    cmd = [sys.executable, "-m", "streamlit", "run", frontend_app]
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[DetectAI] Shutting down DetectAI app. Goodbye!")

if __name__ == "__main__":
    main()
