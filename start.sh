#!/bin/sh
flask run --port=5000 & 
nginx -g "daemon off;"
