from dataclasses import dataclass, field
import uuid
from astropy.time import Time

@dataclass
class CmdMetaData():
    """
    CmdMetaData is a structure containing metadata regarding a command.
    It is generated by dictionary services in response to a successful command input from the user.
    This structure travels through the Uplink Pipeline, modifying the field payload_bytes at each stage.
    Once a round trip has been made and this structure returns to the (currently) Command Loader, the metadata
    is used to notify the user of the command status.
    
    :param payload_string: The input provided by the user.
    :param payload_bytes: The current form of the command, which will vary depending on the previous pipeline stage. This is represented in hexadecimal.
    :param apid: The CCSDS application process id. This is equivalent to the OPCODE of the user's command intput as defined in the dictionary.
    :param valid: Represents whether any pipeline stage has invalidated the structure. Currently functions like Maybe monad, but should function like Either.
    :param sequence: Represents the sequence number of this particular command. Usually 1 if oneshot; n<total if this structure was generated as a result of a CL script. This value is used to track the execution of a large command set.
    :param total: Represents the total number of associated commands. 1 if oneshot, or the total number of commands contained in a CL script.
    :param vcid: The VCID that should be used when generating the TCTF (currently not used).
    :param uid: This is a unique value used to associate this structure as part of a larger set, for instance as one of many results of a CL script.
    :param processors: Linked list containing the processor names that received and processed this structure.
    :param start_time_gps: Timestamp representing the local gps time that this stucture was first issued. This will be in ISO format once marhsalling has occured.
    :param finish_time_gps: Timestamp representing the local gps time that this stucture was finalized. Use the return of gps_timestamp_now() to set it. This will be in ISO format once marhsalling has occured.

    :returns: An CmdMetaData object. It is recommended to use the marshall command and work directly with that representation. 
    """
    # TODO: Use VCID here instead of letting TCTF_Manager guess
    payload_string: str = None
    payload_bytes: bytes = None
    apid: int = None
    valid: bool = False
    sequence: int = 1
    total: int = 1
    vcid: int = 0
    uid: str = None
    uplink_id: int = None
    processors: list = field(default_factory=list)
    start_time_gps = None
    finish_time_gps = None

    def __post_init__(self):
        """
        This is a post init function to automatically timestamp. 
        Provides a consistent gps timestamp object in tai scale.
        You will need to set the format attribute to 'iso' when modifying a timestamp of a marshalled object.

        Also sets UID
        """
        self.start_time_gps = self.gps_timestamp_now()
        self.uid = self.get_uid()

    def __repr__(self):
        return str(self.marshall())
    
    @staticmethod
    def get_uid():
        """
        Provide an identifier for a command group.
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def gps_timestamp_now(iso_string=True):
        t = Time(Time.now(), format='gps', scale='tai', precision=9)
        if not iso_string:
            return t
        t.format = 'iso'
        return str(t)
    
    def marshall(self):
        """
        Dictionary representing a marshalled object. 
        Every element must be serializable by msgpack.packb
        """
        res = {}
        res['data_type'] = type(self).__name__
        res['payload_string'] = self.payload_string
        res['apid'] = self.apid
        res['uid'] = self.uid
        res['payload_bytes'] = self.payload_bytes
        res['vcid'] = self.vcid
        res['sequence'] = self.sequence
        res['total'] = self.total
        res['valid'] = self.valid
        res['processors'] = self.processors
        res['start_time_gps'] = str(self.start_time_gps)
        res['finish_time_gps'] = str(self.finish_time_gps)
        res['uplink_id'] = self.uplink_id
        return res
    
    def unmarshall(self):
        # This is just metadata; We don't need to unmarshall.
        pass
# TODO: Dictionary services should be returning these.