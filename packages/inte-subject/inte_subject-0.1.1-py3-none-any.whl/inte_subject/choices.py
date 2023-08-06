from django.utils.safestring import mark_safe
from edc_constants.constants import OTHER, NOT_APPLICABLE
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, MISSED_VISIT
from edc_reportable import (
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    MICROMOLES_PER_LITER,
    MICROMOLES_PER_LITER_DISPLAY,
)


ACTIVITY_CHOICES = (
    ("working", "Working"),
    ("studying", "Studying"),
    ("caring_for_children", "Caring for children"),
    (OTHER, "Other, please specify"),
)

CHILDCARE_CHOICES = (
    (NOT_APPLICABLE, "Not applicable"),
    ("working", "Working"),
    ("studying", "Studying"),
    ("caring_for_children", "Caring for children"),
    ("house_maintenance", "House maintenance"),
    ("nothing", "Nothing"),
    (OTHER, "Other, specify"),
)

VISIT_UNSCHEDULED_REASON = (
    ("patient_unwell_outpatient", "Patient unwell (outpatient)"),
    ("patient_hospitalised", "Patient hospitalised"),
    ("routine_non_study", "Routine appointment (non-study)"),
    ("recurrence_symptoms", "Recurrence of symptoms"),
    (OTHER, "Other"),
    (NOT_APPLICABLE, "Not applicable"),
)

VISIT_REASON = (
    (SCHEDULED, "Scheduled visit"),
    (UNSCHEDULED, "Unscheduled visit"),
    (MISSED_VISIT, "Missed visit"),
)

ALCOHOL_CONSUMPTION = (
    ("less_than_once_per_week", "less than once per week"),
    ("1-3_times_per_week", "1-3 times per week"),
    ("daily", "daily"),
)

ALCOHOL_PREFERENCES = (
    ("beer", "beer"),
    ("wine", "wine"),
    ("spirits", "spirits"),
    ("locaL_brew", "local_brew"),
)

CIGARETTES_PER_DAY = (
    ("1-10", "1-10"),
    ("11-20", "11-20"),
    ("gt-20", "more than 20"),
)

INFO_SOURCE = (
    ("hospital_notes", "Hospital notes"),
    ("outpatient_cards", "Outpatient cards"),
    ("patient", "Patient"),
    ("collateral_history", "Collateral History from relative/guardian"),
    (OTHER, "Other"),
)

PHYSICAL_ACTIVITY = (
    ("retired", "Retired"),
    ("sitting", "Mostly sitting"),
    ("standing_or_walking", "Mostly standing or walking"),
    ("physical_effort", "Definite physical effort"),
    ("vigorous_physical_activity", "Vigorous physical activity"),
)

PHYSICAL_ACTIVITY_HOURS = (
    ("none", "None"),
    ("lt_1hr", "Some but less than one hour"),
    ("1-3hr", "1 hour but less than 3 hours"),
    ("gte_3hr", "3 hours or more"),
)


GLUCOSE_UNITS = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),
)

PAYEE_CHOICES = (
    ("own_cash", "Own cash"),
    ("insurance", "Insurance"),
    ("relative", "Relative of others paying"),
    ("free", "Free drugs from the pharmacy"),
    (NOT_APPLICABLE, "Not applicable"),
)

TRANSPORT_CHOICES = (
    ("bus", "Bus"),
    ("train", "Train"),
    ("ambulance", "Ambulance"),
    ("private_taxi", "Private taxi"),
    ("own_bicycle", "Own bicycle"),
    ("hired_motorbike", "Hired motorbike"),
    ("own_car", "Own car"),
    ("own_motorbike", "Own motorbike"),
    ("hired_bicycle", "Hired bicycle"),
    ("foot", "Foot"),
    (OTHER, "Other, specify"),
)
