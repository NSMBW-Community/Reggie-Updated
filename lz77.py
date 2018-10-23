import struct
import sys


# Function to get the integer value of a byte, optimized for each Python
# version
if sys.version_info.major < 3:
    def getByte(data, offset):
        return ord(data[offset])
else:
    def getByte(data, offset):
        return data[offset]


class LZS11(object):
    def __init__(self):
        self.magic = 0x11
        self.decomp_size = 0
        self.curr_size = 0
        self.compressed = True
        self.outdata = []
    def Decompress11LZS(self, filein):
        offset = 0
        # check that file is < 2GB
        #print("length of file: 0x%x" % len(filein))
        assert len(filein) < 0x4000 * 0x4000 * 2
        self.magic = getByte(filein, offset)
        #print("magic = 0x%x" % self.magic)
        assert self.magic == 0x11
        decomp_size = struct.unpack('<I', filein[offset:offset+4])[0] >> 8
        self.decomp_size = decomp_size
        offset += 4
        assert decomp_size <= 0x200000
        if decomp_size == 0:
            decomp_size = struct.unpack('<I', filein[offset:offset+4])[0]
            offset += 4
        assert decomp_size <= 0x200000 << 8

        #print("Decompressing 0x%x. (outsize: 0x%x)" % (len(filein), decomp_size))
        outdata = []
        curr_size = 0
        lenFileIn = len(filein)

        while curr_size < decomp_size and offset < lenFileIn:
            flags = getByte(filein, offset)
            offset += 1

            for i in range(8):
                x = 7 - i
                if curr_size >= decomp_size:
                    break
                if (flags & (1 << x)) > 0:
                    first = getByte(filein, offset)
                    offset += 1
                    second = getByte(filein, offset)
                    offset += 1

                    if first < 0x20:
                        third = getByte(filein, offset)
                        offset += 1

                        if first >= 0x10:
                            fourth = getByte(filein, offset)
                            offset += 1

                            pos = (((third & 0xF) << 8) | fourth) + 1
                            copylen = ((second << 4) | ((first & 0xF) << 12) | (third >> 4)) + 273
                        else:
                            pos = (((second & 0xF) << 8) | third) + 1
                            copylen = (((first & 0xF) << 4) | (second >> 4)) + 17
                    else:
                        pos = (((first & 0xF) << 8) | second) + 1
                        copylen = (first >> 4) + 1

                    # We need to append as many copies of copyBuf as it
                    # takes to reach copylen, but no more. This is the
                    # absolute fastest way of doing that that I've
                    # found, based on timing tests.
                    # We repeatedly double the size of copyBuf until
                    # it's the right size or too large, and then trim it
                    # down if we need to.
                    # Keeping track of the buffer length manually
                    # seems to also be slightly faster than calling
                    # len(copyBuf) repeatedly, so we do that, too.
                    copyBuf = outdata[curr_size - pos : curr_size - pos + copylen]
                    copyBufLen = len(copyBuf)
                    while copyBufLen < copylen:
                        copyBuf.extend(copyBuf)
                        copyBufLen *= 2
                    if copyBufLen > copylen:
                        copyBuf = copyBuf[:copylen]
                    outdata.extend(copyBuf)

                    curr_size += copylen
                else:

                    outdata.append(getByte(filein, offset))
                    offset += 1
                    curr_size += 1

                if offset >= len(filein) or curr_size >= decomp_size:
                    break

        if len(outdata) < decomp_size:
            outdata.extend([0] * (decomp_size - len(outdata)))

        self.outdata = outdata
        self.curr_size = curr_size
        return outdata
