#ifndef PIPE_H
#define PIPE_H

#include <stddef.h>

int CreatePipe(int pid);
int WritePipe(int pipe_id, const void *data, size_t size);
int ReadPipe(int pipe_id, void *buffer, size_t maxSize, size_t *outSize);

#endif