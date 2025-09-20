# HIVE Realtime Rendering Test Data Maker and Rocket API Emulator
## Description
This repository contains tools for recording a rocket launch from the videogame Kerbal Space Program (KSP) using KRPC (Kerbal Remote Procedure Call) and emulating the API exposed by Soteria (the Ground control station software used by HIVE). The recorded data can be used for testing and development purposes.

## How to use it

### Setup
1. Clone the repository to your local machine.
   ```bash
   git clone <repository-url>
   ```
2. Make a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```  

### Rocket Emulation
There is some test data included, meaning you can run the emulator without needing to record your own data.

### Recording Data
You will need the game Kerbal Space Program (KSP) and the KRPC mod installed. Follow the instructions on the [KRPC GitHub page](https://github.com/krpc/krpc) to set up the mod.

1. Start Kerbal Space Program (KSP) and place your rocket on the launch pad.
2. Run the `KspTelemetryCollector.py` script to begin recording telemetry data. By default, the data will be saved as `testdata/launch3.json`. To use a different filename, edit the script and change `"testdata/launch3.json"` to your preferred name.
3. The script will automatically handle throttling and staging during the launch.
4. Once the rocket has landed or crashed, stop the script by pressing Ctrl+C in the terminal.

### Running the Emulator
1. Run the `RocketApiEmulator.py` script to start the API emulator.
2. When prompted, input the name of the file to emulate. `testdata/` is prefixed and `.json` is postfixed (e.g., `launch3`).
3. The emulator will start a web server on `http://localhost:8765` by default. You can access the API endpoints using a web browser or tools like Postman or curl.

> **Note**: the included launches include the rocket becoming aerodynamically unstable and tumbling out of control. Also they end up on an angle because of the curvature and rotation of kerbin.

