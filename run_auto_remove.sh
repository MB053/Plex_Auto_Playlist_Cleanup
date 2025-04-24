#!/bin/bash

# == INFORMATION ==
# Make this executable by running chmod +x /home/USER_LOCATION/run_auto_remove.sh (Change USER_LOCATION to actual script location)
# Please make sure to build the plex_env on the location 
# === Absolute paths ===
VENV_PATH="/home/USER_LOCATION/plex_env"   #Change USER_LOCATION to actual script location
SCRIPT_PATH="/home/USER_LOCATION/Auto_Remove_Script.py"  #Change USER_LOCATION to actual script location

# === Optional hardcoded token (if needed) ===
# export PLEX_TOKEN="your_actual_token_here"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Run the script
"$VENV_PATH/bin/python3" "$SCRIPT_PATH"

