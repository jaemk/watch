# on.Watch

> Service for aggregating output from multiple time-lapsed webcams

##### still a work in progress.

## Client Setup
The listening server will accept image posts from any number of clients. Clients must make all requests using a valid api-token and a valid camera id-name, both created on the listening server. Client will check if the listening server is accepting images for the given camera before capturing an image and uploading it. No images will be captured if the listening server says collection for the given camera is disabled.
 * client code requires python3^
 * create a virtualenv under watch/cam and `pip install -r -client-requirements.txt`
 * install fswebcam, `sudo apt-get fswebcam`
 * copy `.env_copy` to `.env` and update with your host/token/cam-id-name
 * copy `cam/capture_copy.sh` to `cam/capture.sh` and update `PROJ_PATHs`
 * put the above in a cron job to run as frequently as you desire

## Server Setup
This service is setup as a master server listening for image posts on registered cameras.
 * provision a server to listen
 * install python3.6^
 * install postgres, nginx
 * in a virtaulenv `pip install -r requirements.txt`
 * copy `gunicorn_copy.conf` to `/etc/init/gunicorn.conf` and update `USER` and `PATH_TO_PROJ_BASE`
 * `initctl reload-configuration` to pull in our gunicorn commands (see notes in comments for upstart installation)
 * copy `nginx_copy.conf` to `/etc/nginx/sites-available/watch` and update `DOMAIN`, `PATH_TO_PROJ_BASE`, `PROJ_APP_NAME`
 * symlink /etc/nginx/sites-available/watch to /etc/nginx/sites-enabled/watch, may need to remove sites-enabled/default
 * setup your ssl certs with letsencrypt, see `letsencrypt.info`
 * `sudo service nginx restart`, `sudo service gunicorn start`
 * add cameras and api tokens using either the django-admin interface or the admin management command `./manage.py admin --help`

