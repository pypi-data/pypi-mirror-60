from django.db import models
from edc_constants.choices import YES_NO
from edc_model.models import BaseUuidModel

from ...choices import (
    CIGARETTES_PER_DAY, ALCOHOL_CONSUMPTION, ALCOHOL_PREFERENCES,
)
from ..crf_model_mixin import CrfModelMixin


class RiskFactors(CrfModelMixin, BaseUuidModel):

    smoker_current = models.CharField(
        verbose_name="Does the patient smoke currently?",
        max_length=15,
        choices=YES_NO,
    )

    smoker_last_12m = models.CharField(
        verbose_name="If no, did the patient smoke in the past 12 months?",
        max_length=15,
        choices=YES_NO,
    )

    smoker_cigarettes_per_day = models.CharField(
        verbose_name="If currently smoking, how many sticks of cigarette in a day?",
        max_length=25,
        choices=CIGARETTES_PER_DAY,
    )

    alcohol = models.CharField(
        verbose_name="Does the patient drink alcohol?",
        max_length=15,
        choices=YES_NO,
    )

    alcohol_consumption = models.CharField(
        verbose_name="If yes, how often does the patient take alcohol?",
        max_length=25,
        choices=ALCOHOL_CONSUMPTION,
    )

    alcohol_preference = models.CharField(
        verbose_name="Does the patient drink alcohol?",
        max_length=25,
        choices=ALCOHOL_PREFERENCES,
    )

    class Meta(CrfModelMixin.Meta):
        verbose_name = "Alcohol and Smoking"
        verbose_name_plural = "Alcohol and Smoking"
