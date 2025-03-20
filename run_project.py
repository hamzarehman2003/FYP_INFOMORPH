"""
Helper script to run the InfoMorph project
"""
import os
import sys
import subprocess
import webbrowser
from time import sleep

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50 + "\n")

def run_command(command, cwd=None):
    """Run a command and print its output"""
    try:
        print(f"Running: {command}")
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        
        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        return_code = process.poll()
        if return_code != 0:
            print(f"Command failed with return code {return_code}")
            error = process.stderr.read()
            print(f"Error: {error}")
            return False
        return True
    except Exception as e:
        print(f"Failed to run command: {e}")
        return False

def main():
    print_header("InfoMorph Project Runner")
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("Error: This script should be run from the project root directory")
        print(f"Current directory: {os.getcwd()}")
        return False

    # Check if the virtual environment exists
    if not os.path.exists("venv"):
        print("Creating Python virtual environment...")
        if not run_command("python -m venv venv"):
            print("Failed to create virtual environment. Please check your Python installation.")
            return False
    
    # Install Python dependencies
    print_header("Installing Python dependencies")
    activate_cmd = "venv\\Scripts\\activate" if sys.platform == "win32" else "source venv/bin/activate"
    if not run_command(f"{activate_cmd} && pip install -r requirements.txt"):
        print("Failed to install Python dependencies.")
        return False
    
    # Check if the frontend directory exists
    if os.path.exists("info-morph"):
        print_header("Setting up Next.js frontend")
        if not run_command("npm install", cwd="info-morph"):
            print("Warning: Failed to install Node.js dependencies.")
            print("If you want to run the frontend, navigate to the info-morph directory and run 'npm install'")
    else:
        print("Frontend directory not found. Skipping frontend setup.")
    
    # Run the FastAPI server
    print_header("Starting FastAPI server")
    print("(Press Ctrl+C to stop the server)")
    
    # Open API docs in browser
    sleep(2)  # Give the server a moment to start
    webbrowser.open("http://localhost:8000/docs")
    
    # Run the server (this will block until stopped)
    run_command(f"{activate_cmd} && uvicorn main:app --reload")
    
    return True

if __name__ == "__main__":
    main()
