#!/bin/bash

ENV_PATH="../.env_qrogue"

echo "[Qrogue] Creating a new venv..."

FULL_PATH=$(realpath $0)
cd $(dirname $FULL_PATH) || exit 202
mkdir $ENV_PATH
python3 -m venv $ENV_PATH

if [ $? ]; then
	echo "[Qrogue] venv successfully created"
	echo "[Qrogue] Activating venv..."
	source ${ENV_PATH}/bin/activate
	
	if [ $? ]; then
		echo "[Qrogue] Downloading and installing required packages..."
		pip3 install -r requirements_linux.txt
		
		if [ $? ]; then
			echo
			echo "[Qrogue] Done!"
			echo "[Qrogue] You can play now my executing play_qrogue.sh!"
			exit 0
		else
			echo "[Qrogue] ERROR: Requirements could not be installed!"
			exit 1
		fi
	else
		echo "[Qrogue] ERROR: Could not activate venv"
		exit 2
	fi
else
	echo "[Qrogue] Creating venv failed. Please check if you fulfill all prerequisites (in prerequisites.txt)!"
	exit 3
fi

