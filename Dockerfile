FROM jupyter/base-notebook:hub-4.0.2

USER root
# RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
# RUN add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
RUN sudo apt update
RUN apt-get -y install gcc git
# RUN sudo apt upgrade -y
RUN apt-get -y install r-base
RUN apt-get -y install curl
RUN apt-get -y install libcurl4-openssl-dev
RUN apt-get -y install libssl-dev
# RUN apt-get -y install libcurl
# RUN R -e "install.packages('littler', dependencies=TRUE)"
RUN R -e "install.packages('BiocManager', quiet=TRUE)"
RUN R -e "BiocManager::install('DESeq2', quiet=TRUE)"
RUN R -e "install.packages('dplyr', quiet=TRUE)"
RUN R -e "install.packages('ggplot2', quiet=TRUE)"
RUN R -e "install.packages('remotes', quiet=TRUE)"
RUN R -e "remotes::install_github('satijalab/seurat', 'seurat5', quiet = TRUE)"
USER jovyan

RUN pip install rpy2 anndata2ri
COPY requirements.txt .
RUN pip install --file requirements.txt
# RUN pip install --no-binary :mnnpy: mnnpy==0.1.9.5
# RUN pip install pydpc==0.1.3
# RUN pip install sam-algorithm==0.8.7
# RUN pip install DCA==0.3.4
# RUN pip install magic-impute==3.0.0
# RUN pip install palantir==1.0.0
# RUN pip install trimap==1.0.15
# RUN pip install phenograph==1.5.3
# RUN pip install git+https://github.com/mossjacob/pcurvepy
# RUN pip install pyslingshot
# RUN pip install openpyxl==3.0.9
# RUN pip install gprofiler-official==1.0.0
# RUN pip install scikit-misc==0.1.4
# RUN pip install scvi-tools==0.14.6

# RUN R -e ""
# RUN Rscript -e "install.packages('methods',dependencies=TRUE, repos='http://cran.rstudio.com/')"
#   --library=/home/username/Rpackages