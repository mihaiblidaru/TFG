from django.db import models
from django.template.defaultfilters import slugify

from django.core.exceptions import ObjectDoesNotExist, ValidationError


class Host(models.Model):
    name = models.CharField(max_length=100, unique=True, default="")
    slug = models.SlugField(unique=True, max_length=128)
    ip = models.GenericIPAddressField()
    port = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.ip}:{self.port}"

    def __unicode__(self):
        return str(self)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Host, self).save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        super(Host, self).validate_unique(exclude=exclude)

        if self.id:
            try:
                Host.objects.exclude(id=self.id).get(slug=slugify(self.name))
                raise ValidationError({'name': ["This host name generates a slug that already exists."]})
            except ObjectDoesNotExist:
                pass
        else:
            # si estamos añadiendo
            try:
                Host.objects.get(slug=slugify(self.name))
                raise ValidationError({'name': ["This host name generates a slug that already exists."]})
            except ObjectDoesNotExist:
                pass


class Subscription(models.Model):
    host = models.ForeignKey(Host, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=100, default='periodic')
    data = models.CharField(max_length=100)
    interval = models.PositiveIntegerField(default=10000)


