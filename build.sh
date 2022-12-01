#!/bin/bash

var=0.6

docker build . --no-cache -t dsblab/single_cell_analysis:$var
#docker push dsblab/single_cell_analysis:$var