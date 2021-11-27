FROM dsblab/single_cell_analysis:0.1

RUN pip install git+https://github.com/mossjacob/pcurvepy
RUN pip install pyslingshot
RUN pip install openpyxl==3.0.9