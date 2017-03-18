from django.core.management.base import BaseCommand, CommandError
from core import models


class Command(BaseCommand):
    _help = "** Create, List, Revoke Camera Tokens **"

    def add_arguments(self, parser):
        parser.add_argument('-lt', '--list-tokens', action='store_true', dest='list_tokens')
        parser.add_argument('-nt', '--new-token', nargs=2, type=str, action='store', dest='new_token_name')
        parser.add_argument('-r', '--revoke', nargs=1, type=str, action='store', dest='revoke_token_name')
        parser.add_argument('-lc', '--list-cams', action='store_true', dest='list_cams')
        parser.add_argument('-nc', '--new-cam', action='store', dest='new_cam_name')

    @staticmethod
    def _check(cam):
        return "\u2713" if cam.active else 'X'

    def handle(self, *_, **args):
        if args['list_cams']:
            cams = models.Cam.objects.all()
            print(' ** Available Cameras')
            for cam in cams:
                print(f" - [{self._check(cam)}] {cam.id_name: >5}")
            return

        if args['list_tokens']:
            tokens = models.Token.objects.all()
            print(' ** Current Tokens:')
            for token in tokens:
                print(f" - ({token.cam.id_name}[{self._check(token.cam)}]) {token.name: >5}: {token.value.hex}")
            return

        if args['new_token_name']:
            new_name = args['new_token_name'][0]
            cam_id_name = args['new_token_name'][1]
            if models.Token.objects.filter(name=new_name).exists():
                raise CommandError(f"token with name '{new_name}' already exists.")
            if not models.Cam.objects.filter(id_name=cam_id_name).exists():
                raise CommandError(f"No cam with id-name '{cam_id_name}' found.")
            cam = models.Cam.objects.get(id_name=cam_id_name)
            token = models.Token.objects.create(name=new_name, cam=cam)
            print(f" ** Created token [for {cam.id_name}]! {token.name}: {token.value.hex}")
            return

        if args['revoke_token_name']:
            token_name = args['revoke_token_name'][0]
            if not models.Token.objects.filter(name=token_name).exists():
                raise CommandError(f"token with name '{token_name}' does not exist.")
            models.Token.objects.get(name=token_name).delete()
            print(f" ** Deleted token '{token_name}'!")

