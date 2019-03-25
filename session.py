from requests.exceptions import ConnectionError
import requests, json, logging, sys
from enum import Enum

import image_handler

class SessionStatus(Enum):
    INITIALIZED = 'INITIALIZED'
    GOT_PUB_KEY = 'GOT_PUB_KEY'
    GOT_ENCR_DATA = 'GOT_ENCR_DATA'
    FINALIZED = 'FINALIZED'

class OnboardingSession:
    """
    This class handles all the communcation with the session manager.

    session_id: Session ID of session retrieved from Session Manager

    TODO:
    - handle http non 200 responses
    """
    def __init__(self, api_url):
        """
        - Initiate the class as an object
        - Initiate a session at the session manager
        - Setup socket communication with session manager

        :param string api_url: URL of Session Manager to connect with
        """
        self.api_url = api_url
        self.error_message_init = "Could not connect to API [{}], please check connection".format(self.api_url)
        self.error_message_lost = "Connection with API lost [{}], please check connection".format(self.api_url)

        try:
            response = requests.post("{0}/{1}".format(self.api_url, 'init_onboarding'))
            if response.status_code != 200:
                #TODO: improve
                print(response)
                sys.exit(1)
            self.session_id = response.json()['session_id']
            logging.info("Started session [{}]".format(self.session_id))
        except ConnectionError as e:
            logging.error(e)
            logging.info(self.error_message_init)
            sys.exit(1)

    def get_data(self):
        """
        Get all the data of a session by its session ID
        """
        data = {"session_id": self.session_id}
        try:
            response = requests.post("{0}/{1}".format(self.api_url, 'get_session'), json=data)
            return response.json()['response']
        except ConnectionError as e:
            logging.error(e)
            logging.info(self.error_message_lost)

    def attach_encrypted_data(self, data):
        """
        Add encrypted data to the session

        :param string data: String retrieved from encryption library with encrypted data
        """
        data = {"encrypted_data": data, "session_id": self.session_id}
        try:
            response = requests.post("{0}/{1}".format(self.api_url, 'attach_encrypted_data'), json=data)
            logging.info("Added data to session [{}]".format(self.session_id))
            return response.json()['response']
        except ConnectionError as e:
            logging.error(e)
            logging.info(self.error_message_lost)

    # Deprecated
    def get_status(self):
        """
        Get status of the session by its session ID
        """
        data = {"session_id": self.session_id}
        try:
            response = requests.post("{0}/{1}".format(self.api_url, 'get_session_status'), json=data)
            return response.json()['response']
        except ConnectionError as e:
            logging.error(e)
            logging.info(self.error_message_lost)
