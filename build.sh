#!/bin/bash

var=0.2-light

docker push dsblab/single_cell_analysis:$var
docker push dsblab/single_cell_analysis:$var

# docker manifest create amouat/single_cell_analysis:$var dsblab/single_cell_analysis:$var-amd64 dsblab/single_cell_analysis:$var-arm64
# docker push dsblab/single_cell_analysis:$var