import binascii
import argparse
import logging
import time

import lemuria.parser
import lemuria.streaming_device
import lemuria.udp_listener

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("files", type=argparse.FileType("rb"), nargs='+',
                        metavar='file')
    parser.add_argument(
        "-o", "--offset", type=float, metavar='time', dest="offset",
        help="offset in seconds from start of first file")
    parser.add_argument(
        "-s", "--serial", metavar='sn', dest="serial",
        help="serial number of virtual device")
    args = parser.parse_args()

    file_times, header = lemuria.parser.load_batch(f.name for f in args.files)

    offset = args.offset
    if offset is None:
        offset = 0.0
    start_time = min(file_times.keys()) + offset

    serial_number = args.serial
    if serial_number is None:
        serial_number = header['serial_number']

    device_args = {
        "serial_number": serial_number.encode("UTF-8"),
        "max_incoming_param_len": header['max_outgoing_param_length'],
        "max_outgoing_param_len": header['max_incoming_param_length'],
        "stream_packet_size": header['stream_packet_length'],
        "board_info": (header["board_info"][0].encode("UTF-8"),
                       header["board_info"][1]),
        "build_info": header["build_info"].encode("UTF-8"),
        "build_date": header["build_date"].encode("UTF-8"),
        "chip_family": header["chip_family"].encode("UTF-8"),
        "chip_model": header["chip_model"].encode("UTF-8"),
        "chip_id": binascii.a2b_hex(header['chip_id']),
        "nvm": bytearray(header['nvm']),
        "tag_locations": header['tag_locations'],
        "rgb_values": [],
        "led_values": [],
        "stream_filler_bits": header['stream_filler_bits'],
        "stream_id_bits": header['stream_id_bits'],
        "streams": header['streams'],
        "channels": header['channels'],
        "supplies": [],
        "ctrl_vars": [],
        "settings": [],
        "custom_enums": [],
        "setting_categories": [],
    }
    device = lemuria.streaming_device.StreamingDevice(
        file_times, start_time, **device_args)

    udp_listener = lemuria.udp_listener.UDPListener()
    udp_listener.add_device(device)

    try:
        while True:
            time.sleep(1)
    finally:
        udp_listener.close()
        device.close()
        udp_listener.join()
        device.join()


if __name__ == '__main__':
    main()
