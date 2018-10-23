#include <Python.h>
#include "list.h"

#define s32 signed int
#define s16 signed short
#define s8 signed char
#define u32 unsigned int
#define u16 unsigned short
#define u8 unsigned char

/************************************************************
 * New Super Mario Bros Wii Module for Python               *
 * Written by Treeki; 19th December 2009                    *
 ************************************************************
 * This module is used by the Reggie! level editor          *
 * in order to speed up some algorithms like decoding       *
 * textures and decompressing data. Slower Python versions  *
 * of the functions are available in reggie.py, and will be *
 * used if this module isn't available for whatever reason. *
 ************************************************************/

/* Update Log:
 * -----------
 * 0.1: First version
 * 0.2: Added nsmblib_decompress11LZS
 * 0.3: Fixed hosed memory addressing in nsmblib_decompress11LZS
 * 0.4: Added nsmblib_getVersion
 * 0.5: Added nsmblib_compress11LZS (thanks to puyo_tools
 *      for the original C# code)
 */

#define CURRENT_VERSION 5

static PyObject *nsmblib_getVersion(PyObject *self, PyObject *args) {
    /* Gets the current version of the NSMB module.
     * Returns: int (version number * 10)
     * Parameters: none
     */

     return Py_BuildValue("i", CURRENT_VERSION);
}

static PyObject *nsmblib_decompress11LZS(PyObject *self, PyObject *args) {
    /* Decompresses a file using LZSS 0x11 variant.
     * Returns: str (containing the decompressed data)
     * Parameters:
     *  - str data (containing the compressed data)
     */

    const u8 *data;
    int datalength;

    u8 *decoded;
    PyObject *retvalue;
    int decompsize;

    /* used while decompressing */
    int curr_size;
    const u8 *source;
    u8 *dest, *end;
    int len, i, j, cdest, disp, flag;
    u8 b1, b2, b3, bt, flags;

    /* get the arguments */
    if (!PyArg_ParseTuple(args, "s#", &data, &datalength))
        return NULL;

    /* parse the file itself */
    source = data;
    if (*(source++) != 0x11) {
        /* it's invalid */
        Py_INCREF(Py_None);
        return Py_None;
    }

    decompsize = 0;
    for (i = 0; i < 3; i++) {
        decompsize += (*(source++)) << (i * 8);
    }

    if (decompsize == 0) {
        for (i = 0; i < 4; i++) {
            decompsize += (*(source++)) << (i * 8);
        }
    }

    /* if it's obviously invalid, kill it */
    if (decompsize > 0x800000) {
        /* fixed 8mb limit */
        PySys_WriteStdout("Too big! %d\n", decompsize);
        Py_INCREF(Py_None);
        return Py_None;
    }

    /* allocate a buffer */
    decoded = (char*)PyMem_Malloc(decompsize);
    if (decoded == NULL)
        return PyErr_NoMemory();

    /* now we can start going through everything */
    dest = decoded;
    end = &decoded[decompsize];
    curr_size = 0;

    while (curr_size < decompsize) {
        flags = *(source++);

        for (i = 0; i < 8 && curr_size < decompsize; i++) {
            flag = (flags & (0x80 >> i));
            if (flag > 0) {
                b1 = *(source++);

                switch (b1 >> 4) {
                    case 0:
                        len = b1 << 4;
                        bt = *(source++);
                        len |= bt >> 4;
                        len += 0x11;

                        disp = (bt & 0x0F) << 8;
                        b2 = *(source++);
                        disp |= b2;
                        break;

                    case 1:
                        bt = *(source++);
                        b2 = *(source++);
                        b3 = *(source++);

                        len = (b1 & 0xF) << 12;
                        len |= (bt << 4);
                        len |= (b2 >> 4);
                        len += 0x111;
                        disp = (b2 & 0xF) << 8;
                        disp |= b3;
                        break;

                    default:
                        len = (b1 >> 4) + 1;
                        disp = (b1 & 0x0F) << 8;
                        b2 = *(source++);
                        disp |= b2;
                        break;
                }

                if (disp > curr_size) {
                    /* how's that for failure? */
                    PyMem_Free(decoded);
                    Py_INCREF(Py_None);
                    return Py_None;
                }

                cdest = curr_size;

                for (j = 0; j < len && curr_size < decompsize; j++) {
                    *(dest++) = decoded[cdest - disp - 1 + j];
                    curr_size++;
                }

                if (curr_size > decompsize) {
                    break;
                }
            } else {
                *(dest++) = *(source++);
                curr_size++;

                if (curr_size > decompsize) {
                    break;
                }
            }
        }

    }

    /* return it */
    retvalue = PyString_FromStringAndSize((const char*)decoded, decompsize);
    PyMem_Free(decoded);

    return retvalue;
}

