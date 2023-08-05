import binascii
import datetime
import json
import lzma
import struct

import asphodel


def decode_header(header_bytes):
    try:
        header_str = header_bytes.decode("UTF-8")
        header = json.loads(header_str)
    except:
        raise Exception("Could not parse file header!")

    # convert the JSON info back into an actual Asphodel structure
    all_streams = [asphodel.AsphodelStreamInfo.from_json_obj(s)
                   for s in header['streams']]
    all_channels = [asphodel.AsphodelChannelInfo.from_json_obj(c)
                    for c in header['channels']]

    header['streams'] = all_streams
    header['channels'] = all_channels

    # stream rate info
    stream_rate_info = []
    for values in header.get('stream_rate_info', []):
        # fix floats getting converted to strings in older files
        values = [float(v) if isinstance(v, str) else v for v in values]

        if values is not None:
            stream_rate_info.append(asphodel.StreamRateInfo(*values))
        else:
            stream_rate_info.append(None)
    header['stream_rate_info'] = stream_rate_info

    # supplies
    supplies = []
    for name, values in header.get('supplies', []):
        # fix floats getting converted to strings in older files
        values = [float(v) if isinstance(v, str) else v for v in values]

        supplies.append((name, asphodel.SupplyInfo(*values)))
    header['supplies'] = supplies

    # control variables
    ctrl_vars = []
    for name, values, setting in header.get('ctrl_vars', []):
        # fix floats getting converted to strings in older files
        values = [float(v) if isinstance(v, str) else v for v in values]

        ctrl_vars.append((name, asphodel.CtrlVarInfo(*values), setting))
    header['ctrl_vars'] = ctrl_vars

    # nvm
    header['nvm'] = binascii.a2b_hex(header['nvm'])

    return header


def load_batch(files):
    """
    returns (file_times, header) where file_times is a dictonary of
    timestamp:filename
    * header is the dictionary loaded from the file's JSON data, with
      appropriate conversions applied to Asphodel struct data.
    * filename is the absolute path to the file location.
    * timestamp is the floating point time of the first packet in the file
    """

    first_file = True

    file_times = {}

    for filename in files:
        with lzma.LZMAFile(filename, "rb") as f:
            # read the header
            header_leader = struct.unpack(">dI", f.read(12))
            header_timestamp = header_leader[0]
            header_bytes = f.read(header_leader[1])

            if len(header_bytes) == 0:
                raise Exception("Empty header in {}!".format(filename))

            # read the first packet's datetime
            first_packet_timestamp = struct.unpack(">d", f.read(8))[0]

            if first_file:
                first_file = False
                first_header_bytes = header_bytes
                first_header_timestamp = header_timestamp

                header = decode_header(header_bytes)
                if not header:
                    return  # error message already displayed
            else:
                if (first_header_bytes != header_bytes or
                        first_header_timestamp != header_timestamp):
                    # error
                    raise Exception(
                        "Headers do not match on {}!".format(filename))

            if first_packet_timestamp in file_times:
                f2 = file_times[first_packet_timestamp]
                m = f"Timestamps overlap between files {filename} and {f2}"
                raise Exception(m)

            file_times[first_packet_timestamp] = filename

    return (file_times, header)
