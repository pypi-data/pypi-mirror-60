from shapely.geometry import Point, Polygon
from datetime import datetime

class Restrictions:
    def __init__(self, boundary_polygon, permission_expiry_time, max_alt=-1):
        self.boundary = Polygon(boundary_polygon)
        self.permission_expiry_time = permission_expiry_time
        self.max_alt = max_alt
    
    def isWithinBoundary(self, lat, lon):
        p = Point(lat, lon)
        if p.within(self.boundary):
            return True
        else:
            return False
    
    def isWithinTimelimit(self):
        if datetime.now().timestamp() <= self.permission_expiry_time:
            return True
        else:
            return False
    
    def isWithinMaxAltitude(self, alt):
        if alt <= self.max_alt:
            return True
        else:
            return False

    