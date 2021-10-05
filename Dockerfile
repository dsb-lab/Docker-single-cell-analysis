FROM jupyter/base-notebook:python-3.8.8

COPY requirements.txt .

#Add some packages
USER root
RUN sudo apt-get update
RUN apt-get -y install gcc git
USER jovyan

#Install requirement packages
RUN conda config --add channels bioconda &&\
    conda config --add channels defaults &&\
    conda config --add channels conda-forge &&\
    conda config --add channels powerai &&\
    conda config --add channels auto

RUN conda install --file requirements.txt

# Install apart because it is giving problems or do not exist in conda
RUN pip install --no-binary :mnnpy: mnnpy==0.1.9.5
RUN pip install pydpc==0.1.3
RUN pip install sam-algorithm==0.8.7
