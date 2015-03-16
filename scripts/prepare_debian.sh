#!/bin/bash

apt-get update
apt-get install -y build-essential ruby1.9.1-dev git python-dev python-virtualenv libxml2-dev libxslt-dev libffi-dev libmysqlclient-dev libpq-dev libsqlite3-dev wget

# remove pip if present and get the latest
apt-get remove -y python-pip
GET_PIP_MD5=add41078298d8111714c6b87636714f5
wget https://bootstrap.pypa.io/get-pip.py 
if md5sum get-pip.py | grep -q $GET_PIP_MD5; then 
    python get-pip.py
fi
pip install -U setuptools swiftly