typedef struct LZDict_t {
    int WindowSize;
    int WindowStart;
    int WindowLength;
    int MinMatchAmount;
    int MaxMatchAmount;
    int BlockSize;
    IntList OffsetList[0x100];
} LZDict;

void LZDict_init(LZDict *dict);
void LZDict_free(LZDict *dict);
void LZDict_search(LZDict *dict, u8 *data, int offset, int length, int *ret1, int *ret2);
void LZDict_slide_window(LZDict *dict, int amount);
void LZDict_slide_block(LZDict *dict);
void LZDict_remove_old_entries(LZDict *dict, u8 index);
void LZDict_set_window_size(LZDict *dict, int size);
void LZDict_set_min_match_amount(LZDict *dict, int amount);
void LZDict_set_max_match_amount(LZDict *dict, int amount);
void LZDict_set_block_size(LZDict *dict, int size);
void LZDict_add_entry(LZDict *dict, u8 *data, int offset);
void LZDict_add_entry_range(LZDict *dict, u8 *data, int offset, int length);


void LZDict_init(LZDict *dict) {
    /* set up the dict */
    int i;
    for (i = 0; i < 0x100; i++) {
        IntList_init(&(dict->OffsetList[i]));
    }

    dict->WindowSize = 0x1000;
    dict->WindowStart = 0;
    dict->WindowLength = 0;
    dict->MinMatchAmount = 3;
    dict->MaxMatchAmount = 18;
    dict->BlockSize = 0;
}

void LZDict_free(LZDict *dict) {
    /* free the dict */
    int i;
    for (i = 0; i < 0x100; i++) {
        IntList_free(&(dict->OffsetList[i]));
    }
}

void LZDict_search(LZDict *dict, u8 *data, int offset, int length, int *ret1, int *ret2) {
    int i;
    int MatchStart;
    int MatchSize;

    LZDict_remove_old_entries(dict, data[offset]);

    if (offset < dict->MinMatchAmount || length - offset < dict->MinMatchAmount) {
        *ret1 = 0;
        *ret2 = 0;
        return;
    }

    // start finding matches
    *ret1 = 0;
    *ret2 = 0;

    for (i = dict->OffsetList[data[offset]].Count - 1; i >= 0; i--) {
        MatchStart = dict->OffsetList[data[offset]].Elements[i];
        MatchSize = 1;

        while (MatchSize < dict->MaxMatchAmount && MatchSize < dict->WindowLength && MatchStart + MatchSize < offset && offset + MatchSize < length && data[offset + MatchSize] == data[MatchStart + MatchSize])
            MatchSize++;

        if (MatchSize >= dict->MinMatchAmount && MatchSize > *ret2) {
            // this is a good match
            *ret1 = offset - MatchStart;
            *ret2 = MatchSize;
            if (MatchSize == dict->MaxMatchAmount)
                break; // don't look for more matches
        }
    }
}

void LZDict_slide_window(LZDict *dict, int amount) {
    if (dict->WindowLength == dict->WindowSize)
        dict->WindowStart += amount;
    else {
        if (dict->WindowLength + amount <= dict->WindowSize)
            dict->WindowLength += amount;
        else {
            amount -= (dict->WindowSize - dict->WindowLength);
            dict->WindowLength = dict->WindowSize;
            dict->WindowStart += amount;
        }
    }
}

void LZDict_slide_block(LZDict *dict) {
    dict->WindowStart += dict->BlockSize;
}

void LZDict_remove_old_entries(LZDict *dict, u8 index) {
    int i;

    for (i = 0; i < dict->OffsetList[index].Count;) { // don't increment i
        if (dict->OffsetList[index].Elements[i] >= dict->WindowStart)
            break;
        else
            IntList_removeAt(&(dict->OffsetList[index]), 0);
    }
}

void LZDict_set_window_size(LZDict *dict, int size) {
    dict->WindowSize = size;
}

