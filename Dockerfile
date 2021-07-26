FROM jupyter/base-notebook:python-3.8.8

COPY requirements.txt .

RUN conda config --add channels bioconda &&\
    conda config --add channels defaults &&\
    conda config --add channels conda-forge &&\
    conda config --add channels powerai

RUN conda install --file requirements.txt
