from dj_pony.tenant.settings import get_setting

from dj_pony.tenant.helpers import TenantJSONFieldHelper


class TenantExtraDataHelper(TenantJSONFieldHelper):
    def __init__(self, instance=None):
        super(TenantExtraDataHelper, self).__init__(
            instance_field_name="extra_data",
            instance=instance,
            tenant_fields=get_setting("DEFAULT_TENANT_EXTRA_DATA_FIELDS"),
            tenant_default_fields_values=get_setting("DEFAULT_TENANT_EXTRA_DATA"),
        )
