#include <Python.h>
#include "bytesobject.h"
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
 * 0.4.1: Added Python 3 compatibility
 */

#define CURRENT_VERSION 4

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

    const char *data;
    int datalength;

    u8 *decoded;
    PyObject *retvalue;
    int decompsize;

    /* used while decompressing */
    int curr_size;
    const char *source;
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
    retvalue = PyBytes_FromStringAndSize((const char*)decoded, decompsize);
    PyMem_Free(decoded);

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
    retvalue = PyBytes_FromStringAndSize(decoded, 1048576);
    PyMem_Free(decoded);

    return retvalue;
}

static PyMethodDef NSMBLibMethods[] = {
    {"getVersion", nsmblib_getVersion, METH_VARARGS,
     "Gets the current version of the NSMB module."},
    {"decompress11LZS", nsmblib_decompress11LZS, METH_VARARGS,
     "Decompresses a file using LZSS 0x11 variant."},
    {"decodeTileset", nsmblib_decodeTileset, METH_VARARGS,
     "Decodes an uncompressed RGB5A4 tileset into ARGB32 Premultiplied."},
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3

struct module_state {
    PyObject *error;
};
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
static int nsmblib_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}
static int nsmblib_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "nsmblib",
        NULL,
        sizeof(struct module_state),
        NSMBLibMethods,
        NULL,
        nsmblib_traverse,
        nsmblib_clear,
        NULL
};
#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC
PyInit_nsmblib(void)
#else
void
initnsmblib(void)
#endif
{

#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("nsmblib", NSMBLibMethods);
#endif

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}