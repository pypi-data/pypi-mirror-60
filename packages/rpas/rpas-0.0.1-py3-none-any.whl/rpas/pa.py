from random import random

from .lib import PermissionArtefact_pb2

class RPASPermission:
    def request_permission(self, pa={}):
        ua = PermissionArtefact_pb2.UAPermission()
        ua.permissionartefactId = pa.get('id', '0f1a040e0279496384be28c5d7e7c59d')

        boundary = pa.get('boundary', [])
        self.add_boundary(boundary, ua)

        return ua
    
    def add_boundary(self, b, ua):
        if len(b) != 0:
            for item in b:
                c = ua.flightDetails.flightParameters.coordinates.add()
                c.latitude = item[0]
                c.longitude = item[1]
        else:
            for i in range(10):
                c = ua.flightDetails.flightParameters.coordinates.add()
                c.latitude = 12. + random()
                c.longitude = 77. + random()
        

