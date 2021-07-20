Docker file for the analysis of Pijuan and Sala.

**Warning**: The analysis has not been completed yet. Some parts of the code ar nonsense so be careful to run it for now.

# Use without docker

In the file `requirements.txt` there is the defined basic packages used and its versions for the analysis. The analsys is performed using Python3.8.8.

Inside home, you will find all the analysis scripts.

The necessary data for the analysis can be obtained running

```
./download_data
```

For running the docker and go over the analysis steps in a jupyter lab session, just run,

```
./run
```

# Use with Docker

A docker image with the required python version and packages can be created running

```
./build_git
```

The necessary data for the analysis can be obtained running

```
./download_data
```

For running the docker and go over the analysis steps in a jupyter lab session, just run,

```
./run
```

