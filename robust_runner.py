import subprocess
import time
import sys
import os
from pathlib import Path

# Force stdout to use UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).parent.resolve()
PYTHON_EXE = ROOT_DIR / "venv" / "Scripts" / "python.exe"

if not PYTHON_EXE.exists():
    PYTHON_EXE = "python"  # Fallback to system python if venv not found

def run_pipeline(source: str):
    """Run ingest.py for a given source and restart on failure or temporary blocks."""
    print(f"\n==============================================")
    print(f"STARTING ROBUST RUN FOR SOURCE: {source.upper()}")
    print(f"==============================================\n")
    
    attempts = 0
    while True:
        attempts += 1
        print(f"\n[Runner] Running ingest.py --source {source} (Attempt #{attempts})...")
        
        # Start ingest.py as a subprocess and stream its output
        cmd = [str(PYTHON_EXE), "ingest.py", "--source", source]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1
        )
        
        quota_exceeded = False
        
        # Stream output line-by-line
        for line in iter(process.stdout.readline, ''):
            print(line, end='', flush=True)
            if "API Quota Exceeded" in line or "quota" in line.lower() or "429" in line:
                quota_exceeded = True
        
        process.stdout.close()
        return_code = process.wait()
        
        if return_code == 0:
            if quota_exceeded:
                print(f"\n[Runner] Hit Daily/RPM API Quota. Sleeping for 2 minutes before retrying...")
                time.sleep(120)  # Cooldown period before trying again
            else:
                print(f"\n[Runner] Completed ingest.py --source {source} successfully!")
                break
        else:
            print(f"\n[Runner] ingest.py exited with error code {return_code}.")
            print("[Runner] Sleeping for 30 seconds before restarting...")
            time.sleep(30)

def main():
    # Step 1: Run Vagad Ingestion to completion
    run_pipeline("vagad")
    
    # Step 2: Run KVO Ingestion to completion
    run_pipeline("kvo")
    
    print("\n==============================================")
    print("ALL INGESTION RUNS COMPLETED SUCCESSFULLY!")
    print("==============================================\n")

if __name__ == "__main__":
    main()
