#!/bin/bash
./ressources/updateRessources.sh
pyinstaller -F main.py
mv ./dist/main ./dist/SaisieMesAbs
cp -r ./configurations ./dist/configurations