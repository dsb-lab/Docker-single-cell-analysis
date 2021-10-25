#!/bin/bash

var=0.2

docker build . -t dsblab/single_cell_analysis:$var

docker push dsblab/single_cell_analysis:$var