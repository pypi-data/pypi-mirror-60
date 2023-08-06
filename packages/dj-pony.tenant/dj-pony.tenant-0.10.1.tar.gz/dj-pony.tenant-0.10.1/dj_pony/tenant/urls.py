# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from dj_pony.tenant import views

# TODO: Do I really need these? They feel like unused leftovers.
urlpatterns = [
    url(
        regex=r"^organization/$",
        view=views.TenantListView.as_view(),
        name="tenant_list",
    ),
    url(
        regex=r"^organization/details/$",
        view=views.TenantDetailsView.as_view(),
        name="tenant_details",
    ),
    url(
        regex=r"^organization-site/$",
        view=views.TenantSiteListView.as_view(),
        name="tenant_site_list",
    ),
    url(
        # regex=r'^organization-site/(?P<pk>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        regex=r"^organization-site/(?P<pk>[\d]+)/$",
        view=views.TenantSiteDetailsView.as_view(),
        name="tenant_site_details",
    ),
    url(
        regex=r"^organization-settings/(?P<pk>[\w.@+-]+)/$",
        view=views.TenantSettingsDetailsView.as_view(),
        name="tenant_settings_details",
    ),
]
