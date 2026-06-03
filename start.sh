#!/bin/sh
run --port=5000 & 
nginx -g "daemon off;"
