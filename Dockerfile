FROM dsblab/single_cell_analysis:0.2

RUN pip install gprofiler-official==1.0.0
RUN pip install scikit-misc==0.1.4
RUN pip install scvi-tools==0.14.6
