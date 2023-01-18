import json
import logging
import furl
import os
import requests

from flask import Flask, request
from dotenv import load_dotenv
from waitress import serve
from paste.translogger import TransLogger

load_dotenv('../.env')

env = {}
for key in ('LIBAPPS_BASE', 'SITE_ID', 'GUIDES_API_KEY', 'SITE_ID',
            'NO_RESULTS_URL', 'MODULE_URL'):
    env[key] = os.environ.get(key)
    if env[key] is None:
        raise RuntimeError(f'Missing environment variable: {key}')

no_results_url = env['NO_RESULTS_URL']
module_url = env['MODULE_URL']
site_id = env['SITE_ID']
api_key = env['GUIDES_API_KEY']

debug = os.environ.get('FLASK_DEBUG')

logger = logging.getLogger('guides-searcher')
loggerWaitress = logging.getLogger('waitress')

if debug:
    logger.setLevel(logging.DEBUG)
    loggerWaitress.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    loggerWaitress.setLevel(logging.INFO)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def root():
    return {'status': 'ok'}


@app.route('/ping')
def ping():
    return {'status': 'ok'}


@app.route('/search')
def search():
    args = request.args

    # Check query param
    if 'q' not in args or args['q'] == '':
        return {
            'error': {
                'msg': 'q parameter is required',
            },
        }, 400

    query = args['q']

    # Full pagination not supported, but limit is supported
    # using the standard per_page parameter.
    limit = 3
    if 'per_page' in args and args['per_page'] != "":
        limit = int(args['per_page'])

    params = {
        'site_id': site_id,
        'search_terms': query,
        'key': api_key,
        'sort_by': 'relevance'
    }

    full_query_url = env['LIBAPPS_BASE']

    search_url = furl.furl(full_query_url)

    # Execute Guides search
    try:
        response = requests.get(search_url.url, params=params)
    except Exception as err:
        logger.error(f'Search error at url'
                     '{search_url.url}, params={params}\n{err}')

        return {
            'endpoint': 'guides',
            'results': [],
            'error': {
                'msg': f'Search error',
            },
        }, 500

    if response.status_code not in [200, 206]:
        logger.error(f'Received {response.status_code} with q={query}')

        return {
            'endpoint': 'guides',
            'results': [],
            'error': {
                'msg': f'Received {response.status_code} for q={query}',
            },
        }, 500

    logger.debug(f'Submitted url={search_url.url}, params={params}')
    logger.debug(f'Received response {response.status_code}')

    json_content = json.loads(response.text)
    rendered_content = None
    total_records = len(json_content)
    module_link = module_url + query

    api_response = {
        'endpoint': 'guides',
        'query': query,
        'per_page': limit,
        'page': 1,
        'total': total_records,
        'module_link': module_link,
    }

    if total_records > 0:
        rendered_content = parse_results(json_content, limit)
        api_response['results'] = rendered_content
    else:
        api_response['error'] = build_no_results()
        api_response['results'] = []

    return api_response


def build_no_results():
    return {
        'msg': 'No Results',
        'no_results_url': no_results_url,
    }


def parse_results(raw_results, limit):
    results = []

    i = 0
    for item in raw_results:
        if 'friendly_url' in item and item['friendly_url'] != '':
            link = item['friendly_url']
        else:
            link = item['url']

        results.append({
            'title': item['name'],
            'link': link,
            'description': item['description'],
            'item_format': 'web_page'
        })
        i = i + 1
        if i >= limit:
            break

    return results


def get_total_records(parsed_content):
    return len(parsed_content)


if __name__ == '__main__':
    # This code is not reached when running "flask run". However the Docker
    # container runs "python app.py" and host='0.0.0.0' is set to ensure
    # that flask listens on port 5000 on all interfaces.

    # Run waitress WSGI server
    serve(TransLogger(app, setup_console_handler=True),
          host='0.0.0.0', port=5000, threads=10)