void LZDict_set_min_match_amount(LZDict *dict, int amount) {
    dict->MinMatchAmount = amount;
}

void LZDict_set_max_match_amount(LZDict *dict, int amount) {
    dict->MaxMatchAmount = amount;
}

void LZDict_set_block_size(LZDict *dict, int size) {
    dict->BlockSize = size;
    dict->WindowLength = size;
}

void LZDict_add_entry(LZDict *dict, u8 *data, int offset) {
    IntList_add(&(dict->OffsetList[data[offset]]), offset);
}

void LZDict_add_entry_range(LZDict *dict, u8 *data, int offset, int length) {
    int i;
    for (i = 0; i < length; i++)
        IntList_add(&(dict->OffsetList[data[offset]]), offset + i);
}

static PyObject *nsmblib_compress11LZS(PyObject *self, PyObject *args) {
    /* Compresses a file using LZSS 0x11 variant.
     * Returns: str (containing the compressed data)
     * Parameters:
     *  - str data (containing the decompressed data)
     */

    const u8 *data;
    int datalength;

    u8 *src_ptr;
    u8 *dest_ptr;

    u8 *end_src_ptr;

    u8 *buffer;
    int bufSize;

    PyObject *retvalue;
    int i, ret1, ret2; // used in the compression loop
    LZDict dict;

    /* get the arguments */
    if (!PyArg_ParseTuple(args, "s#", &data, &datalength))
        return NULL;

    /* allocate a buffer to start with */
    bufSize = datalength;
    buffer = (char*)PyMem_Malloc(bufSize);
    if (buffer == NULL)
        return PyErr_NoMemory();

    src_ptr = (u8*)data;
    dest_ptr = buffer;

    end_src_ptr = (u8*)data + datalength;

    LZDict_init(&dict);
    LZDict_set_window_size(&dict, 0x1000);
    LZDict_set_max_match_amount(&dict, 0xFFFF + 273);

    /* write the decomp size */
    if (datalength <= 0xFFFFFF) {
        *dest_ptr++ = 0x11;
        *dest_ptr++ = (datalength & 0xFF);
        *dest_ptr++ = ((datalength >> 8) & 0xFF);
        *dest_ptr++ = ((datalength >> 16) & 0xFF);
    } else {
        *dest_ptr++ = 0x11;
        *dest_ptr++ = 0x00;
        *dest_ptr++ = 0x00;
        *dest_ptr++ = 0x00;
        *dest_ptr++ = (datalength & 0xFF);
        *dest_ptr++ = ((datalength >> 8) & 0xFF);
        *dest_ptr++ = ((datalength >> 16) & 0xFF);
        *dest_ptr++ = ((datalength >> 24) & 0xFF);
    }

    /* start compression */
    while (src_ptr < end_src_ptr) {
        u8 flag = 0;
        u8 *flagpos = dest_ptr;
        *dest_ptr++ = flag;

        for (i = 7; i >= 0; i--) {
            LZDict_search(&dict, data, src_ptr - data, datalength, &ret1, &ret2);
            if (ret2 > 0) { /* there is a compression match */
                flag |= (u8)(1 << i);

                /* write the distance/length pair */
                if (ret2 <= 0xF + 1) { /* 2 bytes */
                    *dest_ptr++ = (((ret2 - 1) & 0xF) << 4) | (((ret1 - 1) & 0xFFF) >> 8);
                    *dest_ptr++ = ((ret1 - 1) & 0xFF);
                } else if (ret2 <= 0xFF + 17) { /* 3 bytes */
                    *dest_ptr++ = (((ret2 - 17) & 0xFF) >> 4);
                    *dest_ptr++ = ((((ret2 - 17) & 0xF) << 4) | (((ret1 - 1) & 0xFFF) >> 8));
                    *dest_ptr++ = ((ret1 - 1) & 0xFF);
                } else { /* 4 bytes */
                    *dest_ptr++ = ((1 << 4) | (((ret2 - 273) & 0xFFFF) >> 12));
                    *dest_ptr++ = (((ret2 - 273) & 0xFFF) >> 4);
                    *dest_ptr++ = ((((ret2 - 273) & 0xF) << 4) | (((ret1 - 1) & 0xFFF) >> 8));
                    *dest_ptr++ = ((ret1 - 1) & 0xFF);
                }

                LZDict_add_entry_range(&dict, data, src_ptr - data, ret2);
                LZDict_slide_window(&dict, ret2);

                src_ptr += ret2;

            } else { /* there wasn't a match */
                flag |= (u8)(0 << i);

                LZDict_add_entry(&dict, data, src_ptr - data);
                LZDict_slide_window(&dict, 1);

                *dest_ptr++ = *src_ptr++;
            }

            /* check for out of bounds */
            if (src_ptr >= end_src_ptr)
                break;
        }

        /* write the flag */
        *flagpos = flag;
    }

    LZDict_free(&dict);

    /* return it! */
    retvalue = PyString_FromStringAndSize((const char*)buffer, dest_ptr - buffer);
    PyMem_Free(buffer);

    return retvalue;
}

