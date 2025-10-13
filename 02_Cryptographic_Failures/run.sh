#!/bin/sh
docker build -t owasp2 .                          
docker run --rm -p 8000:8000 owasp2
