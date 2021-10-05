#!/bin/bash

docker stop dsblab/single_cell_analysis
docker rmi -f dsblab/single_cell_analysis
docker build . -t dsblab/single_cell_analysis:latest