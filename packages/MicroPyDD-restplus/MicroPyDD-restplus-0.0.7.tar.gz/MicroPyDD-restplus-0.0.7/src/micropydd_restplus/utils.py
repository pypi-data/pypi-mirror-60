from typing import List

from flask_restplus import Namespace

from micropydd_restplus.namespaces.logger import loggers_ns
from micropydd_restplus.namespaces.misc import misc_ns


def base_resources() -> List[Namespace]:
    """
    Return basic resources from pvtrest.resource
    :return:
    """
    return [loggers_ns, misc_ns]
