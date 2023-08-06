from dj_pony.tenant.constants import THREAD_LOCAL
from dj_pony.tenant.settings import get_setting
from dj_pony.tenant.models import Tenant
from dj_pony.tenant.utils import import_from_string
from sentinels import NOTHING
# import contextvars


THREAD_LOCAL.current_tenant = NOTHING


TENANT_RETRIEVERS = {}
tenant_retriever_list = get_setting("TENANT_RETRIEVERS")
for tenant_retriever in tenant_retriever_list:
    TENANT_RETRIEVERS[tenant_retriever] = import_from_string(tenant_retriever)


# TODO: This function needs to be overridable.
def get_tenant(request):
    # if not hasattr(request, "_cached_tenant"):
    #     tenant_retrievers = get_setting("TENANT_RETRIEVERS")
    #     tenant_retrieved = False
    #
    #     for tenant_retriever in tenant_retrievers:
    #         tenant = import_from_string(tenant_retriever)(request)
    #         if tenant:
    #             request._cached_tenant = tenant
    #             tenant_retrieved = True
    #             break
    #
    #     if not tenant_retrieved:
    #         if not getattr(request, "_cached_tenant", False):
    #             lazy_tenant = ThreadMapTenantMiddleware.get_current_tenant()
    #             if not lazy_tenant:
    #                 return None
    #
    #             lazy_tenant._setup()
    #             request._cached_tenant = lazy_tenant._wrapped
    #
    #         elif get_setting("ADD_TENANT_TO_SESSION"):
    #             try:
    #                 request.session["tenant_slug"] = request._cached_tenant.slug
    #             except AttributeError:
    #                 pass
    #
    # return request._cached_tenant

    # if hasattr(THREAD_LOCAL, 'current_tenant'):
    #     if THREAD_LOCAL.current_tenant is not None:
    if THREAD_LOCAL.current_tenant is not NOTHING:
        if THREAD_LOCAL.current_tenant is not None:
            return THREAD_LOCAL.current_tenant
    tenant_retrievers = get_setting("TENANT_RETRIEVERS")
    for tenant_retriever in tenant_retrievers:
        # TODO: Move the import_from_string step up to the
        #  module level so its cached between function calls.
        # tenant = import_from_string(tenant_retriever)(request)
        tenant = TENANT_RETRIEVERS[tenant_retriever](request)
        if tenant:
            return tenant
    return None


def lookup_current_tenant(request):
    # THREAD_LOCAL.current_tenant = SimpleLazyObject(lambda: get_tenant(request))
    THREAD_LOCAL.current_tenant = get_tenant(request)


def get_current_tenant():
    try:
        if THREAD_LOCAL.current_tenant is not NOTHING:
            return THREAD_LOCAL.current_tenant
        else:
            return None
    # TODO Not sure this try except is still needed.
    except AttributeError:
        return None


# TODO: This should support setting the tenant using both slug and ulid.
def set_current_tenant(tenant_slug):
    # THREAD_LOCAL.current_tenant = SimpleLazyObject(
    #     lambda: Tenant.objects.filter(slug=tenant_slug).first()
    # )
    THREAD_LOCAL.current_tenant = Tenant.objects.filter(slug=tenant_slug).first()


def clear_current_tenant():
    # if hasattr(THREAD_LOCAL, 'current_tenant'):
    #     del THREAD_LOCAL.current_tenant
    THREAD_LOCAL.current_tenant = NOTHING


class ThreadLocalTenantMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request = self.process_request(request)
        response = self.get_response(request)
        return self.process_response(request, response)

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        clear_current_tenant()
        lookup_current_tenant(request)
        return request

    # noinspection PyMethodMayBeStatic
    def process_response(self, request, response):
        clear_current_tenant()
        return response

    # noinspection PyMethodMayBeStatic
    def process_exception(self, request, exception):
        clear_current_tenant()


# # TODO: Re-Integrate this so it selctable and actually useful.
# class ThreadMapTenantMiddleware(object):
#     _threadmap = {}
#
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.
#
#     @classmethod
#     def get_current_tenant(cls):
#         try:
#             return cls._threadmap[threading.get_ident()]
#         except KeyError:
#             return None
#
#     @classmethod
#     def set_tenant(cls, tenant_slug):
#         cls._threadmap[threading.get_ident()] = SimpleLazyObject(
#             lambda: Tenant.objects.filter(slug=tenant_slug).first())
#
#     @classmethod
#     def clear_tenant(cls):
#         del cls._threadmap[threading.get_ident()]
#
#     def process_request(self, request):
#         request.tenant = SimpleLazyObject(lambda: get_tenant(request))
#         self._threadmap[threading.get_ident()] = request.tenant
#
#         return request
#
#     def process_exception(self, request, exception):
#         try:
#             del self._threadmap[threading.get_ident()]
#         except KeyError:
#             pass
#
#     def process_response(self, request, response):
#         try:
#             del self._threadmap[threading.get_ident()]
#         except KeyError:
#             pass
#         return response
#
#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.
#         request = self.process_request(request)
#         response = self.get_response(request)
#         return self.process_response(request, response)
#
#
# #
#
#
# # TODO: I really need to develop tests that properly exercise this code.
# #  Thread Local vs Context Variables is complicated.
#
#
# TENANT_CONTEXT_VAR = contextvars.ContextVar("tenant_context")
# TENANT_THREAD_LOCAL = threading.local()
#
#
# class TenantMiddleware(object):
#     _use_threading = True
#     context_token = None
#
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.
#
#     @classmethod
#     def get_current_tenant(cls):
#         try:
#             if not cls._use_threading:
#                 return TENANT_CONTEXT_VAR.get()
#             else:
#                 return TENANT_THREAD_LOCAL.tenant
#         except (LookupError, AttributeError):
#             return None
#
#     @classmethod
#     def set_tenant(cls, tenant_slug):
#         if not cls._use_threading:
#             cls.context_token = TENANT_CONTEXT_VAR.set(
#                 SimpleLazyObject(
#                     lambda: Tenant.objects.filter(slug=tenant_slug).first()
#                 )
#             )
#         else:
#             TENANT_THREAD_LOCAL.tenant = SimpleLazyObject(
#                 lambda: Tenant.objects.filter(slug=tenant_slug).first()
#             )
#
#     @classmethod
#     def clear_tenant(cls):
#         if not cls._use_threading:
#             TENANT_CONTEXT_VAR.reset(cls.context_token)
#         else:
#             TENANT_THREAD_LOCAL.tenant = None
#
#     def process_request(self, request):
#         request.tenant = SimpleLazyObject(lambda: get_tenant(request))
#         if not self._use_threading:
#             self.context_token = TENANT_CONTEXT_VAR.set(request.tenant)
#         else:
#             # TODO: not sure i need to do anything for the thread local mode.
#             pass
#         return request
#
#     def process_exception(self, request, exception):
#         if not self._use_threading:
#             TENANT_CONTEXT_VAR.reset(self.context_token)
#         else:
#             TENANT_THREAD_LOCAL.tenant = None
#
#     def process_response(self, request, response):
#         if not self._use_threading:
#             TENANT_CONTEXT_VAR.reset(self.context_token)
#         else:
#             TENANT_THREAD_LOCAL.tenant = None
#         return response
#
#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.
#         request = self.process_request(request)
#         response = self.get_response(request)
#         return self.process_response(request, response)
