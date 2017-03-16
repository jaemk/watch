from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class TimeStamped(models.Model):
    """ Abstract base class to provide inheritable timestamps. """
    date_created = models.DateTimeField(editable=False, blank=True)
    date_modified = models.DateTimeField(blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """ Override save to update stamps """
        if not self.id:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()
        return super(TimeStamped, self).save(*args, **kwargs)


class Cam(TimeStamped):
    id_name = models.TextField(null=False, unique=True)
    description = models.TextField()
    active = models.BooleanField(default=False)

    @property
    def snaps(self):
        return self.snap_set.order_by('-date_created')

    @property
    def snaps_limited(self):
        return self.snaps[:6]

    def __repr__(self):
        return f'<Cam.{self.pk}[{self.id_name}, {self.description[:15]}]>'

    def __str__(self):
        return self.__repr__()


class Snap(TimeStamped):
    cam = models.ForeignKey('Cam')
    image = models.ImageField()

    def __repr__(self):
        return f'<Snap.{self.pk}[{self.date_created}]>'

    def __str__(self):
        return self.__repr__()


class Archive(TimeStamped):
    cam = models.ForeignKey('Cam')
    tarball = models.FileField()


class Token(TimeStamped):
    cam = models.ForeignKey('Cam')
    name = models.TextField()
    value = models.UUIDField(default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)

    def __repr__(self):
        return f'<Token.{self.pk}[{self.name}][{self.cam}]>'

    def __str__(self):
        return self.__repr__()

