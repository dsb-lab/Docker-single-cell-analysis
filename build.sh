#!/bin/bash

var=0.7

# docker build . --no-cache -t dsblab/single_cell_analysis:$var
docker build . -t dsblab/single_cell_analysis:$var
#docker push dsblab/single_cell_analysis:$var