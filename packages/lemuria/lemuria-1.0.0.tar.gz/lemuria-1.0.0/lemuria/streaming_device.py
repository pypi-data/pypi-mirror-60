import logging
import lzma
import struct
import time
import threading

from .tcp_device import TCPDevice

logger = logging.getLogger(__name__)


class StreamingDevice(TCPDevice):
    def __init__(self, file_times, start_time, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.file_times = file_times
        self.start_time = start_time

        self.streaming_started = threading.Event()
        self.streaming_stopped = threading.Event()
        self.stream_thread = threading.Thread(target=self._stream_thread_run)
        self.stream_thread.start()

        self.file_lock = threading.Lock()
        self.current_file = None
        self.next_packet_timestamp = None
        self.next_packet_bytes = None

        self._setup_streaming()

    def _start_streaming(self):
        logger.debug("Starting streaming")
        self.stream_start_time = time.monotonic()
        self.streaming_stopped.clear()
        self.streaming_started.set()

    def _stop_streaming(self):
        logger.debug("Stopping streaming")
        self.streaming_started.clear()
        self.streaming_stopped.set()
        self._setup_streaming()

    def _stream_set_enable(self, index, enable):
        if enable:
            any_running = any(self.stream_enable_status)
            if not any_running:
                # starting our first stream
                self._start_streaming()
        else:
            stopping_last = True
            for i, enabled in enumerate(self.stream_enable_status):
                if i == index:
                    if not enabled:
                        stopping_last = False
                        break
                else:
                    if enabled:
                        stopping_last = False
                        break

            if stopping_last:
                self._stop_streaming()

        super()._stream_set_enable(index, enable)

    def _setup_streaming(self):
        with self.file_lock:
            self.remaining_timestamps = sorted(self.file_times.keys())
            timestamp = self.remaining_timestamps.pop(0)
            filename = self.file_times[timestamp]

            self.next_packet_timestamp = None
            self.next_packet_bytes = None

            if self.current_file:
                self.current_file.close()
                self.current_file = None

            self._open_file(filename, timestamp)
            if self.current_file is None:
                self._open_next_file()

    def _open_file(self, filename, timestamp):
        logger.debug("Opening file %s", filename)

        lzmafile = lzma.LZMAFile(filename, "rb")

        # skip over the header (since it's already been processed)
        header_leader = struct.unpack(">dI", lzmafile.read(12))
        _header_bytes = lzmafile.read(header_leader[1])

        packet_leader = struct.Struct(">dI")

        if timestamp < self.start_time:
            while True:
                leader_bytes = lzmafile.read(packet_leader.size)
                if not leader_bytes or len(leader_bytes) != packet_leader.size:
                    logger.debug("Finished file")
                    lzmafile.close()
                    return  # file is finished

                leader = packet_leader.unpack(leader_bytes)
                packet_timestamp = leader[0]
                packet_length = leader[1]
                packet_bytes = lzmafile.read(packet_length)
                if not packet_bytes or len(packet_bytes) != packet_length:
                    logger.debug("Finished file")
                    lzmafile.close()
                    return  # file is finished

                if self.start_time < packet_timestamp:
                    # start streaming from this packet
                    self.next_packet_timestamp = packet_timestamp
                    self.next_packet_bytes = packet_bytes
                    break
        self.current_file = lzmafile

    def _open_next_file(self):
        while self.current_file is None:
            try:
                timestamp = self.remaining_timestamps.pop(0)
            except IndexError:
                # hit the end of all of the files
                return
            filename = self.file_times[timestamp]
            self._open_file(filename, timestamp)

    def _process_packets(self, timestamp):
        if self.next_packet_timestamp is not None:
            if self.next_packet_timestamp <= timestamp:
                # logger.debug("sending stashed packet %s", timestamp - self.next_packet_timestamp)
                self._send_stream_packet(self.next_packet_bytes)
                self.next_packet_timestamp = None
                self.next_packet_bytes = None
            else:
                # not time to send this yet
                # logger.debug("stash not ready %s", timestamp - self.next_packet_timestamp)
                return

        packet_leader = struct.Struct(">dI")
        while True:
            leader_bytes = self.current_file.read(packet_leader.size)
            if not leader_bytes or len(leader_bytes) != packet_leader.size:
                logger.debug("Finished file")
                self.current_file.close()
                self.current_file = None
                return  # file is finished

            leader = packet_leader.unpack(leader_bytes)
            packet_timestamp = leader[0]
            packet_length = leader[1]
            packet_bytes = self.current_file.read(packet_length)
            if not packet_bytes or len(packet_bytes) != packet_length:
                logger.debug("Finished file")
                self.current_file.close()
                self.current_file = None
                return  # file is finished

            if packet_timestamp <= timestamp:
                # logger.debug("sending packet %s", timestamp - packet_timestamp)
                self._send_stream_packet(packet_bytes)
            else:
                # not time for this packet yet
                # logger.debug("not ready %s", timestamp - packet_timestamp)
                self.next_packet_timestamp = packet_timestamp
                self.next_packet_bytes = packet_bytes
                break

    def _stream_thread_run(self):
        while not self.is_finished.is_set():
            # wait for streaming to start
            self.streaming_started.wait()

            if self.is_finished.is_set():
                # close() was called
                return

            logger.debug("Streaming beginning")

            while not self.streaming_stopped.is_set():
                now = time.monotonic()
                timestamp = self.start_time + (now - self.stream_start_time)

                with self.file_lock:
                    if self.current_file is not None:
                        self._process_packets(timestamp)
                    else:
                        self._open_next_file()
                        if self.current_file is None:
                            break

                if self.next_packet_timestamp is not None:
                    delay = self.next_packet_timestamp - timestamp
                    self.streaming_stopped.wait(delay)

            logger.debug("Streaming finished")
            self.streaming_stopped.wait()

    def close(self):
        super().close()

        # set both events to force _stream_thread_run to wake up
        self.streaming_started.set()
        self.streaming_stopped.set()

    def join(self):
        super().join()
        self.stream_thread.join()
