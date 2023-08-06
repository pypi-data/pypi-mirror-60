# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import sys
from docker_tasks.cli import main

__title__ = "docker-tasks"
__version__ = "0.0.8"
__author__ = "Reimund Klain"
__license__ = "BSD"
__copyright__ = "Copyright 2020 Reimund Klain"

if __name__ == "__main__":
    sys.exit(main())
