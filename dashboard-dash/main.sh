#!/bin/sh

nginx -g "daemon off;" &

gunicorn -w 1 -b 127.0.0.1:8050 app:server
