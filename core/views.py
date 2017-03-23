from django.shortcuts import render, redirect
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import HttpResponse as http_resp
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.conf import settings

import os
import pathlib
import json
import uuid
import mimetypes

from core import forms
from core import models


class BaseView(View):
    """
    Base View for all authenicated endpoints.
    Subclasses can implement custom `bouncer` methods as needed
    or override class variables `bouncer_allow_**`
    """
    bouncer_allow_all = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def json_resp(content, **kwargs):
        """
        Wrapper http-resp to auto populate json params.

        :param content: dict of serializable things to serialize to json
        :param **kwargs: any additional kwargs will be passed to HttpResponse
        """
        indent = sort_keys = None
        if settings.DEBUG:
            indent = 4
            sort_keys = True
        return http_resp(json.dumps(content, indent=indent, sort_keys=sort_keys),
                            content_type='Application/json',
                            **kwargs)

    def bouncer(self, request):
        """
        For supporting various authentication checks before processing the request.
        Subclassed views can implement their own specific checks.
        Passing checks should return a falsey value, any truthy value is
        assumed to be an http-resp and will be returned immediately.
        """
        if self.bouncer_allow_all:
            return
        if not request.user.is_authenticated():
            return redirect('core:login')

    def render(self, request, template, context=None):
        """
        Wrapped render to inject context values common to all subclassed views.
        Arguments mirror the default render function.
        """
        context = context if context is not None else {}
        default_context = {
            'user': request.user,
            'authenticated': request.user.is_authenticated(),
        }
        context.update(default_context)
        return render(request, template, context)

    def dispatch(self, request, *args, **kwargs):
        """
        Handling of requests will first invoke the current bouncer,
        then look for a 'handle' method to process both gets & posts.
        If no handle method is found, request processing falls through
        to django's default behavior of looking for either a 'get' or 'post'
        method depending on the current request.METHOD
        """
        err_resp = self.bouncer(request)
        if err_resp:
            return err_resp

        if hasattr(self, 'handle'):
            return self.handle(request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)


class Login(BaseView):
    """
    Validate and serve login form
    """
    bouncer_allow_all = True
    def handle(self, request):
        if request.method == 'GET':
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


class Home(BaseView):
    """
    Default landing page
    """
    def handle(self, request):
        cams = models.Cam.objects.all()
        return self.render(request, 'core/home.html', {'cams': cams})


def valid_cam_token(request) -> bool:
    """
    Check given request for a valid camera api-token
    """
    token = request.POST.get('token') or request.GET.get('token')
    if not token:
        return
    token = uuid.UUID(token)
    try:
        return models.Token.objects.get(value=token).active
    except:
        return


class CameraStatus(BaseView):
    """
    Endpoint to service both token holders and webpages
    returning the current status of the request `cam` id_name
    """
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
    """
    Toggle the `active` state of the given `cam_id_name`
    """
    def post(self, request):
        data = json.loads(request.body)
        cam = data.get('cam_id_name')
        action = data.get('action')
        if action == 'activate':
            models.Cam.objects.filter(id_name=cam).update(active=True)
        elif action == 'disable':
            models.Cam.objects.filter(id_name=cam).update(active=False)

        return self.json_resp({'ok': 'ok'})


class SecureMedia(BaseView):
    """
    Uploaded files are stored under media/
    We want to serve them directly through nginx instead of python, but also
    need to make sure access is authorized. If we just have nginx serve directly
    from media/, the files will be available to unauthenticated requests.

    Nginx is setup with an 'internal' location named /protected/, aliased to our
    media/ directory. All requests to /media/* urls will be routed to this view
    where they'll be redirected to our internal /protected/ url using nginx's
    X-Accel-Redirect header.
    """
    def get(self, request):
        content_type, _encoding = mimetypes.guess_type(request.path_info)

        # change /media/<filename> to /protected/<filename>
        path = pathlib.Path(request.path_info)
        path = os.path.join('/protected', *path.parts[2:])

        resp = http_resp()
        resp['Content-Type'] = f'{content_type}'
        resp['X-Accel-Redirect'] = f'{path}'
        # to invoke downloads
        # _, filename = os.path.split(request.path_info)
        # resp['Content-Disposition'] = f'attachment; filename={filename}'
        return resp


@csrf_exempt
def camera_upload(request):
    """
    Endpoint for receiving camera posts. Ignore the lack of csrf tokens
    and instead ensure a valid api-token has been sent in the post params.
    """
    if not valid_cam_token(request):
        return BaseView.json_resp({'error': 'Invalid or missing api token!'})
    cam_id_name = request.POST.get('cam')
    cam = models.Cam.objects.get(id_name=cam_id_name)
    if not cam.active:
        return BaseView.json_resp({'error': f'{cam_id_name} is currently disabled'})
    pic = request.FILES.get('pic')
    snap = models.Snap.objects.create(cam=cam, image=pic)
    return BaseView.json_resp({'ok': 'ok'})

