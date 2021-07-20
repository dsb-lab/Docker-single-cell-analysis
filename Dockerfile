FROM jupyter/base-notebook:python-3.8.8

COPY requirements.txt .

RUN conda config --add channels bioconda &&\
    conda config --add channels defaults &&\
    conda config --add channels conda-forge &&\
    conda config --add channels powerai

RUN conda install --file requirements.txt

# RUN conda install scanpy==1.7.0 &&\
#     conda install matplotlib==3.3.4 &&\
#     conda install numpy==1.20.1 &&\
#     conda install pandas==1.2.2 &&\
#     conda install scipy==1.6.0 &&\
#     conda install scikit-learn==0.24.1 &&\
#     conda install scrublet==0.2.3 &&\
#     conda install seaborn==0.11.1 &&\
#     conda install MulticoreTSNE==0.1 &&\
#     conda install scrublet==0.2.3





