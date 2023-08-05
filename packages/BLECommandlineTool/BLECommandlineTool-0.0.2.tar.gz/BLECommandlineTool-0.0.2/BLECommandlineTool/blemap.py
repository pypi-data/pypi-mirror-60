import json
import os
from .common.utils import get_json
from .parser_config import get_args
from .parser_config import BLUETOOTH_FILE_KEY
from .parser_config import APK_FILE_KEY
from .parser_config import OUTPUT_FILE_KEY
from .parser_config import UPLOAD_ARGUMMENT
from .parser_config import CHECK_EXISTS_ARGUMENT
from .api.BLEBackendServices import BLEBackendServices
from BLECryptracer_BLEMAP.BLECryptracer import analyse_file
from BLECryptracer_BLEMAP.common.hash import sha256sum


def analyse_apk(apk_file):
    print('analysing=========', apk_file)
    output_js_file = apk_file.split('.')[0] + '.json'
    print(output_js_file)
    file = analyse_file(apk_file, output_js_file)
    print(file)
    return output_js_file


def resolve_apk(file_name, upload_argument):
    """

    :param file_name: name of file to analyse
    :param upload_argument: if None, result will not be uploaded
    :return: json, upload id
    """
    # extension can either be apk or bluetooth here
    if file_name is None:
        return None, None
    json_file_name = file_name
    if file_name.split('.')[1] == 'apk':
        json_file_name = analyse_apk(file_name)
    apk_json = get_json(json_file_name)
    object_id = None
    if upload_argument is not None:
        response = BLEBackendServices.register_apk_analysis(apk_json)
        object_id = response.json()['id']
    return apk_json, object_id


def get_file_name(file_name):
    """
    converts name of file with directory path
    to file name alone
    /dir/dir2/file_name.ext => file_name.ext
    :param file_name:
    :return:
    """
    by_dir = file_name.split('/')
    file_name = by_dir[len(by_dir) - 1]
    return file_name


def resolve_bluetooth(file_name, upload_argument):
    """
    :param file_name: name of file to analyse
    :param upload_argument: if None, result will not be uploaded
    :return: json, upload id
    """
    print(file_name, upload_argument)
    # extension can either be apk or bluetooth here
    if file_name is None:
        return None, None
    json_file_name = file_name
    # right now just works with json.
    # if file_name.split('.')[1] == 'apk':
    #     json_file_name = analyse_apk(file_name)
    bluetooth_json = get_json(json_file_name)
    object_id = None
    if upload_argument is not None:
        response = BLEBackendServices.register_bluetooth_analysis(bluetooth_json)
        object_id = response.json()['id']
    return bluetooth_json, object_id


def resolve_binding(apk_id, bluetooth_id):
    if apk_id is not None and bluetooth_id is not None:
        BLEBackendServices.bind_analysis(apk_id, bluetooth_id)


def output_to_file(file_name, bluetooth_upload_id, bluetooth_json, apk_upload_id, apk_json):
    """
    A parameter can be passed as None, e.g. if bluetooth_json is not available, but upload id is.
    :param file_name: file name to which the output will be dumped
    :param bluetooth_upload_id: upload id (data to be retrieved from server)
    :param bluetooth_json: json to be dumped
    :param apk_upload_id: upload id (data to be retrieved from server)
    :param apk_json: json to be dumped.
    :return:
    """
    print("OUTPUTTING TO FILE: ", file_name)
    if file_name is None:
        file_name = ""
        if apk_json is not None:
            print(apk_json)
            sects = apk_json['filename'].split('/')
            print("-----------------", sects)
            file_name += sects[len(sects) - 1]
            file_name = file_name.split('.')[0]
            file_name += '.js'
        if bluetooth_json is not None:
            sects = apk_json['filename'].split('/')
            file_name += sects[len(sects) - 1]
            file_name = file_name.split('.')[0]
            file_name += '.js'
    if bluetooth_upload_id is not None and apk_upload_id is not None:
        output_json = BLEBackendServices.get_bluetooth_analysis({'id': bluetooth_upload_id})
    else:
        if bluetooth_json is not None and apk_upload_id is not None:
            # some combination thing
            output_json = {
                'apk_analysis': apk_json,
                'apk_object_id': apk_upload_id,
                'bluetooth_analysis': bluetooth_json,
                'bluetooth_object_id': bluetooth_upload_id,
            }
        elif bluetooth_json is not None:
            output_json = bluetooth_json
        else:
            output_json = apk_json
    with open(file_name, 'w') as file:
        # get the relevant data from server
        # append it to the file
        file.write(json.dumps(output_json))


def output_existing(check_arg, bluetooth_file_name, apk_file_name):
    """

    :param check_arg: if None will not execute.
    :param bluetooth_file_name: file name to be checked on the server
    :param apk_file_name: file name to be checked on the server
    :return: the list of analysis found on the server as a dictionary.
    """
    if check_arg is None:
        return

    outputs = {}
    if bluetooth_file_name is not None:
        outputs.update({'bluetooth_results': BLEBackendServices.get_bluetooth_analysis_list({
            'sha_256': sha256sum(bluetooth_file_name)
        })})
    if apk_file_name is not None:
        outputs.update({'apk_results': BLEBackendServices.get_apk_analysis_list({
            'sha_256': sha256sum(apk_file_name)
        })})
    print(outputs)
    return outputs


def main():
    """
    get arguments
    get output/upload bluetooth arguments
    manage apk arguments
    manage output argument

    :return:
    """
    try:
        print('ARGS: ')
        args = get_args()
        print(args)
        bluetooth_json, bluetooth_upload_id = resolve_bluetooth(args[BLUETOOTH_FILE_KEY], args[UPLOAD_ARGUMMENT])
        print('BLUE')
        apk_json, apk_upload_id = resolve_apk(args[APK_FILE_KEY], args[UPLOAD_ARGUMMENT])
        print('apk')
        resolve_binding(apk_upload_id, bluetooth_upload_id)
        print('resolve')
        output_to_file(args[OUTPUT_FILE_KEY], bluetooth_upload_id, bluetooth_json, apk_upload_id, apk_json)
        print('out')
        output_existing(args[CHECK_EXISTS_ARGUMENT], args[BLUETOOTH_FILE_KEY], args[APK_FILE_KEY])
    except Exception as e:
        print("Error: ", e)


if __name__ == '__main__':
    main()
