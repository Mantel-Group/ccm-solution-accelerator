FROM python:latest

# Create a non-root user and group
RUN groupadd -r collector && useradd -r -g collector collector

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y jq

# Set up Workdir
WORKDIR /extract

# == Install Metric Generation requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --no-cache-dir \
    && rm requirements.txt

COPY . .

# Adjust file permissions
RUN chmod +x *.sh \
    && chown -R collector:collector /extract

# Switch to non-root user
USER collector

CMD [ "./main.sh" ]
