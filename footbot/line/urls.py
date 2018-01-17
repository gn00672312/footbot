# -*- coding:utf-8 -*-


from django.conf.urls import url

from footbot.line import views

urlpatterns = [
    url("^$", views.index),
    url('^callback/', views.callback),
]
