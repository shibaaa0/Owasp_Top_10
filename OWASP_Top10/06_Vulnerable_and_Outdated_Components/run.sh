#!/bin/sh
docker build -t owasp6 .                          
docker run --rm -p 5000:5000 --name ctf-lab owasp6
