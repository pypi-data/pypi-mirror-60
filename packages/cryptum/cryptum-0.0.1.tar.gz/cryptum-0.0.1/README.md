# cryptum
[![Build Status](https://travis-ci.org/AUCR/cryptum.svg?branch=master)](https://travis-ci.org/AUCR/cryptum)
[![codecov](https://codecov.io/gh/AUCR/cryptum/branch/master/graph/badge.svg)](https://codecov.io/gh/AUCR/AUCR)

## Overview

cryptum is a simple python encryption library that can generate rsa public/private keys and encrypt data for easy 
transport between applications and languages.

## Install with Pip

Example Install with Pip

    pip install PyYAML
    pip install -r requiremnets.txt
    export FLASK_APP=aucr.py
    export FLASK_DEBUG=1
    flask run

## Easy Docker use

    sudo docker pull quay.io/wroersma/aucr
    sudo docker run aucr -p 5000:5000