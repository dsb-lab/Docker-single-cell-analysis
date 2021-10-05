#!/bin/bash

mkdir home

PATHIN="$(pwd)/home"

#Files to remove other ongoing sessions of the analuysis, comment if you want to have more open sessions at the same time
docker stop single_cell_analysis
docker rm single_cell_analysis

#Channel of the localhost browser where to show the jupyterlab session
CHANNEL=8888

docker run --rm \
           -p $CHANNEL:8888 \
           --name single_cell_analysis \
           --mount type=bind,source=$PATHIN,destination=/home/jovyan \
           -e JUPYTER_ENABLE_LAB=yes \
           single_cell_analysis 
           
docker stop single_cell_analysis
docker rm single_cell_analysis
