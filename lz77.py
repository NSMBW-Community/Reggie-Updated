import struct
import ctypes

class LZS11(object):
    def __init__(self):
        self.magic = 0x11
        self.decomp_size = 0
        self.curr_size = 0
        self.compressed = True
        self.outdata = bytearray()

    def Decompress11LZS(self, filein):
        offset = 0
        # check that file is < 2GB
        #print("length of file: 0x%x" % len(filein))
        assert len(filein) < 0x4000 * 0x4000 * 2
        self.magic = filein[offset]
        #print("magic = 0x%x" % self.magic)
        assert self.magic == 0x11
        decomp_size = struct.unpack('<I', filein[offset:offset+4])[0] >> 8
        self.decomp_size = decomp_size
        offset += 4
        # assert decomp_size <= 0x200000
        if decomp_size == 0:
            decomp_size = struct.unpack('<I', filein[offset:offset+4])[0]
            offset += 4
        # assert decomp_size <= 0x200000 << 8

        #print("Decompressing 0x%x. (outsize: 0x%x)" % (len(filein), decomp_size))
        outdata = bytearray()
        curr_size = 0
        lenFileIn = len(filein)

        while curr_size < decomp_size and offset < lenFileIn:
            flags = filein[offset]
            offset += 1

            for i in range(8):
                x = 7 - i
                if curr_size >= decomp_size:
                    break
                if (flags & (1 << x)) > 0:
                    first = filein[offset]
                    offset += 1
                    second = filein[offset]
                    offset += 1

                    if first < 0x20:
                        third = filein[offset]
                        offset += 1

                        if first >= 0x10:
                            fourth = filein[offset]
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

                    outdata.append(filein[offset])
                    offset += 1
                    curr_size += 1

                if offset >= len(filein) or curr_size >= decomp_size:
                    break

        if len(outdata) < decomp_size:
            outdata.extend(bytes(decomp_size - len(outdata)))

        self.outdata = outdata
        self.curr_size = curr_size
        return outdata

    def Compress11LZS(self, data):
        dcsize = len(data)
        cbuffer = bytearray()

        src = 0
        dest = 4

        if dcsize > 0xFFFFFFFF: return None

        cbuffer.append(0x11)

        if dcsize <= 0xFFFFFF:
            cbuffer.append(dcsize & 0xFF)
            cbuffer.append((dcsize >> 8) & 0xFF)
            cbuffer.append((dcsize >> 16) & 0xFF)
        else:
            return None

        flagrange = [7,6,5,4,3,2,1,0]

        CompressionSearch = self.CompressionSearch

        while src < dcsize:
            flag = 0
            flagpos = dest
            cbuffer.append(flag)
            dest += 1

            for i in flagrange:
                matchOffs, matchLen = CompressionSearch(data, src, dcsize, 0x1000, 0xFFFF + 273)
                if matchLen > 0:
                    flag |= (1 << i)

                    matchOffsM1 = matchOffs - 1
                    if matchLen <= 0x10:
                        cbuffer.append((((matchLen - 1) & 0xF) << 4) | ((matchOffsM1 >> 8) & 0xF))
                        cbuffer.append(matchOffsM1 & 0xFF)
                        dest += 2
                    elif matchLen <= 0x110:
                        matchLenM17 = matchLen - 17
                        cbuffer.append((matchLenM17 & 0xFF) >> 4)
                        cbuffer.append(((matchLenM17 & 0xF) << 4) | ((matchOffsM1 & 0xFFF) >> 8))
                        cbuffer.append(matchOffsM1 & 0xFF)
                        dest += 3
                    else:
                        matchLenM273 = matchLen - 273
                        cbuffer.append(0x10 | ((matchLenM273 >> 12) & 0xF))
                        cbuffer.append((matchLenM273 >> 4) & 0xFF)
                        cbuffer.append(((matchLenM273 & 0xF) << 4) | ((matchOffsM1 >> 8) & 0xF))
                        cbuffer.append(matchOffsM1 & 0xFF)
                        dest += 4

                    src += matchLen
                else:
                    cbuffer.append(data[src])

                    src += 1
                    dest += 1

                if src >= dcsize: break

            cbuffer[flagpos] = flag

        return cbuffer

    @staticmethod
    def CompressionSearch(data, offset, totalLength, windowSize=0x1000, maxMatchAmount=18):
        """
        Find the longest possible match (in the current window) of the
        data in "data" (which has total length "length") at offset
        "offset".
        Return the offset of the match relative to "offset", and its
        length.
        This function is ported from ndspy.
        """

        if windowSize > offset:
            windowSize = offset
        start = offset - windowSize

        if windowSize < maxMatchAmount:
            maxMatchAmount = windowSize
        if (totalLength - offset) < maxMatchAmount:
            maxMatchAmount = totalLength - offset

        # Strategy: do a binary search of potential match sizes, to
        # find the longest match that exists in the data.

        lower = 3
        upper = maxMatchAmount

        recordMatchOffset = recordMatchLen = 0
        while lower <= upper:
            # Attempt to find a match at the middle length
            matchLen = (lower + upper) // 2
            match = data[offset : offset + matchLen]
            matchOffset = data.rfind(match, start, offset)

            if matchOffset == -1:
                # No such match -- any matches will be smaller than this
                upper = matchLen - 1
            else:
                # Match found!
                if matchLen > recordMatchLen:
                    recordMatchOffset, recordMatchLen = matchOffset, matchLen
                lower = matchLen + 1

        if recordMatchLen == 0:
            return 0, 0
        return offset - recordMatchOffset, recordMatchLen


def main(args=None):
    """
    Main function for the CLI
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Reggie/Puzzle LZ11 compressor/decompressor.')
    subparsers = parser.add_subparsers(title='commands',
        description='(run a command with -h for additional help)')

    def handleCompress(pArgs):
        """
        Handle the "compress" command.
        """
        with open(pArgs.input_file, 'rb') as f:
            data = f.read()

        outdata = LZS11().Compress11LZS(data)

        outfp = pArgs.output_file
        if outfp is None: outfp = pArgs.input_file + '.cmp'

        with open(outfp, 'wb') as f:
            f.write(outdata)

    parser_compress = subparsers.add_parser('compress', aliases=['c'],
                                            help='compress a file')
    parser_compress.add_argument('input_file',
        help='input file to compress')
    parser_compress.add_argument('output_file', nargs='?',
        help='what to save the compressed file as')
    parser_compress.set_defaults(func=handleCompress)

    def handleDecompress(pArgs):
        """
        Handle the "decompress" command.
        """
        with open(pArgs.input_file, 'rb') as f:
            data = f.read()

        outdata = LZS11().Decompress11LZS(data)

        outfp = pArgs.output_file
        if outfp is None: outfp = pArgs.input_file + '.dec'

        with open(outfp, 'wb') as f:
            f.write(outdata)

    parser_decompress = subparsers.add_parser('decompress', aliases=['d'],
                                              help='decompress a file')
    parser_decompress.add_argument('input_file',
        help='input file to decompress')
    parser_decompress.add_argument('output_file', nargs='?',
        help='what to save the decompressed file as')
    parser_decompress.set_defaults(func=handleDecompress)

    # Parse args and run appropriate function
    pArgs = parser.parse_args(args)
    if hasattr(pArgs, 'func'):
        pArgs.func(pArgs)
    else:  # this happens if no arguments were specified at all
        parser.print_usage()


if __name__ == '__main__':
    main()
