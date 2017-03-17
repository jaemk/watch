from django.shortcuts import render, redirect
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import HttpResponse as http_resp
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.conf import settings

import json
import uuid

from core import forms
from core import models


class BaseView(View):
    bouncer_allow_all = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def json_resp(content, **kwargs):
        """For convenience... 'content' must be a dictionary"""
        indent = sort_keys = None
        if settings.DEBUG:
            indent = 4
            sort_keys = True
        return http_resp(json.dumps(content, indent=indent, sort_keys=sort_keys),
                            content_type='Application/json',
                            **kwargs)

    def bouncer(self, request):
        if self.bouncer_allow_all:
            return
        if not request.user.is_authenticated():
            return redirect('core:login')

    def render(self, request, template, context=None):
        context = context if context is not None else {}
        default_context = {
            'user': request.user,
            'authenticated': request.user.is_authenticated(),
        }
        context.update(default_context)
        return render(request, template, context)

    def dispatch(self, request, *args, **kwargs):
        err_resp = self.bouncer(request)
        if err_resp:
            return err_resp

        if hasattr(self, 'handle'):
            return self.handle(request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)


class Login(BaseView):
    bouncer_allow_all = True
    def handle(self, request):
        if request.method == 'GET':
            # return form
            form = forms.LoginForm()
        else:
            form = forms.LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect('core:home')

        return self.render(request, 'core/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('core:home')


def into_home(request):
    return redirect('core:home')


class Home(BaseView):
    def handle(self, request):
        cams = models.Cam.objects.all()
        return self.render(request, 'core/home.html', {'cams': cams})


class ListImages(BaseView):
    def get(self, request):
        return self.render(request, 'core/home.html', {})


def valid_cam_token(request):
    token = request.POST.get('token') or request.GET.get('token')
    if not token:
        return
    token = uuid.UUID(token)
    try:
        return models.Token.objects.get(value=token).active
    except:
        return


class CameraStatus(BaseView):
    def bouncer(self, request):
        if valid_cam_token(request):
            return
        return super().bouncer(request)

    def get(self, request):
        cam = request.GET.get('cam')
        if cam:
            active = models.Cam.objects.get(id_name=cam).active
            return self.json_resp({'active': active})
        return self.json_resp({'error': 'invalid camera id_name, query param "cam" is required'}, status=500)


class ToggleCamera(BaseView):
    def post(self, request):
        data = json.loads(request.body)
        cam = data.get('cam_id_name')
        action = data.get('action')
        if action == 'activate':
            models.Cam.objects.filter(id_name=cam).update(active=True)
        elif action == 'disable':
            models.Cam.objects.filter(id_name=cam).update(active=False)

        return self.json_resp({'ok': 'ok'})


@csrf_exempt
def camera_upload(request):
    if not valid_cam_token(request):
        return BaseView.json_resp({'error': 'Invalid or missing api token!'})
    cam_id_name = request.POST.get('cam')
    cam = models.Cam.objects.get(id_name=cam_id_name)
    if not cam.active:
        return BaseView.json_resp({'error': f'{cam_id_name} is currently disabled'})
    pic = request.FILES.get('pic')
    snap = models.Snap.objects.create(cam=cam, image=pic)
    return BaseView.json_resp({'ok': 'ok'})
