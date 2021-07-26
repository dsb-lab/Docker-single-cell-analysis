Docker file for single cell analysis.

## 1. Building the docker
A docker image with the required python version and packages can be created running

```
./build_git
```

## 2. Running the docker
For running the docker and go over the analysis steps in a jupyter lab session, just run,

```
./run
```

Once run, the docker will be working and executing in the channel 10000. Change the channel in the `run` script if you want to run it in some other channel.. In the terminal you will find a token code that is generated for security reasons:

![](assets/token.png)

Copy that number. For accessing the session, open your favorite folder brwoser and search `localhost:10000`. Directly from the terminal it will be something like,

```
firefox localhost::10000
```

it will open a jupyterlab session that will ask for a password or token.  

![](assets/jupyterlab.png)

Copy the token you obtained before and you will be set up! 

Anything in the `home` folder can be seen by the docker and you and will be saved after the docker is finished.


