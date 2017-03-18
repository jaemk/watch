from django.core.management.base import BaseCommand, CommandError
import cam


class Command(BaseCommand):
    parser.add_argument('--capture', action='store_true', dest='capture')

    def handle(self, *_, **args):
        if args['capture']:
            cam.corder.query_capture_upload()

