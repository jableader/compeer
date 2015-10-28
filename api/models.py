__author__ = 'Jableader'

from django.db import models
from django.contrib.auth.models import User


class List(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=25, blank=False)
    description = models.CharField(max_length=500, blank=False)
    action_word = models.CharField(max_length=15, default='better')


class Item(models.Model):
    list = models.ForeignKey(List, related_name='items')
    caption = models.CharField(max_length=25)
    image = models.ImageField(null=True)
    description = models.CharField(max_length=140)
    score = models.IntegerField(default=0)

    class Meta:
        ordering = ['-score']