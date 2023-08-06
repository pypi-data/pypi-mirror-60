from django.contrib.gis.db.models.functions import GeoFunc, OracleToleranceMixin
from django.db.models import Aggregate, IntegerField, Func

class GType(GeoFunc):
    function = 'SDO_GEOMETRY.Get_GType'
    output_field=IntegerField()

class Rectify(GeoFunc, OracleToleranceMixin):
    function = 'SDO_UTIL.RECTIFY_GEOMETRY'

class Buffer(GeoFunc, OracleToleranceMixin):
    function = 'SDO_GEOM.SDO_BUFFER'

class ConvexHull(GeoFunc, OracleToleranceMixin):
    function = 'SDO_GEOM.SDO_CONVEXHULL'

class Simplify(GeoFunc, OracleToleranceMixin):
    function = 'SDO_UTIL.SIMPLIFY'

class SimplifyVW(GeoFunc, OracleToleranceMixin):
    function = 'SDO_UTIL.SIMPLIFYVW'
