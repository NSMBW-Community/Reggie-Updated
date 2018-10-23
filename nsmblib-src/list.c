#include "list.h"

IntList *IntList_new() {
    /* allocates a new IntList and returns a pointer to it
     * must be cleaned up with IntList_delete later,
     * and NOT IntList_free */

    IntList *list = PyMem_Malloc(sizeof(IntList));
    IntList_init(list);
    return list;
}

void IntList_init(IntList *list) {
    /* sets up an IntList (does not need to be called if
     * it's been allocated with IntList_new) */

    list->Count = 0;
    list->AllocSize = INITIAL_SIZE;
    list->Elements = (int*)PyMem_Malloc(sizeof(int) * INITIAL_SIZE);
}

void IntList_free(IntList *list) {
    /* frees the memory for an IntList (only use if the
     * IntList was set up with IntList_init */

    PyMem_Free(list->Elements);
}

void IntList_delete(IntList *list) {
    /* deletes an IntList that was created with IntList_new */

    IntList_free(list);
    PyMem_Free(list);
}

void IntList_resize(IntList *list, int size) {
    /* resizes an IntList's element buffer */

    if (size <= 0) return;
    if (list->Count > size)
        list->Count = size;

    list->AllocSize = size;
    list->Elements = (int*)PyMem_Realloc(list->Elements, sizeof(int) * list->AllocSize);
}

void IntList_add(IntList *list, int elem) {
    /* adds a new element to an IntList */

    list->Count += 1;
    if (list->Count > list->AllocSize) {
        IntList_resize(list, list->AllocSize + SIZE_INCREMENT);
    }

    list->Elements[list->Count - 1] = elem;
}

void IntList_removeAt(IntList *list, int index) {
    /* removes the element at a specific point in an IntList */

    if (index < 0 || index >= list->Count) return;

    // check to see if we have to copy anything
    if (index < (list->Count - 1)) {
        int copyCount = list->Count - index - 1;
        int *copyFrom = &(list->Elements[index+1]);
        int *copyTo = &(list->Elements[index]);
        memmove(copyTo, copyFrom, copyCount*sizeof(int));
    }

    list->Count -= 1;
}

