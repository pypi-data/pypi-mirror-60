import requests
import argparse
import os
import sys

README_API_KEY = os.environ.get('README_API_KEY', None)


def update_spec(path, id, ignore_erros=None):
    url = "https://dash.readme.io/api/v1/api-specification/%s" % id
    files = {'spec': open(path, 'rb')}

    response = requests.request('PUT', url, auth=(README_API_KEY, 'pass'), files=files)

    if(response.status_code == 200):
        print('Updated successfully')
    else:
        print('Failure')

        if not ignore_erros:
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='rdme-cli')
    parser.add_argument('job_option', help='options:spec, doc')
    parser.add_argument('--path')
    parser.add_argument('--id')
    parser.add_argument('--ignore-erros')
    args = parser.parse_args()

    if args.job_option == 'spec':
        update_spec(args.path, args.id, args.ignore_erros)
        sys.exit(0)
    else:
        raise Exception('Invalid job_option, should be: spec or doc')
