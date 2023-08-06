from .general_assessment import GeneralAssessment


class GeneralAssessmentInitial(GeneralAssessment):
    class Meta:
        proxy = True
        verbose_name = "General Assessment (Baseline)"
        verbose_name_plural = "General Assessment (Baseline)"
