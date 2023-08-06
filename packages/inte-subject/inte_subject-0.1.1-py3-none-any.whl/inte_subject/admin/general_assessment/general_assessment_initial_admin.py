from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_form_label.form_label_modeladmin_mixin import FormLabelModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin


from ...admin_site import inte_subject_admin
from ...forms import GeneralAssessmentInitialForm
from ...models import GeneralAssessmentInitial
from ..modeladmin import CrfModelAdminMixin


@admin.register(GeneralAssessmentInitial, site=inte_subject_admin)
class GeneralAssessmentInitialAdmin(
    CrfModelAdminMixin, FormLabelModelAdminMixin, SimpleHistoryAdmin
):

    form = GeneralAssessmentInitialForm

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        ("Diagnoses at screening", {"fields": ("conditions",),},),
        ("HIV", {"fields": ("hiv_screen", "hiv_informed", "hiv_screen_date",),},),
        (
            "Diabetes",
            {
                "fields": (
                    "diabetes_screen",
                    "diabetes_informed",
                    "diabetes_screen_date",
                ),
            },
        ),
        (
            "Hypertension",
            {
                "fields": (
                    "hypertension_screen",
                    "hypertension_informed",
                    "hypertension_screen_date",
                ),
            },
        ),
        audit_fieldset_tuple,
    )

    filter_horizontal = ("conditions",)

    radio_fields = {
        "hiv_screen": admin.VERTICAL,
        "hiv_informed": admin.VERTICAL,
        "diabetes_screen": admin.VERTICAL,
        "diabetes_informed": admin.VERTICAL,
        "hypertension_screen": admin.VERTICAL,
        "hypertension_informed": admin.VERTICAL,
    }
