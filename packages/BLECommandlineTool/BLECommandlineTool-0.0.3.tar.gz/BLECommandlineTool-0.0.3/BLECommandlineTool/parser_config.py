import argparse

BLUETOOTH_FILE_KEY = 'bluetooth'
APK_FILE_KEY = 'apk'
OUTPUT_FILE_KEY = 'output'
UPLOAD_ARGUMMENT='upload'
CHECK_EXISTS_ARGUMENT='check'
parser = argparse.ArgumentParser()
parser.add_argument('--' + BLUETOOTH_FILE_KEY, '-b', help="Analyse and upload Bluetooth file (for now not available)",type=str)
parser.add_argument('--' + APK_FILE_KEY, '-a', help="Analyse and upload APK file", type=str)
parser.add_argument('--' + OUTPUT_FILE_KEY, '-o', help="Specify output file default is the sha", type=str)
parser.add_argument('--' + UPLOAD_ARGUMMENT, '-u', help="upload the specified files", type=str)
parser.add_argument('--' + CHECK_EXISTS_ARGUMENT, '-c', help="", type=str)

print(__name__)

def get_args():
    """
    Checks if the extensions of the files provided are relevant
    :return:
    """
    args = vars(parser.parse_args())
    accepted_extensions = ['json', 'apk']
    print(accepted_extensions)
    if args[BLUETOOTH_FILE_KEY] is not None:
        extension = args[BLUETOOTH_FILE_KEY].split('.')[1]
        if extension not in accepted_extensions:
            raise Exception('Bluetooth extension provided: ', extension, ' should be one of: ', accepted_extensions)

    if args[APK_FILE_KEY] is not None:
        print(args[APK_FILE_KEY])
        name=args[APK_FILE_KEY]
        extension =name.split('.')[1]
        print(extension)
        if extension not in accepted_extensions:
            raise Exception('APK extension provided: ', extension, ' should be one of: ', accepted_extensions)

    return args
