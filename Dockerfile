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
    conda config --add channels powerai

RUN conda install --file requirements.txt

# Install mnnpy apart because it is giving problems
RUN pip install --no-binary :mnnpy: mnnpy==0.1.9.5
