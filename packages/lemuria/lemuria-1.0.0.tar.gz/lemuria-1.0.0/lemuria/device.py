import struct

from .protocol import *


class DeviceError(Exception):
    def __init__(self, error_code):
        self.error_code = error_code


class Device:
    def __init__(self, serial_number, max_incoming_param_len,
                 max_outgoing_param_len, stream_packet_size, board_info,
                 build_info, build_date, chip_family, chip_model, chip_id, nvm,
                 tag_locations, rgb_values, led_values, stream_filler_bits,
                 stream_id_bits, streams, channels, supplies, ctrl_vars,
                 settings, custom_enums, setting_categories):
        # NOTE: serial_number, max_incoming_param_len and stream_packet_size
        # aren't used inside the class but are needed externally
        self.serial_number = serial_number  # UTF-8 encoded bytes
        self.max_incoming_param_len = max_incoming_param_len
        self.max_outgoing_param_len = max_outgoing_param_len
        self.stream_packet_size = stream_packet_size

        self.protocol_type = ASPHODEL_PROTOCOL_TYPE_BASIC  # only basic support

        self.board_info = board_info  # (UTF-8 encoded bytes, revision)
        self.build_info = build_info  # UTF-8 encoded bytes
        self.build_date = build_date  # UTF-8 encoded bytes
        self.chip_family = chip_family  # UTF-8 encoded bytes
        self.chip_model = chip_model  # UTF-8 encoded bytes
        self.chip_id = chip_id  # UTF-8 encoded bytes

        self.nvm = nvm  # byte array

        # ((ut1_index, ut1_len), (ut2_index, ut2_len), (gs_index, gs_len))
        self.tag_locations = tag_locations

        self.rgb_values = rgb_values  # list of (R, G, B) values
        self.led_values = led_values  # list of values
        self.stream_filler_bits = stream_filler_bits  # 8-bit value
        self.stream_id_bits = stream_id_bits  # 8-bit value
        self.streams = streams  # list of AsphodelStreamInfo
        self.channels = channels  # list of AsphodelChannelInfo
        self.supplies = supplies  # TODO: list of ?
        self.ctrl_vars = ctrl_vars  # list of ?
        self.settings = settings  # list of AsphodelSettingInfo
        self.custom_enums = custom_enums  # TODO: list of [names]

        # list of (name, [setting_indexes]), name is UTF-8 encoded
        self.setting_categories = setting_categories

        # states
        self.initial_rgb_values = self.rgb_values.copy()
        self.initial_led_values = self.led_values.copy()
        self.stream_enable_status = [False] * len(self.streams)
        self.stream_warmup_status = [False] * len(self.streams)

    def _update_rgb(self, index, new_value, instant):
        self.rgb_values[index] = tuple(new_value)

    def _update_led(self, index, new_value, instant):
        self.led_values[index] = new_value

    def _stream_set_enable(self, index, enable):
        self.stream_enable_status[index] = enable

    def _stream_set_warm_up(self, index, enable):
        self.stream_warmup_status[index] = enable

    def _channel_specific(self, index, cmd, params):
        raise DeviceError(ERROR_CODE_UNIMPLEMENTED_COMMAND)

    def _flush(self):
        for i in range(len(self.streams)):
            self._stream_set_enable(i, False)
            self._stream_set_warm_up(i, False)
        for i, value in enumerate(self.initial_rgb_values):
            self._update_rgb(i, value, True)
        for i, value in enumerate(self.initial_led_values):
            self._update_led(i, value, True)
        # TODO: cancel supply measurements
        # TODO: reset ctrl vars
        # TODO: packet queue empty

    def _handle_command_internal(self, cmd, params):
        if cmd == CMD_GET_PROTOCOL_VERSION:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((ASPHODEL_PROTOCOL_VERSION_MAJOR,
                          (ASPHODEL_PROTOCOL_VERSION_MINOR << 4) |
                          ASPHODEL_PROTOCOL_VERSION_SUBMINOR))
        elif cmd == CMD_GET_BOARD_INFO:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((self.board_info[1],)) + self.board_info[0]
        elif cmd == CMD_GET_USER_TAG_LOCATIONS:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            flat = (i // 4 for t in self.tag_locations for i in t)
            return struct.pack(">6H", *flat)
        elif cmd == CMD_GET_BUILD_INFO:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return self.build_info
        elif cmd == CMD_GET_BUILD_DATE:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return self.build_date
        elif cmd == CMD_GET_CHIP_FAMILY:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return self.chip_family
        elif cmd == CMD_GET_CHIP_MODEL:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return self.chip_model
        elif cmd == CMD_GET_CHIP_ID:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return self.chip_id
        elif cmd == CMD_GET_NVM_SIZE:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return struct.pack(">H", len(self.nvm) // 4)
        elif cmd == CMD_ERASE_NVM:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            self.nvm = bytearray(b'\xff' * len(self.nvm))
        elif cmd == CMD_WRITE_NVM:
            if len(params) < 6 or len(params) % 4 != 2:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            byte_address = struct.unpack(">H", params[0:2])[0] * 4
            if byte_address + len(params) - 2 > len(self.nvm):
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)

            self.nvm[byte_address:byte_address + len(params) - 2] = params[2:]
        elif cmd == CMD_READ_NVM:
            if len(params) != 2:
                raise DeviceError(ERROR_CODE_BAD_ADDRESS)
            byte_address = struct.unpack(">H", params)[0] * 4
            if byte_address >= len(self.nvm):
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)

            # round down to multiple of 4
            bytes_to_read = (self.max_outgoing_param_len // 4) * 4

            return bytes(self.nvm[byte_address:byte_address + bytes_to_read])
        elif cmd == CMD_FLUSH:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            self._flush()
        elif cmd == CMD_GET_BOOTLOADER_INFO:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return b''  # bootloader not supported
        elif cmd == CMD_GET_RGB_COUNT:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.rgb_values),))
        elif cmd == CMD_GET_RGB_VALUES:
            if len(params) != 1:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            return bytes(self.rgb_values[index])
        elif cmd == CMD_SET_RGB:
            if len(params) != 4:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            self._update_rgb(params[0], params[1:], False)
        elif cmd == CMD_SET_RGB_INSTANT:
            if len(params) != 4:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            self._update_rgb(params[0], params[1:], True)
        elif cmd == CMD_GET_LED_COUNT:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.led_values),))
        elif cmd == CMD_GET_LED_VALUE:
            if len(params) != 1:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            return bytes((self.led_values[index],))
        elif cmd == CMD_SET_LED:
            if len(params) != 2:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            self._update_led(params[0], params[1], False)
        elif cmd == CMD_SET_LED_INSTANT:
            if len(params) != 2:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            self._update_led(params[0], params[1], True)
        elif cmd == CMD_GET_STREAM_COUNT_AND_ID:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.streams), self.stream_filler_bits,
                          self.stream_id_bits))
        elif cmd == CMD_GET_STREAM_CHANNELS:
            if len(params) != 1:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            stream = self.streams[params[0]]
            channels = stream.channel_index_list[:stream.channel_count]
            return bytes(channels)
        elif cmd == CMD_GET_STREAM_FORMAT:
            if len(params) != 1:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            stream = self.streams[params[0]]
            return struct.pack(
                ">BBfff", stream.filler_bits, stream.counter_bits, stream.rate,
                stream.rate_error, stream.warm_up_delay)
        elif cmd == CMD_ENABLE_STREAM:
            if len(params) != 2:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            self._stream_set_enable(params[0], bool(params[1]))
        elif cmd == CMD_WARM_UP_STREAM:
            if len(params) != 2:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            self._stream_set_warm_up(params[0], bool(params[1]))
        elif cmd == CMD_GET_STREAM_STATUS:
            if len(params) != 1:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return self.stream_enable_status[params[0]]
        elif cmd == CMD_GET_STREAM_RATE_INFO:
            # TODO: implement this!
            raise DeviceError(ERROR_CODE_UNIMPLEMENTED_COMMAND)
        elif cmd == CMD_GET_CHANNEL_COUNT:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.channels),))
        elif cmd == CMD_GET_CHANNEL_NAME:
            if len(params) != 1:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            channel = self.channels[params[0]]
            return channel.name
        elif cmd == CMD_GET_CHANNEL_INFO:
            if len(params) != 1:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            channel = self.channels[params[0]]
            return struct.pack(
                ">BBHHBhfffB", channel.channel_type, channel.unit_type,
                channel.filler_bits, channel.data_bits, channel.samples,
                channel.bits_per_sample, channel.minimum, channel.maximum,
                channel.resolution, channel.chunk_count)
        elif cmd == CMD_GET_CHANNEL_COEFFICIENTS:
            if len(params) not in (1, 2):
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            channel = self.channels[params[0]]
            if len(params) == 2:
                start_index = params[1]
            else:
                start_index = 0
            if start_index >= channel.coefficients_length:
                raise DeviceError(ERROR_CODE_BAD_INDEX)
            length = channel.coefficients_length - start_index
            max_send = self.max_outgoing_param_len // 4
            if length > max_send:
                length = max_send
            c = channel.coefficients[start_index:start_index + length]
            return struct.pack(">{}f".format(length), *c)
        elif cmd == CMD_GET_CHANNEL_CHUNK:
            if len(params) != 2:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            channel = self.channels[params[0]]
            chunk_number = params[1]
            if chunk_number >= channel.chunk_count:
                raise DeviceError(ERROR_CODE_BAD_INDEX)
            chunk_length = channel.chunk_lengths[chunk_number]
            chunk = channel.chunks[chunk_number][:chunk_length]
            return bytes(chunk)
        elif cmd == CMD_CHANNEL_SPECIFIC:
            if len(params) < 2:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            channel_cmd = params[1]
            if index >= len(self.channels):
                raise DeviceError(ERROR_CODE_BAD_INDEX)
            return self._channel_specific(index, channel_cmd, params[2:])
        elif cmd == CMD_GET_SUPPLY_COUNT:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.supplies),))
        elif cmd == CMD_GET_SUPPLY_NAME:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_GET_SUPPLY_INFO:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_CHECK_SUPPLY:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_GET_CTRL_VAR_COUNT:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.ctrl_vars),))
        elif cmd == CMD_GET_CTRL_VAR_NAME:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_GET_CTRL_VAR_INFO:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_GET_CTRL_VAR:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_SET_CTRL_VAR:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_GET_SETTING_COUNT:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.settings),))
        elif cmd == CMD_GET_SETTING_NAME:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_GET_SETTING_INFO:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_GET_SETTING_DEFAULT:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # TODO: implement this
        elif cmd == CMD_GET_CUSTOM_ENUM_COUNTS:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes(len(x) for x in self.custom_enums)
        elif cmd == CMD_GET_CUSTOM_ENUM_VALUE_NAME:
            if len(params) != 2:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            enum_index = params[0]
            enum_value = params[1]
            return self.custom_enums[enum_index][enum_value]
        elif cmd == CMD_GET_SETTING_CATEGORY_COUNT:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return bytes((len(self.setting_categories),))
        elif cmd == CMD_GET_SETTING_CATEGORY_NAME:
            if len(params) != 1:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            return self.setting_categories[index][0]
        elif cmd == CMD_GET_SETTING_CATERORY_SETTINGS:
            if len(params) != 1:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            index = params[0]
            return bytes(self.setting_categories[index][1])
        elif cmd == CMD_GET_GPIO_PORT_COUNT:
            if len(params) != 0:
                raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
            return b'\x00'  # not supported
        elif cmd == CMD_GET_GPIO_PORT_NAME:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_GET_GPIO_PORT_INFO:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_GET_GPIO_PORT_VALUES:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_SET_GPIO_PORT_MODES:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_DISABLE_GPIO_PORT_OVERRIDES:
            pass  # not supported
        elif cmd == CMD_GET_BUS_COUNTS:
            return b'\x00\x00'  # not supported
        elif cmd == CMD_SET_SPI_CS_MODE:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_DO_SPI_TRANSFER:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_DO_I2C_WRITE:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_DO_I2C_READ:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_DO_I2C_WRITE_READ:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_GET_INFO_REGION_COUNT:
            return b'\x00'  # not supported
        elif cmd == CMD_GET_INFO_REGION_NAME:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_GET_INFO_REGION:
            raise DeviceError(ERROR_CODE_BAD_INDEX)  # not supported
        elif cmd == CMD_GET_STACK_INFO:
            return struct.pack(">2I", 0, 0)  # not supported
        else:
            raise DeviceError(ERROR_CODE_UNIMPLEMENTED_COMMAND)

        # everything is fine
        return b""

    def handle_command(self, rx_buf):
        if len(rx_buf) == 0:
            # nothing to do
            return b''

        if len(rx_buf) == 1:
            # malformed packet
            return bytes((rx_buf[0], CMD_REPLY_ERROR,
                          ERROR_CODE_MALFORMED_COMMAND, CMD_REPLY_ERROR))

        try:
            cmd = rx_buf[1]
            params = rx_buf[2:]

            # check for the ECHO commands here, as they can't be handled in the
            # normal manner
            if cmd == CMD_ECHO_RAW:
                if len(params) > self.max_outgoing_param_len + 2:
                    raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
                return params
            elif cmd == CMD_ECHO_TRANSACTION:
                if len(params) > self.max_outgoing_param_len + 1:
                    raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
                return rx_buf[0:1] + params
            elif cmd == CMD_ECHO_PARAMS:
                if len(params) > self.max_outgoing_param_len:
                    raise DeviceError(ERROR_CODE_BAD_CMD_LENGTH)
                return rx_buf[0:2] + params
            else:
                cmd_params = self._handle_command_internal(cmd, params)
                return rx_buf[0:2] + cmd_params
        except DeviceError as e:
            return bytes((rx_buf[0], CMD_REPLY_ERROR, e.error_code, cmd))
        except IndexError:
            return bytes((rx_buf[0], CMD_REPLY_ERROR, ERROR_CODE_BAD_INDEX,
                          cmd))
