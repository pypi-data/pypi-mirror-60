from django.test import TestCase, tag
from edc_constants.constants import (
    YES,
    NO,
    RANDOM_SAMPLING,
    MALE,
    NOT_APPLICABLE,
)
from edc_utils.date import get_utcnow

from ..forms import SubjectScreeningForm
from ..models import SubjectScreening


class TestForms(TestCase):
    def get_data(self):
        return {
            "screening_consent": YES,
            "selection_method": RANDOM_SAMPLING,
            "report_datetime": get_utcnow(),
            "initials": "EW",
            "gender": MALE,
            "age_in_years": 25,
            "hospital_identifier": "13343322",
            "hiv_pos": YES,
            "diabetic": YES,
            "hypertensive": YES,
            "lives_nearby": YES,
            "staying_nearby": YES,
            "requires_acute_care": NO,
            "unsuitable_for_study": NO,
            "unsuitable_agreed": NOT_APPLICABLE,
        }

    def test_screening_ok(self):

        form = SubjectScreeningForm(data=self.get_data(), instance=None)
        form.is_valid()
        self.assertEqual(form._errors, {})
        form.save()

        self.assertTrue(SubjectScreening.objects.all()[0].eligible)

    def test_screening_ineligible(self):

        data = self.get_data()
        data.update(
            {"hiv_pos": NO, "diabetic": NO, "hypertensive": NO,}
        )

        form = SubjectScreeningForm(data=data, instance=None)
        form.is_valid()
        self.assertEqual(form._errors, {})
        form.save()

        self.assertFalse(SubjectScreening.objects.all()[0].eligible)
