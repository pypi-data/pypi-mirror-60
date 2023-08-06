from datetime import datetime
from google.protobuf.json_format import MessageToJson

from .lib import FlightLog_pb2
from .lib import PermissionArtefact_pb2
from .restrictions import Restrictions 
from . import proto_xml

class FlightLog:
    class Type:
        UNKNOWN = FlightLog_pb2.FlightLog.UNKNOWN
        TAKEOFF_ARM = FlightLog_pb2.FlightLog.TAKEOFF_ARM
        GEOFENCE_BREACH = FlightLog_pb2.FlightLog.GEOFENCE_BREACH
        TIME_BREACH = FlightLog_pb2.FlightLog.TIME_BREACH
        LAND_DISARM = FlightLog_pb2.FlightLog.LAND_DISARM

    class State:
        Takeoff = 0
        Midair = 1
        Land = 2
    
    def __init__(self, permission_artefact, previous_log_hash=b''):
        if(not isinstance(permission_artefact, PermissionArtefact_pb2.UAPermission)):
            raise Exception('pass a permission artefact object')

        self.pa = permission_artefact

        boundary_poly = []
        for c in self.pa.flightDetails.flightParameters.coordinates:
            boundary_poly.append((c.latitude, c.longitude))
        
        self.restrictions = Restrictions(boundary_poly, self.pa.flightDetails.flightParameters.flightEndTime, -1)
        
        self.log = FlightLog_pb2.Log()
        self.log.flightLog.permissionArtefact = self.pa.permissionartefactId
        self.log.flightLog.previousLogHash = previous_log_hash

    def update_current_position(self, lat, lon, alt, state=1):
        if state == FlightLog.State.Midair:
            if not self.restrictions.isWithinBoundary(lat, lon):
                self.add_log_entry(FlightLog.Type.GEOFENCE_BREACH, lat, lon, alt)
            if not self.restrictions.isWithinTimelimit():
                self.add_log_entry(FlightLog.Type.TIME_BREACH, lat, lon, alt)
        elif state == FlightLog.State.Takeoff:
            self.add_log_entry(FlightLog.Type.TAKEOFF_ARM, lat, lon, alt)
        elif state == FlightLog.State.Land:
            self.add_log_entry(FlightLog.Type.LAND_DISARM, lat, lon, alt)

    def add_log_entry(self, entry_type, lat, lon, alt):
        entry = self.log.flightLog.logEntries.add()

        entry.entryType = entry_type
        entry.latitude = lat
        entry.longitude = lon
        entry.altitude = alt
        entry.timestamp = int(datetime.now().timestamp())
    
    def get_json_string(self):
        return MessageToJson(self.log)

    def __str__(self):
        #print(proto_xml.MessageToXml(self.log))
        #print(self.log.flightLog.SerializeToString())
        return str(self.log)