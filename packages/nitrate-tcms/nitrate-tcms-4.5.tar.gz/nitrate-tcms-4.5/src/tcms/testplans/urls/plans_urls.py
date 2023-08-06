# -*- coding: utf-8 -*-

from django.conf.urls import url
from .. import views

urlpatterns = [
    url(r'^$', views.all, name='plans-all'),
    url(r'^new/$', views.new, name='plans-new'),
    url(r'^ajax/$', views.ajax_search, name='plans-ajax-search'),
    url(r'^treeview/$', views.tree_view, name='plans-treeview'),
    url(r'^clone/$', views.clone, name='plans-clone'),
    url(r'^printable/$', views.printable, name='plans-printable'),
    url(r'^export/$', views.export, name='plans-export'),
    # url(r'^component/$', views.component, name='plans-component'),

    url(r'^component/$', views.PlanComponentsActionView.as_view(),
        name='plans-component-actions'),
]
