FROM python:latest

RUN groupadd -r dbt && useradd -r -g dbt dbt

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --no-cache-dir

COPY . .

RUN python generate_int_metrics_combined.py
RUN chmod +x main.sh

RUN chown -R dbt:dbt /usr/src/app

USER dbt
RUN dbt deps

CMD [ "./main.sh" ]
