FROM python:3.9

WORKDIR /usr/src/app/

COPY . /usr/src/app/
RUN apt-get update

RUN apt-get -y install libatlas-base-dev
RUN pip install --no-cache-dir --extra-index-url https://piwheels.org/simple -r requirements.txt

CMD ["python", "main.py"]
