import sys
import json
import subprocess
import signal

with open("./cam_config.json") as file:
    cam_config = json.load(file)
    # print(cam_config)


# List to hold the subprocesses
subprocesses = []

# Function to create a subprocess
def create_subprocess(cameraIP):
    # Command to execute the subprocess script
    command = ["python3", "cam_supervisor.py", cameraIP]

    # Create the subprocess and store the process object
    process = subprocess.Popen(command)
    subprocesses.append(process)

    print("Running: ", cameraIP)

# Function to terminate all subprocesses
def terminate_subprocesses():
    for process in subprocesses:
        # Terminate the subprocess
        process.terminate()

# Register a signal handler to catch the script termination
def signal_handler(signal, frame):
    terminate_subprocesses()
    sys.exit(0)

# Register the signal handler for the termination signal (e.g., Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

#run all subprocesses for each camera
for cameraIP in cam_config["cameras"]:
    create_subprocess(cameraIP)

# Wait for the main script to finish (e.g., by blocking on an input)
input("Press Enter to terminate all processes...\n\n")

# Terminate all subprocesses when the script exits
terminate_subprocesses()


