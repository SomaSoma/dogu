"""
    +---------------+
    |Pad Length? (8)|
    +-+-------------+-----------------------------------------------+
    |R|                  Promised Stream ID (31)                    |
    +-+-----------------------------+-------------------------------+
    |                   Header Block Fragment (*)                 ...
    +---------------------------------------------------------------+
    |                           Padding (*)                       ...
    +---------------------------------------------------------------+

"""

from dogu.frame import (Frame, FrameType)
from dogu.util import int_to_bytes
from dogu.http2_exception import ProtocolError
from hpack.hpack import (Encoder, Decoder)


class PushPromiseFrame(Frame):

    PAD_MAX_LENGTH = 255

    # HEADERS frame flags

    END_HEADER_FLAG = 0x4

    PADDED_FLAG = 0x8

    @classmethod
    def load(cls, frame, header, encoded_headers=[], decoder=Decoder()):

        # frame length, type, flag, id
        frm_len, frm_type, frm_flag, frm_id = header

        if frm_id is 0x0:  # protocol error
            raise ProtocolError("'frm_id must not be 0x0")

        if frm_type is not FrameType.PUSH_PROMISE:
            raise ValueError("frame is not type of PUSH_PROMISE type")

        end_header = False

        header_start_index = 0  # default is payload stat index
        header_pad_length = 0

        if frm_flag & PushPromiseFrame.END_HEADER_FLAG is not 0:
            end_header = True

        # create header frame to return
        header_frame = cls(frm_id, [], end_header)

        if frm_flag & PushPromiseFrame.PADDED_FLAG is not 0:  # if it is padded
            header_pad_length = frame[header_start_index]
            header_start_index += 1  # if padded, first byte is pad length

        # get promise stream id

        promised_stream_id = frame[header_start_index] << 24
        promised_stream_id += frame[header_start_index + 1] << 16
        promised_stream_id += frame[header_start_index + 2] << 8
        promised_stream_id += frame[header_start_index + 3]

        # create header block

        header_end_index = 9 + frm_len - header_pad_length

        # get header block fragment

        header_block_frag = frame[header_start_index:header_end_index]
        header_frame._data = header_block_frag

        if end_header:
            header_buffer = bytearray()

            for encoded_header in encoded_headers:
                if encoded_header.is_encoded:
                    header_buffer += encoded_header._encoded_data
                else:
                    raise ValueError("encoded header didn't encoded")

            header_buffer += header_block_frag

            header_frame._header_list = decoder.decode(header_buffer)
        else:
            header_frame._encoded_data = header_block_frag

        return header_frame

    def __init__(self, id, header_list=[], end_header=True):

        self.is_end_header = end_header

        self._is_priority = False

        self._is_padded = False

        self._header_list = header_list  # http header list

        self._encoded_data = None

        self.promised_stream_id = 0x0  # default

        Frame.__init__(self, type=FrameType.PUSH_PROMISE, flag=0x0, id=id, data=None)

    def __repr__(self):

        repr = ""

        for header in self._header_list:
            repr += str(header[0]) + ' :' + str(header[1]) + '\n'

        return repr

    def get_frame_bin(self):

        # Encode header

        encoder = Encoder()

        headers_frame_field = bytearray()

        if self._data is None:  # if user didn't touch data
            self._data = encoder.encode(self._header_list)  # encode header list

        self._flag = self.flag  # get flag by method

        if self._is_padded:

            headers_frame_field.append(self._pad_len)  # append pad length

            self._data += bytearray(self._pad_len)  # append pad byte in pad length

        headers_frame_field += int_to_bytes(self.promised_stream_id, 4)  # append promised stream id

        self._data = headers_frame_field + self._data  # append HEADERS field

        return Frame.get_frame_bin(self)

    def add(self, name, value):

        self._header_list.append((name.lower(), value))

    def get(self, name):

        for header in self._header_list:
                if header[0] == name:
                    return header[1]

        return None

    def get_all(self):
        return self._header_list

    @property
    def status(self):
        return self.get(':status')

    @status.setter
    def status(self, value):
        self.add(':status', value)

    @property
    def method(self):
        return self.get(':method')

    @method.setter
    def method(self, value):
        self.add(':method', value)

    @property
    def scheme(self):
        return self.get(':scheme')

    @scheme.setter
    def scheme(self, value):
        self.add(':scheme', value)

    @property
    def authority(self):
        return self.get(':authority')

    @authority.setter
    def authority(self, value):
        self.add(':authority', value)

    @property
    def path(self):
        return self.get(':path')

    @path.setter
    def path(self, value):
        self.add(':path', value)

    # Remove headers

    def remove(self, name):

        for header in self._header_list:
            if header[0] == name:
                self._header_list.remove(header)

    @property
    def flag(self):
        flag = 0x0

        if self.is_end_header:
            flag |= PushPromiseFrame.END_HEADER_FLAG

        if self._is_padded:
            flag |= PushPromiseFrame.PADDED_FLAG

        return flag

    @property
    def is_encoded(self):
        return self._encoded_data is not None

    def padding(self, pad_len):

        if pad_len > PushPromiseFrame.PAD_MAX_LENGTH:  # padding length error
            raise ValueError("pad_len is greater then pad max length")

        self._flag |= PushPromiseFrame.PADDED_FLAG  # flag padded
        self._is_padded = True
        self._pad_len = pad_len
