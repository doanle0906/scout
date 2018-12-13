# -*- coding: UTF-8 -*-

import logging
import requests
import json
from werkzeug.datastructures import Headers

LOG = logging.getLogger(__name__)

def send_request(matchmaker_url, json_patient, token, external=True):
    """Send patient queries to a MatchMaker instance

        Args:
            matchmaker_url(str): url of a matchmaker server
            json_patient: a patient object as in https://github.com/ga4gh/mme-apis or an ID(str)
            token(str): authorization token
            external(bool): True if query is performed on connected nodes.
                            Otherwise query is performed on internal MatchBox database (scout patients only)

        Returns:


    """
    # create request headers
    headers = Headers()
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/vnd.ga4gh.matchmaker.v1.0+json', "X-Auth-Token": token}

    json_response = None
    data = {}
    method = 'POST'
    if external:
        url = '/'.join([matchmaker_url, 'match', 'external'])
    else:
        url = '/'.join([matchmaker_url, 'match'])

    LOG.info('sending HTTP request to server..')
    # send request and get response from server
    server_return = requests.request(
        method = method,
        url = url,
        headers = headers,
        data = json.dumps(json_patient)
    )
    # workaround to take into account a malformed json response from matchmaker server:
    try:
        json_response = server_return.json()
    except Exception as json_exp:
        json_response = server_return.text
    LOG.info('server returns the following response: {}'.format(json_response))

    return json_response
