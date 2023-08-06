# This holds all validators before saving an instance
import json
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError


def point_check(value):
    try:
        list_value = json.loads(value)
        if isinstance(list_value, list):
            if not len(list_value)==2:
                raise ValidationError(_('The list object should have two element separated by a comma'))
            for element in list_value:
                if not isinstance(element, float) and not isinstance(element, int):
                    raise ValidationError(_('Each element in the list should be of either float or int type'))
    except json.JSONDecodeError:
        raise ValidationError(_("Check to see if the value is JSON serializable. Make sure you have a list of numeric types"))