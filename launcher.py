import subprocess
import os
import time
from pathlib import Path

def run_in_new_window(command, title=None):
    """Run a command in a completely new Terminal window"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        venv_path = os.path.join(script_dir, "venv", "bin", "activate")
        
        # Build the full command sequence
        full_command = f"""
        clear
        cd '{script_dir}'
        source '{venv_path}'
        {command}
        """
        
        # Clean and format the command
        cleaned_command = ""
        for line in full_command.split("\n"):
            stripped = line.strip()
            if stripped:
                cleaned_command += stripped + "; "
        
        # Proper AppleScript formatting
        apple_script = f"""
        tell application "Terminal"
            activate
            tell application "System Events" to tell process "Terminal" to keystroke "n" using command down
            delay 0.5
            do script "{cleaned_command}" in front window
            delay 0.3
            set custom title of front window to "{title}"
        end tell
        """
        
        # Remove empty lines and extra spaces
        apple_script = "\n".join(line.strip() for line in apple_script.split("\n") if line.strip())
        
        # Execute the AppleScript
        process = subprocess.run(
            ["osascript", "-e", apple_script],
            capture_output=True,
            text=True
        )
        
        if process.returncode != 0:
            print(f"Error output: {process.stderr}")
            return False
        return True
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    NUM_BINS = 4
    
    print("🚀 Launching system")
    
    # First launch central station
    if run_in_new_window("python3 central_station.py", "Central Station"):
        print("✅ Successfully launched Central Station")
    else:
        print("❌ Failed to launch Central Station")
        exit(1)
    
    # Then launch smart bins
    print(f"\n Launching {NUM_BINS} Smart Bins...")
    for nr in range(1, NUM_BINS + 1):
        bin_name = f"Smart Bin {nr}"
        print(f"  - Launching {bin_name}...", end=" ", flush=True)
        if run_in_new_window(f"python3 smart_bin.py --id {nr}", bin_name):
            print("✅")
        else:
            print("❌")
    