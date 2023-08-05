from __future__ import absolute_import
import os

# flake8: noqa

from pupilcloud.configuration import Configuration
from pupilcloud.api_client import ApiClient

# import apis into api package
from pupilcloud.api.auth_api import AuthApi
from pupilcloud.api.labels_api import LabelsApi
from pupilcloud.api.recordings_api import RecordingsApi
from pupilcloud.api.templates_api import TemplatesApi
from pupilcloud.api.wearers_api import WearersApi


class Api(
    AuthApi,
    LabelsApi,
    RecordingsApi,
    TemplatesApi,
    WearersApi,
    
):
    """ PupilCloud API client """
    def __init__(
        self,
        api_key,
        host="https://api.cloud.pupil-labs.com",
        downloads_path=None,
        verify_ssl=True,
    ):
        """
        Create a PupilCloud API client

        :param api_key: api key for auth
        :param host: host for the api
        :param downloads_path: path to folder to store downloads (defaults tmp)
        :param verify_ssl: enable/disable ssl verification
        """

        self.config = Configuration()
        self.config.verify_ssl = verify_ssl
        self.config.host = host
        self.config.api_key["api-key"] = api_key
        self.config.temp_folder_path = downloads_path
        if downloads_path:
            os.makedirs(downloads_path, exist_ok=True)

        self.api_client = ApiClient(configuration=self.config)
