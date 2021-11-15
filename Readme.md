# Qrogue #

Qrogue is a Quantum Computing take of the classical game Rogue.

## Installation ##


### Dependencies ###
- py_cui v0.1.4
- qiskit

However, both of these dependencies are installed automatically
in the virtual environment created by the corresponding installer.

### Linux ###

#### Prerequisites ####

- Python 3.8
- python3-venv

For Linux you simply have to run `installer/install.sh` in your
downloaded Qrogue folder to create a new virtual environment for 
the game and install the required packages in there. 

Afterwards just run `play_qrogue.sh` to play the game.

### Windows ###

For Windows there is currently no script available that 
automatically installs everything you need. The best way is to 
create a new virtual environment with Anaconda (Python v3.8). 
Then open your Anaconda Powershell and execute 
`qrogue_folder_path\installer\install.ps1`. You will be asked to 
provide the path to your newly created environment as parameter. 
This will install the required Packages in the virtual 
environment and setup configuration files in your Qrogue folder.

Open the newly created Venv in a terminal and install the 
requirements by typing  
`pip install -r qrogue_folder_path\installer\requirements_windows.txt`

Afterwards you can launch the game in the same terminal by executing 
`python qrogue_folder_path\main.py`.

`qrogue_folder_path` is herby the full path to your downloaded 
Qrogue-folder. 

#### Prerequisites ####

- Python 3.8
- Anaconda
