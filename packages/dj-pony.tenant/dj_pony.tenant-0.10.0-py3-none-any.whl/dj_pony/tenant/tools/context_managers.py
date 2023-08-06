from contextlib import contextmanager

from dj_pony.tenant.helpers import set_current_tenant, clear_current_tenant
from dj_pony.tenant.constants import THREAD_LOCAL
from dj_pony.tenant.constants import BYPASS_MODE
from dj_pony.tenant.constants import NORMAL_MODE


@contextmanager
def current_tenant(tenant):
    set_current_tenant(tenant.slug)
    yield
    clear_current_tenant()


@contextmanager
def use_bypass_mode():
    THREAD_LOCAL.dj_pony_tenant_mode = BYPASS_MODE
    yield
    THREAD_LOCAL.dj_pony_tenant_mode = NORMAL_MODE
