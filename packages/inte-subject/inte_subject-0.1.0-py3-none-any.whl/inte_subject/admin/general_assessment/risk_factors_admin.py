from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_form_label.form_label_modeladmin_mixin import FormLabelModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin


from ...admin_site import inte_subject_admin
from ...forms import RiskFactorsForm
from ...models import RiskFactors
from ..modeladmin import CrfModelAdminMixin


@admin.register(RiskFactors, site=inte_subject_admin)
class RiskFactorsAdmin(CrfModelAdminMixin, FormLabelModelAdminMixin, SimpleHistoryAdmin):

    form = RiskFactorsForm

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Smoking",
            {
                "fields": (
                    "smoker_current",
                    "smoker_last_12m",
                    "smoker_cigarettes_per_day",
                ),
            },
        ),
        (
            "Alcohol",
            {
                "fields": (
                    "alcohol",
                    "alcohol_consumption",
                    "alcohol_preference",
                ),
            },
        ),
        audit_fieldset_tuple,
    )

    radio_fields = {
        "smoker_current": admin.VERTICAL,
        "smoker_last_12m": admin.VERTICAL,
        "smoker_cigarettes_per_day": admin.VERTICAL,
        "alcohol": admin.VERTICAL,
        "alcohol_consumption": admin.VERTICAL,
        "alcohol_preference": admin.VERTICAL,
    }
