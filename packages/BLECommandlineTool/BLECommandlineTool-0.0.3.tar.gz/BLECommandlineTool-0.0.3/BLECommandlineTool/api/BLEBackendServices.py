import json
import requests
import urllib

URL_PREFIX = 'https://ble-service.herokuapp.com/'

HEADERS = {
    'Content-Type': 'application/json'
}


class BLEBackendServices:
    def __init__(self):
        pass

    @staticmethod
    def clean_apk_json(js):
        """
        Things that need cleaning to work with backend
        :param js:
        :return:
        """
        for key, val in js.items():
            print(key)
        # Keys that are potentially named incorrectly:
        corrections = [('classic_uuids', 'classic_uudis'),
                       ('ble_uuids', 'ble_uudis'),
                       ]
        for c in corrections:
            try:
                js[c[0]] = js.pop(c[1])
            except Exception as e:
                continue
        # correct file name:
        split = js['filename'].split('/')
        js['filename'] = split[split.__len__() - 1]

        # Error values are just None:
        for key in js:
            if js[key] == 'Error':
                js[key] = None
        # all boolans should be either True False or None
        return js

    @staticmethod
    def update_bluetooth(bluetooth_id, data):
        headers = {
            'Content-Type': 'application/json'
        }
        URL = URL_PREFIX + 'bluetooth/analysis/' + bluetooth_id.__str__()

        response = requests.put(url=URL, headers=headers, data=json.dumps(data))
        print(response)
        return response

    @staticmethod
    def update_apk(apk_id, data):
        headers = {
            'Content-Type': 'application/json'
        }
        URL = URL_PREFIX + 'cryptracer_apk/analysis/' + apk_id.__str__()

        response = requests.put(url=URL, headers=headers, data=json.dumps(data))
        print(response)
        return response

    @staticmethod
    def register_apk_analysis(analysis_json):
        print("UPLOADING: ===========")
        print(analysis_json)
        headers = {
            'Content-Type': 'application/json'
        }
        analysis_json = BLEBackendServices.clean_apk_json(analysis_json)
        URL = URL_PREFIX + 'cryptracer_apk/analysis/'
        response = requests.post(url=URL, headers=headers, data=json.dumps(analysis_json))
        print(response)
        return response

    @staticmethod
    def register_bluetooth_analysis(analysis_json):
        headers = {
            'Content-Type': 'application/json'
        }
        analysis_json = BLEBackendServices.clean_bluetooth_json(analysis_json)
        URL = URL_PREFIX + 'bluetooth/analysis/'
        response = requests.post(url=URL, headers=headers, data=json.dumps(analysis_json))
        print(response)
        return response

    @staticmethod
    def bind_analysis(apk_id, bluetooth_id):
        # only need to update one as it's a one to one relationship :D
        # update_apk(apk_id, {'bluetooth_analysis': bluetooth_id})
        BLEBackendServices.update_bluetooth(bluetooth_id, {'cryptracer_apk_analysis': apk_id})

    @staticmethod
    def clean_bluetooth_json(js):
        return js

    @staticmethod
    def get_bluetooth_analysis(query_dict):
        headers = {
            'Content-Type': 'application/json'
        }
        query = urllib.parse.urlencode(query_dict, doseq=True)
        print(query)
        URL = URL_PREFIX + 'bluetooth/analysis/?' + query

        response = requests.get(url=URL, headers=headers)
        print(response)
        return response.json()

    @staticmethod
    def get_bluetooth_analysis_list(query_dict):
        headers = {
            'Content-Type': 'application/json'
        }
        query = urllib.parse.urlencode(query_dict, doseq=True)
        print(query)
        URL = URL_PREFIX + 'bluetooth/analysis?' + query

        response = requests.get(url=URL, headers=headers)
        print(response)
        return response.json()

    @staticmethod
    def get_apk_analysis_list(query_dict):
        headers = {
            'Content-Type': 'application/json'
        }
        query = urllib.parse.urlencode(query_dict, doseq=True)
        print(query)
        URL = URL_PREFIX + 'cryptracer_apk/analysis?' + query

        response = requests.get(url=URL, headers=headers)
        print(response)
        return response.json()
