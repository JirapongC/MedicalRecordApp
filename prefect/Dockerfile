FROM prefecthq/prefect:2-python3.10
RUN apt-get update
RUN apt-get install -y libpq-dev
RUN apt-get install -y postgresql-client
RUN pip install psycopg2 prefect-shell sling
EXPOSE 4200