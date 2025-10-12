#!/bin/sh
docker build -t owasp1 .                          
docker run --rm -p 8000:8000 owasp1
