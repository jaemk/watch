#!/usr/bin/env python

import os
import sys
import subprocess

from dotenv import load_dotenv
import requests


BASE_DIR = os.path.dirname(__file__)
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(ENV_PATH)
TOKEN = os.environ.get('TOKEN')
HOST = os.environ.get('HOST')
CAM = os.environ.get('CAM')


def capture():  # -> str
    img_path = '{}/image.jpg'.format(BASE_DIR)
    subprocess.check_call('fswebcam -r 640x480 -D 2 {}'.format(img_path).split(' '))
    return img_path


def accepting_uploads():  # -> bool
    url = '{}/cam/status/'.format(HOST)
    values = {'cam': CAM, 'token': TOKEN}
    r = requests.get(url, params=values)
    if r.status_code != 200:
        return
    return r.json().get('active')


def post(fname):  # -> request-response
    url = '{}/upload/'.format(HOST)
    files = {'pic': open(fname, 'rb')}
    values = {'cam': CAM, 'token': TOKEN}
    return requests.post(url, files=files, data=values)


def query_capture_upload():
    if accepting_uploads():
        fname = capture()
        post(fname)


def main(args):
    acc_ups = accepting_uploads()
    print('accepting uploads: {}'.format(acc_ups))
    if not acc_ups:
        return
    fname = capture()
    if args and args[0] == 'post':
        r = post(fname)
        print('resp -> {}'.format(r.json()))


if __name__ == '__main__':
    main(sys.argv[1:])
