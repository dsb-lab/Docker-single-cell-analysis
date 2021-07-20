Docker file for the analysis of Pijuan and Sala.

**Warning**: The analysis has not been completed yet. Some parts of the code ar nonsense so be careful to run it for now.

# Use without docker

In the file `requirements.txt` there is the defined basic packages used and its versions for the analysis. The analsys is performed using Python3.8.8.

Inside home, you will find all the analysis scripts.

# Construct Docker

A docker image with the required python version and packages can be created running

```
./build_git
```

# Download data

The necessary data for the analysis can be obtained running

```
./download_data
```

# Run analysis

For running the analysis just start a jupyter lab session with

```
./run
```

