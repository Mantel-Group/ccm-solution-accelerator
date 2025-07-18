FROM python:latest

ARG DEFAULT_USER=admin
ARG DEFAULT_PASSWORD=s3cretW0rd

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEFAULT_USER=$DEFAULT_USER \
    DEFAULT_PASSWORD=$DEFAULT_PASSWORD

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nginx \
    apache2-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod +x main.sh

COPY nginx.conf /etc/nginx/sites-enabled/default
RUN htpasswd -cb /etc/nginx/.htpasswd "$DEFAULT_USER" "$DEFAULT_PASSWORD"

RUN mkdir -p /var/log/nginx /var/lib/nginx/body /var/lib/nginx/fastcgi \
    /var/lib/nginx/proxy /var/lib/nginx/scgi /var/lib/nginx/uwsgi \
    && chown -R www-data:www-data /var/log/nginx /var/lib/nginx \
    && chown -R www-data:www-data /app

RUN date -u +"%Y-%m-%dT%H:%M:%SZ" > /app/build-date.txt

RUN touch                       /run/nginx.pid && \
    chown -R www-data:www-data  /run/nginx.pid

USER www-data

EXPOSE 8080

CMD ["./main.sh"]
