import json
def output_to_file(apk_json, bluetooth_json, file_name):
    if file_name is None:
        file_name = ""
        if apk_json is not None:
            file_name += apk_json['str']
        if bluetooth_json is not None:
            file_name += bluetooth_json['str']
        file_name += '.js'

    with open(file_name, 'w') as file:
        # get the relevant data from server
        # append it to the file
        print("hi")


def get_json(file_name):
    with open(file_name) as js:
        return json.load(js)
