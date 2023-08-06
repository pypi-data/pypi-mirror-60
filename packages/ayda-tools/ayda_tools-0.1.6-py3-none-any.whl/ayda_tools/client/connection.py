import json
from time import sleep
from typing import Optional

import requests
import logging

logger = logging.getLogger(__name__)


class ServerConnection:
    def __init__(self, server_address: str, server_port: str, username: str, pw: str):
        self.username = username
        self.server_port = server_port
        self.server_address = server_address
        self.pw = pw

    def send_server_request(
        self, api_call: str, data=None, method="POST"
    ) -> Optional[dict]:
        """
        sends a server request

        Args:
            api_call: the endpoint where the request is sent to
            data: Json formatted payload to send
            method: method to us

        Returns:

        """
        address = "{}:{}/{}".format(self.server_address, self.server_port, api_call)
        # try three times in case of errors
        for i in range(3):
            try:
                auth = (self.username, self.pw)
                if method == "POST":
                    response = requests.post(address, auth=auth, data=data)
                elif method == "PUT":
                    response = requests.put(address, auth=auth, data=data)
                elif method == "GET":
                    response = requests.get(address, auth=auth, data=data)
                else:
                    raise ValueError("Unknown method")

            except requests.exceptions.RequestException as e:
                logger.info(e)
                return

            if response.status_code != 200:
                # error occurred
                logger.info("Could not access %s", address)
                logger.info(response.text)
                sleep(5)
                continue
            try:
                response_content = response.json()
                return response_content
            except json.JSONDecodeError:
                logger.warning("could parse data to json: \n%s", response.text)
                return None
        return
