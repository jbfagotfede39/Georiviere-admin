from django.conf import settings
from django.contrib.gis.geos import Point, LineString
from django.test import TestCase

from georiviere.description.tests.factories import MorphologyFactory, StatusFactory
from georiviere.river.models import Stream
from georiviere.river.tests.factories import TopologyFactory, StreamFactory


class TopologyTest(TestCase):

    def test_str(self):
        morphology = MorphologyFactory.create()
        status = StatusFactory.create()
        lonely_topology = TopologyFactory()
        self.assertEqual(str(status.topology), "Status {}".format(status.pk))
        self.assertEqual(str(morphology.topology), "Morphology {}".format(morphology.pk))
        self.assertEqual(str(lonely_topology), "Topology {}".format(lonely_topology.pk))


class StreamSourceLocationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.stream1 = StreamFactory.create(
            geom=LineString((10000, 10000), (50000, 50000)),
        )
        cls.stream2 = StreamFactory.create(
            geom=LineString((10000, 10000), (50000, 50000)),
            source_location=Point(0, 0, srid=settings.SRID),
        )

    def test_source_location_default(self):
        """Test if source_location is set on save()"""
        self.assertAlmostEqual(self.stream1.source_location.coords, (10000, 10000))

    def test_get_map_image_extent(self):
        """Test get_map_image_extent method with source location not in bbox"""
        lng_min, lat_min, lng_max, lat_max = self.stream2.get_map_image_extent()
        self.assertAlmostEqual(lng_min, -1.363081210117898)
        self.assertAlmostEqual(lat_min, -5.9838563092087576)
        self.assertAlmostEqual(lng_max, -1.0680441780204335)
        self.assertAlmostEqual(lat_max, -5.655019875165679)


class SnapTest(TestCase):
    def test_snap_not_saved(self):
        p = Stream()
        with self.assertRaisesRegex(ValueError, "Cannot compute snap on unsaved stream"):
            p.snap(Point(0, 0))

    def test_snap_reproj(self):
        p = StreamFactory.create(geom=LineString(Point(700000, 6600000), Point(700100, 6600100), srid=settings.SRID))
        snap = p.snap(Point(3, 46.5, srid=4326))
        self.assertEqual(snap.x, 700000)
        self.assertEqual(snap.y, 6600000)
