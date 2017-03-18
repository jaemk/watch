#!/usr/bin/env python

import os
import sys
from dotenv import load_dotenv
from pygame import camera
from pygame import image
import requests


ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_PATH)
TOKEN = os.environ.get('TOKEN')
HOST = os.environ.get('HOST')
CAM = os.environ.get('CAM')


def capture() -> str:
    camera.init()
    camera.list_cameras()
    cam = camera.Camera('/dev/video0', (800, 800))
    cam.start()
    im = cam.get_image()
    cam.stop()
    camera.quit()
    f = os.path.join(os.path.dirname(__file__), 'pic.png')
    image.save(im, f)
    return f


def accepting_uploads() -> bool:
    url = f'{HOST}/cam/status/'
    values = {'cam': CAM, 'token': TOKEN}
    r = requests.get(url, params=values)
    if r.status_code != 200:
        return
    return r.json().get('active')


def post(fname):
    # returns request
    url = f'{HOST}/upload/'
    files = {'pic': open(fname, 'rb')}
    values = {'cam': CAM, 'token': TOKEN}
    return requests.post(url, files=files, data=values)


def query_capture_upload():
    if accepting_uploads():
        fname = capture()
        post(fname)


def main(args):
    print(f'accepting uploads: {accepting_uploads()}')
    fname = capture()
    if args and args[0] == 'post':
        r = post(fname)
        print(r.json())


if __name__ == '__main__':
    main(sys.argv[1:])
