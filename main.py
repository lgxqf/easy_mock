# -*- coding: utf-8 -*-
import os

from easy_mock import config
from easy_mock.core import main
from easy_mock.loader import load_default_conf

# config.port = load_default_conf("port") or "9000"
# config.is_https = bool(load_default_conf("is_https"))

# config.file_path = "server.yml"

main()
