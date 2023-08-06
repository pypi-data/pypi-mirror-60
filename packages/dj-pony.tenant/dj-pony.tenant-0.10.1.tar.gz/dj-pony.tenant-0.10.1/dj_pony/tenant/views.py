from rest_framework import generics, views, response, status, permissions
from django.db import transaction

from dj_pony.tenant.models import Tenant, TenantSite
from dj_pony.tenant.drf.permissions import DjangoTenantModelPermissions
from dj_pony.tenant.utils import import_from_string
from dj_pony.tenant.settings import get_setting
from dj_pony.tenant.helpers import get_current_tenant


# TODO: There is a degree of repetition here that could be improved.
#  get_queryset in particular doesnt feel very DRY, possible refactoring target.


TENANT_SERIALIZER = import_from_string(get_setting("TENANT_SERIALIZER"))
TENANT_SETTINGS_SERIALIZER = import_from_string(get_setting("TENANT_SETTINGS_SERIALIZER"))
TENANT_SITE_SERIALIZER = import_from_string(get_setting("TENANT_SITE_SERIALIZER"))


class TenantListView(generics.ListCreateAPIView):
    permission_classes = [DjangoTenantModelPermissions]

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [permissions.IsAuthenticated]
        return super(TenantListView, self).get_permissions()

    def get_serializer_class(self):
        # return import_from_string(get_setting("TENANT_SERIALIZER"))
        return TENANT_SERIALIZER

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Tenant.objects.filter(
                relationships__user=self.request.user
            ).distinct()
        # TODO: I cant seem to get this branch to be covered by tests.
        else:
            return Tenant.objects.none()


class TenantDetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [DjangoTenantModelPermissions]

    def get_serializer_class(self):
        # return import_from_string(get_setting("TENANT_SERIALIZER"))
        return TENANT_SERIALIZER

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Tenant.objects.filter(
                relationships__user=self.request.user
            ).distinct()
        # TODO: I cant seem to get this branch to be covered by tests.
        else:
            return Tenant.objects.none()

    def get_object(self):
        return get_current_tenant()


class TenantSettingsDetailsView(views.APIView):
    permission_classes = [DjangoTenantModelPermissions]

    def get_serializer_class(self):
        # return import_from_string(get_setting("TENANT_SETTINGS_SERIALIZER"))
        return TENANT_SETTINGS_SERIALIZER

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Tenant.objects.filter(
                relationships__user=self.request.user
            ).distinct()
        # TODO: I cant seem to get this branch to be covered by tests.
        else:
            return Tenant.objects.none()

    def get(self, request, *args, **kwargs):
        tenant = get_current_tenant()
        serializer = self.get_serializer_class()(
            tenant, context={"request": request, "view": self}
        )
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(
            data=self.request.data, context={"request": request, "view": self}
        )

        if serializer.is_valid():
            serializer.save()
            tenant = get_current_tenant()
            return_serializer = self.get_serializer_class()(tenant)
            return response.Response(return_serializer.data, status=status.HTTP_200_OK)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantSiteListView(generics.ListCreateAPIView):
    permission_classes = [DjangoTenantModelPermissions]

    def get_serializer_class(self):
        # return import_from_string(get_setting("TENANT_SITE_SERIALIZER"))
        return TENANT_SITE_SERIALIZER

    def get_queryset(self):
        return TenantSite.objects.all()

    def get_serializer(self, *args, **kwargs):
        if self.request.method == "POST":
            data = kwargs.get("data", {})
            data["tenant"] = get_current_tenant()
            kwargs["data"] = data
        return super(TenantSiteListView, self).get_serializer(*args, **kwargs)


class TenantSiteDetailsView(generics.DestroyAPIView):
    permission_classes = [DjangoTenantModelPermissions]

    def get_serializer_class(self):
        # return import_from_string(get_setting("TENANT_SITE_SERIALIZER"))
        return TENANT_SITE_SERIALIZER

    def get_queryset(self):
        return TenantSite.objects.all()

    def destroy(self, request, *args, **kwargs):
        tenant_site = self.get_object()
        site = tenant_site.site

        with transaction.atomic():
            response = super(TenantSiteDetailsView, self).destroy(
                request, *args, **kwargs
            )
            site.delete()

        return response
