from django.core.management.base import BaseCommand, CommandError
from cam import corder


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--capture', action='store_true', dest='capture')

    def handle(self, *_, **args):
        if args['capture']:
            corder.query_capture_upload()

