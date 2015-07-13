FROM python:2.7

WORKDIR /app

RUN apt-get update && apt-get install -yy libgeos-dev
ADD requirements.txt /app/
RUN pip install -r requirements.txt

#copy all files
ADD . /app
COPY docker/ /app/

EXPOSE 5000

RUN mkdir /log

CMD python manage.py syncdb && python manage.py migrate && python manage.py runserver
