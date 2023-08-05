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


####
#COPY simple_test_generator/tests.py simple_test_generator/main.py ./
#COPY simple_test_generator/another another
#
#RUN python tests.py
#RUN ls -lhRa test-data/
#RUN python main.py
#COPY simple_test_generator/tests.py simple_test_generator/tests.py
#COPY simple_test_generator/another simple_test_generator/another
#
#RUN mv ../test_pytestgen_cases.py .
#RUN pytest -vv -s --trace-config test_example.py