static PyObject *nsmblib_decodeTileset(PyObject *self, PyObject *args) {
    /* Decodes an uncompressed RGB5A4 tileset into ARGB32 Premultiplied.
     * Assumes that the size of the decoded tileset is 1024x512.
     * Returns: str (containing the decoded data)
     * Parameters:
     *  - str texture (containing the raw texture data)
     */

    const char *texture;
    int texlength;
    u8 *decoded;
    PyObject *retvalue;

    /* used later in the pixel loop */
    const char *pointer;
    unsigned int *output;
    int tx, ty, i;

    /* get the arguments */
    if (!PyArg_ParseTuple(args, "s#", &texture, &texlength))
        return NULL;

    if (texlength < 524288) {
        /* if the input string is too small, return None */
        Py_INCREF(Py_None);
        return Py_None;
    }

    /* allocate memory */
    decoded = (char*)PyMem_Malloc(1048576);
    if (decoded == NULL)
        return PyErr_NoMemory();

    /* loop through every tile */
    tx = 0;
    ty = 0;
    pointer = texture;
    output = (int*)decoded;

    for (i = 0; i < 16384; i++) {
        /* loop through every row in this tile */
        int y = ty;
        int endy = ty + 4;

        for (; y < endy; y++) {
            /* now loop through each pixel */
            int sourcey = y << 10;
            int x = tx;
            int endx = tx + 4;

            for (; x < endx; x++) {
                /* calculate this pixel */
                int pos = sourcey | x;
                char a = *(pointer++);
                char b = *(pointer++);

                if ((a & 0x80) == 0) {
                    /* use alpha */
                    char alpha = (a & 0x70) << 1;
                    unsigned int x = (alpha << 24) | ((a & 0xF) << 20) | ((b & 0xF0) << 8) | ((b & 0xF) << 4);

                    /* this code from Qt's PREMUL() inline function in
                     * src/gui/painting/qdrawhelper_p.h */
                    unsigned int al = x >> 24;
                    unsigned int t = (x & 0xff00ff) * al;
                    t = (t + ((t >> 8) & 0xff00ff) + 0x800080) >> 8;
                    t &= 0xff00ff;
                    x = ((x >> 8) & 0xff) * al;
                    x = (x + ((x >> 8) & 0xff) + 0x80);
                    x &= 0xff00;
                    x |= t | (al << 24);

                    output[pos] = x;

                } else {
                    /* no alpha */
                    output[pos] = 0xFF000000 | ((a & 0x7C) << 17) | ((a & 0x3) << 14) | ((b & 0xE0) << 6) | ((b & 0x1F) << 3);
                }
            }
        }

        /* move the positions onwards */
        tx += 4;
        if (tx >= 1024) {
            tx = 0;
            ty += 4;
        }
    }

    /* return it */
    retvalue = PyString_FromStringAndSize(decoded, 1048576);
    PyMem_Free(decoded);

    return retvalue;
}

static PyMethodDef NSMBLibMethods[] = {
    {"getVersion", nsmblib_getVersion, METH_VARARGS,
     "Gets the current version of the NSMB module."},
    {"decompress11LZS", nsmblib_decompress11LZS, METH_VARARGS,
     "Decompresses a file using LZSS 0x11 variant."},
    {"compress11LZS", nsmblib_compress11LZS, METH_VARARGS,
     "Compresses a file using LZSS 0x11 variant."},
    {"decodeTileset", nsmblib_decodeTileset, METH_VARARGS,
     "Decodes an uncompressed RGB5A4 tileset into ARGB32 Premultiplied."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initnsmblib(void) {
    (void)Py_InitModule("nsmblib", NSMBLibMethods);
}