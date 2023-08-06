#!/usr/bin/env python3

from functools import wraps
import inspect
import json
import uuid

from dcyd.utils.async_logger import async_logger
from dcyd.utils.async_publisher import async_publisher
from dcyd.utils.utils import (
    get_project_id,
    get_pubsub_topic_name,
    get_account_data,
    get_mpm_client_data,
    make_json_serializable
)

logger = async_logger()
publisher = async_publisher()

def mpm(func=None, **custom_kwargs): # decorator factory
    def decorator(func):
        """Decorator that logs function inputs and outputs
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            payload = format_payload(func, args, kwargs, custom_kwargs)

            # Log the request.
            push_request(payload)

            # Call the actual function.
            response = func(*args, **kwargs)

            # Log the response.
            push_response(payload, response)

            return response

        return wrapper

    if func:
        return decorator(func)

    return decorator


def push_request(payload):

    logger.info('mpm-request', payload)

    '''
    publisher.publish(
        publisher.topic_path(
            get_project_id(),
            get_pubsub_topic_name()
        ),
        data=json.dumps(payload).encode('utf-8')
    )
    '''

def push_response(payload, response):
    payload.get('request', {}).update(format_arguments([('request_response', response)]))

    logger.info('mpm-response', payload)

    '''
    publisher.publish(
        publisher.topic_path(
            get_project_id(),
            get_pubsub_topic_name()
        ),
        data=json.dumps(payload).encode('utf-8')
    )
    '''

def format_payload(func, func_args, func_kwargs, custom_kwargs):
    # bind arguments
    ba = inspect.signature(func).bind(*func_args, **func_kwargs)
    ba.apply_defaults()

    """
    b_method gauges whether the function is a method, in which case its first
    argument (which is a reference to its class instance) should be skipped. If
    func ever changes between method and function, we want the important args to
    retain their keys.

    Literature, and simple tests show that type(MyClass().my_method).__name__
    yields "method", but that does not work in the case at hand, given where the
    decorator is placed. So, the best I can do for now is to test if the leading
    argument has an attribute with the same name as the function. This is
    compelling but not airtight."""

    b_method = len(ba.args) and hasattr(ba.args[0], func.__name__)

    payload = {
        'function': {
            'function_name': func.__name__,
            'function_module': func.__module__,
            'function_sourcefile': inspect.getsourcefile(func),
            'function_type': 'method' if b_method else 'function'
        },
        'request': {
            'request_id': str(uuid.uuid4()),
            'request_arguments': {
                'args': format_arguments(
                    enumerate(ba.args[1:] if b_method else ba.args)
                ),
                'kwargs': format_arguments(ba.kwargs.items())
            },
        },
        'account': get_account_data(),
        'mpm_client': get_mpm_client_data(),
        'custom_data': format_arguments(custom_kwargs.items())
    }

    return payload


def format_arguments(args_list):
    """Formats how args and kwargs should appear. A requirement is that the
    result is valid json, so key names must be strings, and objects need to be
    converted to strings somehow."""
    
    def stringify_key(k):
        return '_' + str(k) if not isinstance(k, str) else k

    return {
        stringify_key(k): dict(
            zip(
                ('value', 'encoding', 'type'),
                (
                    *make_json_serializable(v),
                    type(v).__module__ + '.' + type(v).__name__
                )
            )
        ) for k, v in args_list
    }


if __name__ == '__main__':
    @mpm(model_version='1a', treatment_group='A')
    def f(*args, qwer=6, **kwargs):
        return 'sassy'

    f(4, {4:'a'}, bad="asdf", cool={'a':6})

    @mpm
    def g(*args, qwer=6, **kwargs):
        return 'sassy'

    g(4, 'a', bad="asdf", cool={'a':6})

    class C(object):
        @mpm
        def m(self):
            return 4

    C().m()
