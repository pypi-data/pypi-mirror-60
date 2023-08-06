#!/usr/bin/env python3

from functools import wraps
import datetime as dt
import inspect
import json
import uuid

from dcyd.utils.async_logger import async_logger
from dcyd.utils.async_publisher import async_publisher
import dcyd.utils.constants as constants
from dcyd.utils.utils import (
    get_project_id,
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
            logger.info('mpm-request', payload)

            # Call the actual function.
            response = func(*args, **kwargs)

            # Log the response.
            payload = add_response(payload, response)
            logger.info('mpm-response', payload)
            publish_payload(payload)

            return response

        return wrapper

    if func:
        return decorator(func)

    return decorator


def add_response(payload, response):
    payload['request'].update({
        'request_response': make_json_serializable(response),
        'request_response_timestamp': dt.datetime.utcnow().isoformat()
    })

    return payload


def publish_payload(payload):
    publisher.publish(
        publisher.topic_path(
            get_project_id(),
            constants.MPM_PUBSUB_TOPIC
        ),
        data=json.dumps(payload).encode('utf-8')
    )


def format_payload(func, func_args, func_kwargs, custom_kwargs):
    """
    """
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
            'request_timestamp': dt.datetime.utcnow().isoformat(),
            'request_arguments': {
                'args': make_json_serializable(ba.args[1:] if b_method else ba.args),
                'kwargs': make_json_serializable(ba.kwargs)
            }
        },
        'account': get_account_data(),
        'mpm_client': get_mpm_client_data(),
        'custom_data': make_json_serializable(custom_kwargs)
    }

    return payload
