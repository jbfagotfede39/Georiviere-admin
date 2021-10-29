from django.conf import settings
from django.contrib.gis.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import TimeStampedModelMixin
from geotrek.zoning.mixins import ZoningPropertiesMixin

from georiviere.main.models import AddPropertyBufferMixin
from georiviere.altimetry import AltimetryMixin
from georiviere.functions import LineSubString
from georiviere.knowledge.models import Knowledge, FollowUp
from mapentity.models import MapEntityMixin
from georiviere.observations.models import Station
from georiviere.proceeding.models import Proceeding
from georiviere.studies.models import Study
from georiviere.watershed.mixins import WatershedPropertiesMixin


class TopologyMixin(object):
    structure_verbose_name = _("Structure")

    def get_topology(self, topology_type):
        start_position = self.topology.start_position
        end_position = self.topology.end_position
        topologies = self.topology.stream.topologies.filter(
            Q(start_position__lte=start_position, end_position__gte=start_position) | Q(
                start_position__lte=end_position,
                end_position__gte=end_position),
            **{f'{topology_type}__isnull': False})
        final_topologies = [getattr(topology, topology_type) for topology in topologies]
        return final_topologies


class Stream(AddPropertyBufferMixin, TimeStampedModelMixin, WatershedPropertiesMixin, ZoningPropertiesMixin,
             MapEntityMixin, AltimetryMixin, StructureRelated):
    name = models.CharField(max_length=100, default=_('Stream'), verbose_name=_("Name"))
    geom = models.LineStringField(srid=settings.SRID, spatial_index=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for model_topology in self.model_topologies:
            setattr(self, model_topology._meta.model_name, self.get_topology(model_topology._meta.model_name))

    def get_topology(self, value):
        topologies = self.topologies.filter(**{f'{value}__isnull': False})
        topologies = [getattr(topology, value) for topology in topologies]
        return topologies

    def __str__(self):
        return self.name

    @classmethod
    def get_create_label(cls):
        return _("Add a new stream")

    @property
    def name_display(self):
        return '<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk,
                                                                 self.get_detail_url(),
                                                                 self,
                                                                 self)

    class Meta:
        verbose_name = _("Stream")
        verbose_name_plural = _("Streams")


class Topology(models.Model):
    stream = models.ForeignKey(Stream, verbose_name=_("Stream"),
                               on_delete=models.CASCADE, related_name='topologies')
    start_position = models.FloatField(verbose_name=_("Start position"), db_index=True, default=0)
    end_position = models.FloatField(verbose_name=_("End position"), db_index=True, default=1)
    qualified = models.BooleanField(verbose_name=_("Qualified"), null=False, default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        geom_topology = self._meta.model.objects.filter(pk=self.pk) \
            .annotate(substring=LineSubString(self.stream.geom, self.start_position, self.end_position)).first().substring
        if hasattr(self, 'status'):
            self.status.geom = geom_topology
            self.status.save()
        elif hasattr(self, 'morphology'):
            self.morphology.geom = geom_topology
            self.morphology.save()
        super().save(force_insert=False)

    class Meta:
        verbose_name = _("Topology")
        verbose_name_plural = _("Topologies")


Study.add_property('stations', Station.within_buffer, _("Stations"))
Study.add_property('knowledges', Knowledge.within_buffer, _("Knowledge"))
Study.add_property('proceedings', Proceeding.within_buffer, _("Proceedings"))
Study.add_property('streams', Stream.within_buffer, _("Streams"))

Station.add_property('studies', Study.within_buffer, _("Studies"))
Station.add_property('knowledges', Knowledge.within_buffer, _("Knowledge"))
Station.add_property('proceedings', Proceeding.within_buffer, _("Proceedings"))
Station.add_property('streams', Stream.within_buffer, _("Streams"))

Knowledge.add_property('stations', Station.within_buffer, _("Stations"))
Knowledge.add_property('studies', Study.within_buffer, _("Studies"))
Knowledge.add_property('proceedings', Proceeding.within_buffer, _("Proceedings"))
Knowledge.add_property('streams', Stream.within_buffer, _("Streams"))

FollowUp.add_property('stations', Station.within_buffer, _("Stations"))
FollowUp.add_property('studies', Study.within_buffer, _("Studies"))
FollowUp.add_property('proceedings', Proceeding.within_buffer, _("Proceedings"))
FollowUp.add_property('streams', Stream.within_buffer, _("Streams"))

Proceeding.add_property('stations', Station.within_buffer, _("Stations"))
Proceeding.add_property('studies', Study.within_buffer, _("Studies"))
Proceeding.add_property('knowledges', Knowledge.within_buffer, _("Knowledges"))
Proceeding.add_property('streams', Stream.within_buffer, _("Streams"))

Stream.add_property('stations', Station.within_buffer, _("Stations"))
Stream.add_property('studies', Study.within_buffer, _("Studies"))
Stream.add_property('knowledges', Knowledge.within_buffer, _("Knowledges"))
Stream.add_property('proceedings', Proceeding.within_buffer, _("Proceedings"))