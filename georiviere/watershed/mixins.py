from django.utils.translation import gettext_lazy as _
from .models import Watershed
from geotrek.common.utils import intersecting, uniquify


class WatershedPropertiesMixin:
    watersheds_verbose_name = _("Watersheds")

    @property
    def zoning_property(self):
        return self

    @property
    def watersheds(self):
        return uniquify(intersecting(Watershed, self.zoning_property, distance=0))
