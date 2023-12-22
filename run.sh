#!/bin/bash

mkdir home

PATHIN="$(pwd)/home"

#Channel of the localhost browser where to show the jupyterlab session
CHANNEL=8888

docker run --rm \
           -p $CHANNEL:8888 \
           --name single_cell_analysis \
           --mount type=bind,source=$PATHIN,destination=/home/jovyan \
           -e JUPYTER_ENABLE_LAB=yes \
           dsblab/single_cell_analysis:0.6