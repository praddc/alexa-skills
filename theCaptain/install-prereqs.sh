#!/usr/bin/env bash

#This assumse you are on an Amazon Linux AMI
sudo yum update
sudo yum install gcc
sudo yum install libxml2-devel libxslt-devel python-devel
sudo yum install libxml2-devel libxslt-devel python-devel
pip install requests -t ./
pip install pytz -t  ./
pip install beautifulsoup -t ./
# Crap, this doesn't always work, need to remember how i fixed it
pip install lxml -t  ./
