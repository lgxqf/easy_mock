# -*- coding: utf-8 -*-
import os
import time

from flask import Flask, request, make_response
from werkzeug.routing import BaseConverter
from easy_mock import config
from easy_mock.common import check_schema
from easy_mock.loader import locate_processor_py, load_processor_func, get_api_yaml, get_request_body, get_all_yaml, \
    get_yaml
from easy_mock.process import resolve_all_refs


class WildcardConverter(BaseConverter):
    regex = r'.*?'
    weight = 200


def mock_server(path):
    conf = get_api_yaml(path, request.method)
    if not conf:
        return make_response({"error": path + " is not defined in ymal file."}, 405)

    req = get_request_body(conf, request)
    sleep_time = conf.get("sleep", 0)

    if sleep_time > 0:
        time.sleep(sleep_time)

    setup, teardown = conf.get("setup"), conf.get("teardown")

    # setup processor
    req = load_processor_func().get(setup)(req) if setup and locate_processor_py(os.getcwd()) else req

    # match easy_mock data
    for md in conf.get("defined_data_list", ()):
        if req == md.get("body"):
            resp = md.get("response")
            break
    else:
        # random data for schema
        response_schema = conf.get("response_schema")

        if not response_schema:
            return make_response({"error": "Must define response_schema or have matching defined_data_list"}, 404)

        resp = resolve_all_refs(response_schema)

    # teardown processor
    resp = load_processor_func().get(teardown)(req, resp) if teardown and locate_processor_py(os.getcwd()) else resp

    if conf.get("request_schema", None):
        error = check_schema(conf.get("request_schema"), req)
        if error:
            msg = make_response({"msg": error['msg']}, 400)
            return msg

    return resp


def main():
    app = Flask(__name__)

    app.url_map.converters['wildcard'] = WildcardConverter

    app.add_url_rule(rule='/<wildcard:path>', view_func=mock_server,
                     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])

    kwargs = {
        "host": '0.0.0.0',
        "port": config.port
    }

    if config.is_https:
        kwargs['ssl_context'] = 'adhoc'
        print("Run in https mode")
    else:
        print("Run in http mode")

    if len(config.file_path) < 2:
        print("Invalid yaml file : " + config.file_path)
        return 1
    else:
        print("Yaml file : " + config.file_path)

    api_list = get_all_yaml(config.file_path) if os.path.isdir(config.file_path) else get_yaml(config.file_path)

    if not api_list or len(api_list) == 0:
        print("Invalid yaml file or directory " + config.file_path)
        return 1

    print("API:")
    for api in api_list:
        print("    - " + api['url'] + "  " + api['method'])
    print("\n")

    app.run(**kwargs)
