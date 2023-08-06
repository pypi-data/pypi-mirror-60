#!/usr/bin/env python3

import base64
import json
import os
import pickle
import pkg_resources

import dcyd.utils.constants as constants


def get_project_id():
    '''Returns the Google Cloud project_id found in the key .json file.'''

    with open(os.environ[constants.DCYD_CONFIG_ENV_VAR], 'r') as f:
        key = json.load(f)

    # Use brackets, since I want to raise an error if key not found.
    return key['project_id']


def get_account_data():
    '''Returns relevant Google Cloud account data found in the key .json file.'''
    with open(os.environ[constants.DCYD_CONFIG_ENV_VAR], 'r') as f:
        key = json.load(f)

    # Use brackets, since I want to raise an error if key not found.
    return {
        'account_id': key['client_id'],
        'account_email': key['client_email'],
        'private_key_id': key['private_key_id']
    }


def get_pubsub_topic_name():
    '''Returns the Google Cloud pubsub data found in the key .json file.'''
    with open(os.environ[constants.DCYD_CONFIG_ENV_VAR], 'r') as f:
        key = json.load(f)

    # Use brackets, since I want to raise an error if key not found.
    return key['pubsub_topic_name']


def get_mpm_client_data():
    dist = pkg_resources.get_distribution('dcyd')

    return {
        'mpm_client_name': dist.key,
        'mpm_client_version': dist.version,
    }


def make_json_serializable(obj):
    '''Check if obj is JSON-serializable.
    If so, leave it be. Else, pickle and base64-encode it.

    arg obj: object to be tested for JSON-serializability
    type obj: any Python object

    returns: a transformation of obj that is JSON-serializable.
    '''

    try:
        obj = json.loads(json.dumps(obj))
    except TypeError:
        try:
            obj = json.loads(
                json.dumps(
                    base64.b64encode( # encode the byte string into bytes
                        pickle.dumps(obj) # convert the object into a byte string
                    ).decode('ascii')
                )
            )
        except Exception as e:
            # This could be either un-pickle-able, un-b64encode-able, or
            # subsequently un-json-able.
            return str(e), None # let us know what's up
        else:
             return obj, 'pickle, base64'
    except Exception as e:
        return str(e), None # let us know what's up
    else:
        return obj, None
