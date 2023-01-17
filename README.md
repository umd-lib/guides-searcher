# guides-searcher

Python 3 Flask application to search the guides searcher.

## Requires

* Python 3.10.8

### Development Setup

See [docs/DevelopmentSetup.md](docs/DevelopmentSetup.md).

## Environment Configuration

The application requires a ".env" file in the root directory to provide
server-specific information (i.e., those parts of the configuration that
may vary based on whether the server is a test/qa/production server).

A sample "env_example" file has been provided to assist with this process.
Simply copy the "env_example" file to ".env" and fill out the parameters as
appropriate.

The configured .env file should not be checked into the Git repository.

### Running in Docker

```bash
$ docker build -t docker.lib.umd.edu/guides-searcher .
$ docker run -it --rm -p 5000:5000 --env-file=.env --read-only docker.lib.umd.edu/guides-searcher
```

### Building for Kubernetes

```bash
$ docker buildx build . --builder=kube -t docker.lib.umd.edu/guides-searcher:VERSION --push
```

### Endpoints

This will start the webapp listening on the default port 5000 on localhost
(127.0.0.1), and running in [Flask's debug mode].

Root endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/>

/ping endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/ping>

/search:

```bash
http://127.0.0.1:5000/search?q=science
```

Note that this searcher does not support pagination or offset at this time.
However, a limit can be used with the per_page parameter.

Example:

```bash
curl 'http://127.0.0.1:5000/search?q=science'
{
  "endpoint": "guides",
  "module_link": "https://lib.guides.umd.edu/srch.php?q=science",
  "page": 1,
  "per_page": 3,
  "query": "science",
  "results": [
    {
      "description": "",
      "item_format": "web_page",
      "link": "https://lib.guides.umd.edu/sciencemicros",
      "title": "Science and Technology Microforms"
    },
    {
      "description": "A guide to Italian Studies Resources at the University of Maryland.",
      "item_format": "web_page",
      "link": "https://lib.guides.umd.edu/italian",
      "title": "Italian Studies"
    },
    {
      "description": "This guide provides links to and information about major electronic and print resources in Latina/o studies available through the University of Maryland Libraries",
      "item_format": "web_page",
      "link": "https://lib.guides.umd.edu/latinx_studies",
      "title": "Latinx Studies"
    }
  ],
  "total": 100
}
```

[Flask's debug mode]: https://flask.palletsprojects.com/en/2.2.x/cli/?highlight=debug%20mode

## License

See the [LICENSE](LICENSE.txt) file for license rights and limitations.
