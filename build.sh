#!/bin/bash

var=0.2-light

docker buildx build --no-cache --platform linux/amd64 -t dsblab/single_cell_analysis:$var-amd64 .
docker buildx build --no-cache --platform linux/arm64 -t dsblab/single_cell_analysis:$var-arm64 .

docker push dsblab/single_cell_analysis:$var-amd64
docker push dsblab/single_cell_analysis:$var-arm64

docker manifest create amouat/single_cell_analysis:$var dsblab/single_cell_analysis:$var-amd64 dsblab/single_cell_analysis:$var-arm64
docker push dsblab/single_cell_analysis:$var