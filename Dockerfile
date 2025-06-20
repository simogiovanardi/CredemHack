FROM python:3.8-slim

WORKDIR /app

# install gcloud dependencies if needed
RUN pip install --no-cache-dir -r requirements.txt

# copy code and static files
COPY main.py /config/Cluster_Docs.xlsx /config/Docs_Train.xlsx /config/Elenco_Personale.xlsx ./

ENTRYPOINT ["python", "main.py"]