import base64
import zeep

from requests import Session
from zeep.transports import Transport
from PIL import Image

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class GHubClient:

    # Create client with endpoint being the IP of SOI, for example: "http://xxx.xxx.xxx.xx:8780/ghub/BasicGHubWebService?wsdl"

    def __init__(self, endpoint):
        self.endpoint = endpoint

        self.soap_client = None

        session = Session()
        session.verify = False
        transport = Transport(session=session)
        try:
            self.soap_client = zeep.Client(self.endpoint, transport=transport)
            print("GHubClient client connected.")
        except Exception as e:
            print("[ error ] GHubClient: error connecting to GHub.")
            print(e)

    def folder_exists(self, folder_name):
        # Return if folder_name already exists
        request_data = {
            'ghubRef': '/{}'.format(folder_name)
        }

        response = self.soap_client.service.exists(**request_data)
        # response == True/False
        return response

    def create_folder(self, folder_name):

        if self.folder_exists(folder_name):
            return

        request_data = {
            'parentGHubPathStr': '/',
            'folderName': folder_name
        }

        response = self.soap_client.service.createFolder(**request_data)

        folder_uuid = response
        return folder_uuid

    def dataset_exists(self, folder_name, dataset_name):
        # Return if folder_name already exists
        request_data = {
            'ghubRef': '/{}/{}'.format(folder_name, dataset_name)
        }

        response = self.soap_client.service.exists(**request_data)
        # response == True/False

        return response

    def get_dataset_uuid(self, folder_name, dataset_name):
        request_data = {
            'ghubRef': '/{}/{}'.format(folder_name, dataset_name)
        }

        response = self.soap_client.service.getDatasetInfo(**request_data)
        return response['datasetID']

    def create_dataset(self, folder_name, dataset_name):

        print("GHubClient.create_dataset: creating dataset {}".format(dataset_name))

        if self.dataset_exists(folder_name, dataset_name):
            print("GHubClient.create_dataset: dataset {} already exists!".format(dataset_name))
            return self.get_dataset_uuid(folder_name, dataset_name)

        request_data = {
            'ghubRef': '/{}'.format(folder_name),
            'metadata': {
                'Title': dataset_name,
                'ID': dataset_name,
                'Creator': '?',
                'security': '?',
                'GeographicExtent': {
                    'BoundingBox': {
                        'minx': '?',
                        'maxx': '?',
                        'miny': '?',
                        'maxy': '?'
                    }
                },
                'CreationDate': '?',
                'SearchRank': '?',
                'SetType': 'Generic Files'
            }
        }

        response = self.soap_client.service.createDataset(**request_data)

        print("GHubClient.create_dataset: response {}".format(response))

        # response is the (UU)ID of the new dataset
        return response

    def add_file(self, filename, data, folder_name, dataset_name):

        request_data = {
            'ghubRef': '/{}/{}'.format(folder_name, dataset_name),
            'addFileList': [
                {
                    'name': filename,
                    'contents': data
                }
            ]
        }

        response = self.soap_client.service.updateDataset(**request_data)

        print("GHubClient.add_file: response {}".format(response))


# Main Service
if __name__ == '__main__':
    ghub_connection = GHubClient("http://172.16.19.5:8780/ghub/BasicGHubWebService?wsdl")
    img = Image.open("350-3506490_search-icon-small-search-icon-small-png.png")
    ghub_connection.create_dataset("folder", "dataset")
    ghub_connection.add_file("filename", img, "folder", "dataset")
