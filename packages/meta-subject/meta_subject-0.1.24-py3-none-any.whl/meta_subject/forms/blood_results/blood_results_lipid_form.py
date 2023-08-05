from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_visit_tracking.modelform_mixins import SubjectModelFormMixin
from meta_form_validators.form_validators import BloodResultsLipidFormValidator

from ...models import BloodResultsLipid


class BloodResultsLipidForm(
    ActionItemFormMixin, SubjectModelFormMixin, forms.ModelForm
):

    form_validator_cls = BloodResultsLipidFormValidator

    class Meta:
        model = BloodResultsLipid
        fields = "__all__"
