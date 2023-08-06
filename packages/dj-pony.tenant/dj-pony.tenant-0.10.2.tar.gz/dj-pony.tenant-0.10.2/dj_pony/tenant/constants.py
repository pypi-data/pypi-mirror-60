from sentinels import Sentinel
import threading


# TODO: Decide if these will be the final names... doesnt feel right yet...
#  These feel like they require documentation rather than being self explanatory.
NORMAL_MODE = Sentinel('Normal Mode')
BYPASS_MODE = Sentinel('Bypass Mode')


THREAD_LOCAL = threading.local()
THREAD_LOCAL.dj_pony_tenant_mode = NORMAL_MODE
