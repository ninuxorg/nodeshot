FROM python:2.7

WORKDIR /app

RUN apt-get update && apt-get install -yy libgeos-dev
ADD requirements.txt /app/
RUN pip install -r requirements.txt

#copy all files
ADD . /app
COPY docker/ /app/

EXPOSE 5000

#remove sync in 1.8
RUN mkdir /log && \
    python manage.py syncdb --noinput --no-initial-data && \
    python manage.py migrate --noinput --no-initial-data && \
    python manage.py loaddata initial_data

CMD python manage.py runserver
