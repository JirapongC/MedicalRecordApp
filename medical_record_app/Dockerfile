FROM python

RUN pip install psycopg2 flask Flask-SQLAlchemy
RUN mkdir app
WORKDIR /app
COPY . /app
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]