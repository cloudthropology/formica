# Formica
[![Build Status](https://travis-ci.org/theserverlessway/formica.svg?branch=master)](https://travis-ci.org/theserverlessway/formica)
[![PyPI version](https://badge.fury.io/py/formica-cli.svg)](https://pypi.python.org/pypi/formica-cli)
[![license](https://img.shields.io/github/license/theserverlessway/formica.svg)](LICENSE)
[![Coverage Status](https://coveralls.io/repos/github/theserverlessway/formica/badge.svg?branch=master)](https://coveralls.io/github/theserverlessway/formica?branch=master)

>Dropped Python 2 compatibility, please upgrade to Python 3. The tool might work or it might not, its not tested against Python 2

Formica makes it easy to create and deploy CloudFormation stacks. It uses CloudFormation syntax with yaml and json support to define your templates. Any existing stack can be used directly, but formica also has built-in modularity so you can reuse and share CloudFormation stack components easily. This allows you to start from an existing stack but split it up into separate files easily.

For dynamic elements in your templates Formica supports [jinja2](http://jinja.pocoo.org/docs/2.9/templates/) as a templating
engine. Jinja2 is widely used, for example in ansible configuration files.

## Installation

Formica can be installed through pip:

```
pip install formica-cli
```

Alternatively you can clone this repository and run

```
python setup.py install
```


## Documentation

Check out the full [Documentation and Quickstart on TheServerlessWay.com](https://theserverlessway.com/tools/formica/)
