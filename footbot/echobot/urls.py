# -*- coding:utf-8 -*-


from django.conf.urls import url

from footbot.echobot import views

urlpatterns = [
    url("^$", views.index),
    url('^callback/', views.callback),
]
