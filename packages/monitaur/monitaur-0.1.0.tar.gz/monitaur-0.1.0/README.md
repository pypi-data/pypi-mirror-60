# Monitaur Client Library

Tested with:

1. Python 3.7.6
1. Python 3.6.10

## Development

Create and activate a virtual environment, and then install the requirements:

```sh
(env)$ pip install -r requirements-dev.txt
```

Tests:

```sh
(env)$ python -m pytest -p no:warnings --cov="monitaur"

or

(env)$ python -m pytest -p no:warnings --cov="monitaur" --cov-report html .
```

Run Flake8, Black, and isort:

```sh
(env)$ flake8 monitaur/ tests/
(env)$ black monitaur/ tests/
(env)$ isort monitaur/**/*.py tests/**/*.py
```

## Docker

By using Docker, you can test the integration between the `client-library` and the back-end Django `data-api`.

First, log in to the [GitLab Docker Registry for the data-api project](https://gitlab.com/monitaur.ai/data-api/container_registry):

```sh
$ docker login registry.gitlab.com/monitaur.ai/data-api -u monitaur-docker-registry -p K4-Xiy5QA8959ywXkPjS
```

Build and spin up the containers:

```sh
$ docker-compose up -d --build
```

Sanity check:

```sh
$ curl http://localhost:8008/ping/

{"ping": "pong!"}
```

## Example Use

See _example/sample.py.

```sh
$ python3.7 -m venv env
$ source env/bin/activate
(env)$ pip install -r requirements.txt
(env)$ pip install -r _example/requirements.txt
(env)$ python _example/sample.py
```
