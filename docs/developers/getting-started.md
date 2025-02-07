# Getting started

The supported environment for Timesketch development is Docker.

Note: Exclamation mark `!` denotes commands that should run in the docker container shell, dollar sign `$` denotes commands to run in your local shell.

## Locations and concepts

- Timesketch provides a webinterface and a REST API
- The configurations is located at `/data` sourcecode folder
- The front end uses `Vue.js` framework and is stored at `/timesketch/frontend`
- Code that is used in potentially multiple locations is stored in `/timesketch/lib`
- Analyzers are located at `/timesketch/lib/analyzers`
- The API methods are defined in `/timesketch/api`
- API client code is in `/api_client/python/timesketch_api_client`
- Data models are defined in `/timesketch/models`

## Setting up your development environment

Start a shell, change to the `timesketch/docker/dev` directory

```bash
$ git clone timesketch
$ cd timesketch/docker/dev
$ docker-compose up
```

Check that everything is running smoothly:

```bash
$ docker ps
CONTAINER ID   IMAGE                                                          COMMAND                  CREATED       STATUS       PORTS                                NAMES
d58d55bd53b3   us-docker.pkg.dev/osdfir-registry/timesketch/dev:latest        "/docker-entrypoint.…"   3 hours ago   Up 3 hours   127.0.0.1:5000->5000/tcp             timesketch-dev
0b99c30fbd25   us-docker.pkg.dev/osdfir-registry/timesketch/notebook:latest   "jupyter notebook"       3 hours ago   Up 3 hours   127.0.0.1:8844->8844/tcp, 8899/tcp   notebook
8696f39a2ba3   justwatch/elasticsearch_exporter:1.1.0                         "/bin/elasticsearch_…"   3 hours ago   Up 3 hours   9114/tcp                             es-metrics-exporter
f91d133600ae   grafana/grafana:latest                                         "/run.sh"                3 hours ago   Up 3 hours   127.0.0.1:3000->3000/tcp             grafana
c4b0f954eba6   prom/prometheus:v2.24.1                                        "/bin/prometheus --c…"   3 hours ago   Up 3 hours   127.0.0.1:9090->9090/tcp             prometheus
75dd0ed520fc   redis:6.0.10-alpine                                            "docker-entrypoint.s…"   3 hours ago   Up 3 hours   6379/tcp                             redis
bd10ed3677ca   docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2       "/tini -- /usr/local…"   3 hours ago   Up 3 hours   9200/tcp, 9300/tcp                   elasticsearch
128ece4be3b5   postgres:13.1-alpine                                           "docker-entrypoint.s…"   3 hours ago   Up 3 hours   5432/tcp                             postgres
```

Wait a few mintues for the installation script to complete.

```bash
$ docker-compose logs timesketch
Attaching to timesketch-dev
timesketch-dev         | Obtaining file:///usr/local/src/timesketch
timesketch-dev         | Installing collected packages: timesketch
timesketch-dev         |   Running setup.py develop for timesketch
timesketch-dev         | Successfully installed timesketch
timesketch-dev         | User dev created/updated
timesketch-dev         | Timesketch development server is ready!
```

Add a user to your Timesketch server (this will add a user `dev` with password `dev`)

```bash
$ docker-compose exec timesketch tsctl add_user --username dev --password dev
User dev created/updated
```

Now, start the `gunicon` server that will serve the Timsesketch WSGI app

In one shell:

```bash
$ docker-compose exec timesketch gunicorn --reload -b 0.0.0.0:5000 --log-file - --timeout 120 timesketch.wsgi:application
[2021-05-25 16:36:32 +0000] [94] [INFO] Starting gunicorn 19.10.0
[2021-05-25 16:36:32 +0000] [94] [INFO] Listening at: http://0.0.0.0:5000 (94)
[2021-05-25 16:36:32 +0000] [94] [INFO] Using worker: sync
/usr/lib/python3.8/os.py:1023: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  return io.open(fd, *args, **kwargs)
[2021-05-25 16:36:32 +0000] [102] [INFO] Booting worker with pid: 102
[2021-05-25 16:36:33,343] timesketch.wsgi_server/INFO Metrics server enabled
```

By now, you should be able to point your browser to `http://localhost:5000/` and log in with
the username and password combination you specified earlier. Any changes to Python files
(e.g. in the `timesketch/api/v1` directory tree) will be picked up automatically.

### Celery workers

Although they are written in Python, changes on importers, analyzers and other asynchronous elements of the codebase
are not picked up by the Gunicorn servers but by **Celery workers**.

If you're planning to work on those (or even just import timelines into your Timesketch instance), you'll need to launch
a Celery worker, and re-launch it every time you bring changes to its code.

In a new shell, run the following:

```bash
$ docker-compose exec timesketch celery -A timesketch.lib.tasks worker --loglevel info
```

### Restarting

To restart the webserver and celery workers, stop the execution. Depending on your system `ctrl+c` will do it.
Then start them both as outlined before with:

```bash
$ docker-compose exec timesketch gunicorn --reload -b 0.0.0.0:5000 --log-file - --timeout 120 timesketch.wsgi:application
$ docker-compose exec timesketch celery -A timesketch.lib.tasks worker --loglevel info
```

## API development

Exposing new functionality via the API starts at `/timesketch/api/v1/routes.py`. In that file the different routes / endpoints are defined that can be used.
Typically every route has a dedicated Resource file in `/timesketch/api/v1/resources`.

A resource can have `GET` as well as `POST`or other HTTP methods each defined in the same resource file. A good example of a resource that has a mixture is `/timesketch/api/v1/resources/archive.py`.

To write tests for the resource, add a section in `/timesketch/api/v1/resources_test.py`

### Error handling

It is recommended to expose the error with as much detail as possible to the user / tool that is trying to access the resource.

For example the following will give a human readable information as well as a HTTP status code that client code can react on

```python
if not sketch:
            abort(HTTP_STATUS_CODE_NOT_FOUND, 'No sketch found with this ID.')
```

On the opposite side the following is not recommended:

```python
if not sketch:
            abort(HTTP_STATUS_CODE_BAD_REQUEST, 'Error')
```

## Writing documentation

Writing documentation is critical for others to use your features, so we encourage to write documentation along side with shipping new features.

The documentation is auto generated by a Github workflow `https://github.com/google/timesketch/blob/master/.github/workflows/mkdocs.yml` which will execute `mkdocs gh-deploy --force`and deploy changes to timesketch.org.

To test mkdocs locally, run the following in your container:

```shell
! cd /usr/local/src/timesketch
! pip3 install mkdocs mkdocs-material mkdocs-redirects
! mkdocs serve
```

And visit the results / review remarks, warnings or errors from mkdocs.
