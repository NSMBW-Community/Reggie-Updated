#include <Python.h>
#include <string.h>

/* This is a basic list implementation in C, for
 * LZ compression. It's not good, but it works. Don't use it.
 *
 * It's not really memory efficient or anything, either. -_-
 */

#define INITIAL_SIZE 0x20
#define SIZE_INCREMENT 0x80

typedef struct IntList_t {
    int Count;
    int AllocSize;
    int *Elements;
} IntList;

IntList *IntList_new();
void IntList_init(IntList *list);
void IntList_free(IntList *list);
void IntList_delete(IntList *list);
void IntList_resize(IntList *list, int size);
void IntList_add(IntList *list, int elem);
void IntList_removeAt(IntList *list, int index);
