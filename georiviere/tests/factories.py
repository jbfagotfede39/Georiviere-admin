import factory
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import LineString
from faker import Faker
from faker.providers import geo
from mapentity.tests.factories import UserFactory

fake = Faker('fr_FR')
fake.add_provider(geo)


class BaseLineStringFactory(factory.django.DjangoModelFactory):
    @factory.lazy_attribute
    def geom(self):
        origin_lat = 0
        destination_lat = 0
        middle_lat = 0
        while origin_lat == destination_lat or middle_lat == origin_lat or destination_lat == middle_lat:
            origin_lat, origin_lon, *other = fake.local_latlng(country_code='FR')
            middle_lat, middle_lon, *other = fake.local_latlng(country_code='FR')
            destination_lat, destination_lon, *other = fake.local_latlng(country_code='FR')
        linestring = LineString((float(origin_lon), float(origin_lat)),
                                (float(middle_lon), float(middle_lat)),
                                (float(destination_lon), float(destination_lat)), srid=4326)
        linestring.transform(2154)
        return linestring


class UserAllPermsFactory(UserFactory):
    is_staff = True

    @factory.post_generation
    def create_path_manager(obj, create, extracted, **kwargs):
        perms = Permission.objects.all()
        obj.user_permissions.set(perms)
