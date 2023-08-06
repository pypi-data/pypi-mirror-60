![Build Status](https://travis-ci.org/canner/cannerflow-python-client.svg?branch=master)

# Introduction

This package provides a client interface to query Cannerflow
a distributed SQL engine. It supports Python 2.7, 3.5, 3.6, and pypy.

# Installation

```
$ pip install cannerflow-python-client
```

# Quick Start

## Client
```python
client = cannerflow.client.bootstrap(
    endpoint='http://localhost:3000',
    workspace_id="c6ce7832-ab83-4d7e-bad3-17397b8f6bdb",
    token="token"
)
queries = client.list_saved_query()
query = client.use_saved_query('region')
raws = query.get_all()
```

## API
Use the DBAPI interface to query cannerflow:

```python
import cannerflow
client = cannerflow.client.bootstrap(
    endpoint="http://localhost:3000",
    workspace_id="18a06718-a976-42a9-a02a-7cf2fe633984",
    token="token"
)

```

# Development
## Setup virtual env

[ref](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

```
python3 -m venv env
source env/bin/activate

```

## Install package for test
```
pip install -e .[tests]
```

## Run test with given workspaceId and token

```
export WORKSPACE_ID="2fae9bf7-a883-4f25-9566-c0d379c44440"
export CANNERFLOW_TOKEN="yJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIwd19hUG43YUpERTRJZXIxanpJUk95akhZZERrWGtfcktjc2RBTVVrUks0In0.eyJqdGkiOiI4Mjc4YjJkOS05NjZmLTRjYjItOGIzZC1kNGVkMGZkYTMzZDQiLCJleHAiOjE1ODA4ODY4MTksIm5iZiI6MCwiaWF0IjoxNTgwODg1NjE5LCJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwODAvYXV0aC9yZWFsbXMvY2FubmVyZmxvd19yZWFsbSIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI1OWVjZGRmYy0wY2ViLTQ0ZjAtOWRhMS0zMmY0N2I4MDg5YTQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJhZG1pbi11aSIsImF1dGhfdGltZSI6MTU4MDg4NDIxNCwic2Vzc2lvbl9zdGF0ZSI6IjYxYjA2MjdiLTFjMmYtNDE4NS05ZTRhLTEyMTM3ZjAwMGRhZSIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsid3M6Yzk4NGIwZjctMWYwYi00NmJhLWJhN2YtNzg1ZDZjOTAwMTFmOioiLCJvZmZsaW5lX2FjY2VzcyIsIndzOmY4ZDIyOWY4LThkZjUtNGRlNC1iNjY5LWQ1NzMyNWZlNjBhNDoqIiwid3M6N2FhMGRjYWMtOTg3ZC00YThlLTk4OGMtNmIyYjgyYTJlMDM5OioiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImdyb3VwcyI6WyIvcm9sZXMvQWRtaW5pc3RyYXRvciIsIi93b3Jrc3BhY2UvZmRzIiwiL3dvcmtzcGFjZS9zZCIsIi93b3Jrc3BhY2UvdGVzdCJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJsZW8ifQ.ES0-hZrd2RR3kSPbErtAN9q72hM-t-FedV86jMiU5agix_5QJg7bEE0CfcVTKuIvR2K8a-TYyqXak7wUqJ-TmU88_h0S73xPStOzPX2AoVpPeBvYN6k_BpUtNAzVOoCJfTcXjlQO29tGyevErkdUtCFWahmhZtatG_WPGQqM9LXGQ4oq_1FGNh1poHh5OADGUTA33Q71j1dJSiLx6gxLtlQjL3q4r9YjcL5Zrh3zbLy6I8UPZFkEFenm1PiN4FGdMRnNtW6_G4PvCUVzcB7ZfUZLySoDIJeoV6akmcp8BQkMEr8mHIXKOkwQf5v22XI96fxO3MZwhCTBtV7FgLJbVw"
python tests/test_utils.py
python tests/test_client.py
```


## Publish

```
python setup.py sdist
twine upload dist/*
```