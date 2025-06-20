FROM python:3.8-slim

WORKDIR /app

# install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the image
COPY requirements.txt ./

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy code and static files
COPY main.py /config/Cluster_Docs.xlsx /config/Docs_Train.xlsx /config/Elenco_Personale.xlsx ./

ENTRYPOINT ["python", "main.py"]