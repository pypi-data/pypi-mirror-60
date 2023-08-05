FROM continuumio/miniconda3

# Install orca dependencies...
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    libgtk2.0-0 \
    libxtst6 \
    libxss1 \
    libgconf-2-4 \
    libnss3 \
    libasound2
RUN conda install -c plotly plotly-orca psutil
RUN pip install pipenv
COPY ./treebeard_lib ./treebeard_lib
COPY ./Pipfile ./Pipfile
RUN pipenv install --skip-lock --system
COPY . .
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app