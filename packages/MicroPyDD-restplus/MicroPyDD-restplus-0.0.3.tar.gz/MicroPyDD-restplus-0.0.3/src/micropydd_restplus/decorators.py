import inspect
import micropydd
from functools import wraps
from typing import Type

from micropydd.actions import Action


def inject_actions(action: Type[Action]):
    """
    Inject actions passed by param
    :param action:
    :return:
    """
    @wraps(action)
    def decorated_function(*args, **kwargs):

        inspection = inspect.getfullargspec(action)
        for key, value in inspection.annotations.items():
            if issubclass(value, Action):
                kwargs[key] = micropydd.app_context.get(value)
        return action(*args, **kwargs)
    return decorated_function
