FROM jupyter/base-notebook:python-3.9.7

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
    conda config --add channels auto &&\
    conda config --add channels letaylor

RUN conda install --file requirements.txt

# Install apart because it is giving problems or do not exist in conda
RUN pip install pydpc==0.1.3
# RUN pip install DCA==0.3.3
RUN pip install magic-impute==3.0.0
RUN pip install palantir==1.0.0
RUN pip install trimap==1.0.15
RUN pip install phenograph==1.5.3
RUN pip install git+https://github.com/mossjacob/pcurvepy
RUN pip install pyslingshot
RUN pip install git+https://github.com/metgem/forceatlas2
RUN pip install --no-binary :mnnpy: mnnpy==0.1.9.5
# RUN pip install git+https://github.com/atarashansky/self-assembling-manifold
