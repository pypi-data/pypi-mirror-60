from django.utils.safestring import mark_safe
from edc_constants.constants import YES, TBD, NO, UNKNOWN, POS, NEG
from edc_utils.date import get_utcnow


class SubjectScreeningEligibilityError(Exception):
    pass


class EligibilityPartOneError(Exception):
    pass


class EligibilityPartTwoError(Exception):
    pass


class EligibilityPartThreeError(Exception):
    pass


def check_eligible_final(obj):
    """Updates model instance fields `eligible` and `reasons_ineligible`.
    """
    reasons_ineligible = []

    if obj.unsuitable_for_study == YES:
        obj.eligible = False
        reasons_ineligible.append("Subject unsuitable")
    else:
        obj.eligible = True if calculate_eligible_final(obj) == YES else False

    if obj.eligible:
        obj.reasons_ineligible = None
    else:
        if obj.hiv_status == NEG:
            reasons_ineligible.append("HIV(-)")
        if obj.hiv_status == UNKNOWN:
            reasons_ineligible.append("HIV(?)")
        if obj.diabetic in [NO, UNKNOWN]:
            reasons_ineligible.append("Not Diabetic")
        if obj.hypertensive in [NO, UNKNOWN]:
            reasons_ineligible.append("Not Hypertensive")
        if obj.lives_nearby == NO:
            reasons_ineligible.append("Not in catchment area")
        if obj.requires_acute_care == YES:
            reasons_ineligible.append("Requires acute care")
        if reasons_ineligible:
            obj.reasons_ineligible = "|".join(reasons_ineligible)
        else:
            obj.reasons_ineligible = None
    obj.eligibility_datetime = get_utcnow()


def calculate_eligible_final(obj):
    """Returns YES, NO or TBD.
    """
    if (
        obj.hiv_status in [POS, NEG, UNKNOWN]
        and obj.diabetic in [YES, NO, UNKNOWN]
        and obj.hypertensive in [YES, NO, UNKNOWN]
        and obj.lives_nearby in [YES, NO]
        and obj.requires_acute_care in [YES, NO]
    ):
        eligible = (
            (obj.hiv_status == POS or obj.diabetic == YES or obj.hypertensive == YES)
            and obj.lives_nearby == YES
            and obj.requires_acute_care == NO
        )
        return NO if not eligible else YES
    return TBD


def format_reasons_ineligible(*str_values):
    reasons = None
    str_values = [x for x in str_values if x is not None]
    if str_values:
        str_values = "".join(str_values)
        reasons = mark_safe(str_values.replace("|", "<BR>"))
    return reasons


def eligibility_display_label(obj):
    if obj.eligible:
        display_label = "ELIGIBLE"
    elif calculate_eligible_final == TBD:
        display_label = "PENDING"
    else:
        display_label = "not eligible"
    return display_label
