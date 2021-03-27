# -*- coding: utf-8 -*-

import argparse
import os
from easy_mock import common, loader, config
from easy_mock.__about__ import __description__, __version__
from easy_mock.core import main
from easy_mock.loader import load_default_conf
from easy_mock.util import Pb2Yaml


def cli():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        '-v', '--version', dest='version', action="store_true",
        help="show version")
    parser.add_argument(
        dest='file_path',
        help="yaml configuration file, directory, or .proto file")
    parser.add_argument(
        '-p', dest='port',
        help="port that needs mock service.")
    parser.add_argument(
        '-https', dest='enable_https', action='store_true', default=False,
        help="enable mock server https protocol")
    parser.add_argument(
        '-req', dest='yaml_req', action='store_true', default=False,
        help="generate request_schema in yaml")
    parser.add_argument(
        '-res', dest='yaml_res', action='store_true', default=True,
        help="generate response_schema in yaml")

    args = parser.parse_args()

    # print(args)
    print("\n")

    if args.version:
        print(__version__)
        exit(0)

    if args.file_path:
        file_path = args.file_path

        if file_path.endswith(".proto"):
            Pb2Yaml.pb2ymal(file_path, args.yaml_req, args.yaml_res)
            exit(0)
        elif file_path.endswith(".yml") or file_path.endswith(".yaml"):
            config.file_path = file_path
        else:
            common.log().error("yml or pb file is not specified.")
            exit(1)

    if args.port:
        config.port = args.port
    else:
        config.port = load_default_conf("port") or "9000"

    if args.enable_https:
        config.is_https = True
    else:
        config.is_https = bool(load_default_conf("is_https"))

    if args.file_path:
        config.file_path = args.file_path
    else:
        config.file_path = os.getcwd()

    main()
