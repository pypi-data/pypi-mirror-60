FROM python:3.7-alpine

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system

COPY pyproject.toml README.md ./
COPY simple_test_generator simple_test_generator


ENV FLIT_ROOT_INSTALL=1
RUN flit install

RUN rm -rf simple_test_generator

ENV AWS_ACCESS_KEY_ID=FAKE AWS_SECRET_ACCESS_KEY=FAKE AWS_REGION=us-east-1
RUN pip install boto3

ADD https://github.com/jeshan/botostubs/archive/master.tar.gz botostubs
RUN tar xvfz botostubs
WORKDIR botostubs-master
#TODO: try without switching dir
RUN AWS_DEFAULT_REGION=us-east-1 python -m simple_test_generator main.py > /dev/null
