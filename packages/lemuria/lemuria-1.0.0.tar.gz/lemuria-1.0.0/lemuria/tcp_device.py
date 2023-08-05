import logging
import queue
import selectors
import socket
import struct
import threading

from .device import Device

logger = logging.getLogger(__name__)


ASPHODEL_TCP_VERSION = 1
ASPHODEL_TCP_MSG_TYPE_DEVICE_CMD = 0x00
ASPHODEL_TCP_MSG_TYPE_DEVICE_STREAM = 0x01
ASPHODEL_TCP_MSG_TYPE_REMOTE_CMD = 0x02
ASPHODEL_TCP_MSG_TYPE_REMOTE_STREAM = 0x03
ASPHODEL_TCP_MSG_TYPE_REMOTE_NOTIFY = 0x06


class TCPDevice(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connected = False
        self.connected_sock = None

        # create a TCP socket
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                                         socket.IPPROTO_TCP)
        self.listen_sock.setblocking(False)
        self.listen_sock.bind(("", 0))
        self.listen_sock.listen(1)

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.listen_sock, selectors.EVENT_READ,
                               self._accept_ready)

        # create a UDP socket
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                      socket.IPPROTO_UDP)

        # bind the UDP socket so outgoing packets have the TCP port as the src
        self.udp_sock.bind(self.listen_sock.getsockname())

        self.is_finished = threading.Event()
        self.read_buffer = bytearray()
        self.read_thread = threading.Thread(target=self._read_thread_run)
        self.write_thread = threading.Thread(target=self._write_thread_run)
        self.write_queue = queue.Queue()

        self.read_thread.start()
        self.write_thread.start()

    def __del__(self):
        self.close()
        self.join()

    def _read_user_tag(self, index, length):
        b = bytes(self.nvm[index:index + length])
        b = b.split(b'\x00', 1)[0]
        b = b.split(b'\xff', 1)[0]
        return b + b'\x00'

    def _create_advertisement(self):
        prefix = struct.pack(
            ">BBHHHB", ASPHODEL_TCP_VERSION, self.connected,
            self.max_outgoing_param_len + 2, self.max_incoming_param_len + 2,
            self.stream_packet_size, self.protocol_type)

        serial = self.serial_number + b'\x00'
        board_rev = bytes((self.board_info[1],))
        board_name = self.board_info[0] + b'\x00'
        build_info = self.build_info + b'\x00'
        build_date = self.build_date + b'\x00'

        tag1 = self._read_user_tag(*self.tag_locations[0])
        tag2 = self._read_user_tag(*self.tag_locations[1])

        packet = b''.join((prefix, serial, board_rev, board_name, build_info,
                           build_date, tag1, tag2))
        return packet

    def send_advertisement(self, address):
        packet = self._create_advertisement()

        # send the advertisement
        try:
            self.udp_sock.sendto(packet, address)
        except OSError:
            pass

    def _send_stream_packet(self, packet_bytes):
        prefix = struct.pack(">HB", len(packet_bytes) + 1,
                             ASPHODEL_TCP_MSG_TYPE_DEVICE_STREAM)
        self.write_queue.put(prefix + packet_bytes)

    def _process_buffer(self, buffer):
        if len(buffer) == 0:
            return

        if buffer[0] == ASPHODEL_TCP_MSG_TYPE_DEVICE_CMD:
            reply = self.handle_command(buffer[1:])
            if reply:
                reply_prefix = struct.pack(">HB", len(reply) + 1,
                                           ASPHODEL_TCP_MSG_TYPE_DEVICE_CMD)
                self.write_queue.put(reply_prefix + reply)
        else:
            raise Exception("Unknown message type")

    def _handle_data(self, data):
        self.read_buffer.extend(data)
        while len(self.read_buffer) >= 2:
            length = struct.unpack_from(">H", self.read_buffer, 0)[0]
            if length + 2 <= len(self.read_buffer):
                # have a full buffer
                buffer = bytes(self.read_buffer[2:2 + length])
                self._process_buffer(buffer)
                del self.read_buffer[0:2 + length]
            else:
                break

    def _accept_ready(self):
        try:
            conn, _addr = self.listen_sock.accept()  # Should be ready
            if self.connected:
                conn.close()
                logger.info("Rejected new connection attempt")
                return

            logger.info("Accepted new connection")

            self.connected = True
            self.connected_sock = conn
            self.connected_sock.setsockopt(
                socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

            self.selector.register(
                self.connected_sock, selectors.EVENT_READ, self._read_ready)
        except OSError:
            pass
        except:
            logger.exception("Unhandled exception in _accept_ready()")

    def _close_connected_socket(self):
        self.selector.unregister(self.connected_sock)
        self.connected_sock.close()
        self.connected_sock = None
        self.connected = False
        logger.info("Connection closed")

        # empty queue
        while True:
            try:
                self.write_queue.get(False)
            except queue.Empty:
                break

        # reset the device state
        self._flush()

    def _read_ready(self):
        try:
            data = self.connected_sock.recv(16384)
            if data:
                self._handle_data(data)
            else:
                # socket closed
                self._close_connected_socket()
        except OSError:
            self._close_connected_socket()
        except:
            logger.exception("Unhandled exception in _read_ready()")
            self._close_connected_socket()

    def _read_thread_run(self):
        while not self.is_finished.is_set():
            events = self.selector.select()
            for key, _mask in events:
                callback = key.data
                callback()

    def _write_thread_run(self):
        while not self.is_finished.is_set():
            try:
                data = self.write_queue.get(True, 0.1)
                if self.connected_sock:
                    self.connected_sock.send(data)
            except queue.Empty:
                pass
            except OSError:
                pass

    def close(self):
        self.is_finished.set()

        self.listen_sock.close()
        self.udp_sock.close()
        if self.connected_sock:
            self.connected_sock.close()

    def join(self):
        self.read_thread.join()
        self.write_thread.join()
