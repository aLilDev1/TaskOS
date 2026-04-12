/**

  "/System Folder/API/Pipe.C"
  Allows communication between 2 programs via a file inside "/tmp".
  Does not matter if "/tmp" is redirected to "/tmpfs" or not.

**/

#include <stdio.h>    // I/O services
#include <stdlib.h>   // Write and Read commands
#include <string.h>   // String services
#include <unistd.h>   // POSIX services
#include <fcntl.h>    // File services
#include <sys/stat.h> // File metadata/creation
#include "pipe.h"     // Include header file
#define MAX_PIPES 256 // Max amount of pipes between two applications

typedef struct {      // Structure of PipeEntry
    char path[64];        // The path to the pipe ("/tmp/Pipe####" who redirects to "/System Folder/TempFallback/Pipe####" or "/tmpfs/Pipe####")
    int in_use;           // If the pipe is in use or not
} PipeEntry;          // Structure Name (PipeEntry)

static PipeEntry pipes[MAX_PIPES]; // All pipes the program KNOWS about


static int GetPipeName(char *outPath) {         // Internal Use; To create pipe file name, aka pipe ID
    for (int i = 0; i < 0x10000; i++) {             // Go through 0x0000 to 0xFFFF
        snprintf(outPath, 64, "/tmp/Pipe%04X", i);      // Assemble file name string

        if (access(outPath, F_OK) != 0) {               // Check if the file does NOT exist
            return(0);                                      // Return 0 for success
        }
    }
    return(-1);                                     // Return -1 for fail
}


int CreatePipe(int pid) {
    (void)pid;  // May only allow 2 programs to communicate on 1 pipe in the future... maybe, and hopefully?

    for (int i = 0; i < MAX_PIPES; i++) {          // Goes from zero to MAX_PIPES
        if (!pipes[i].in_use) {                        // Check if pipe is in use

            if (GetPipeName(pipes[i].path) != 0)
                return(-1);                            // Return -1 for  fail

            if (mkfifo(pipes[i].path, 0666) != 0)      
                return(-1);                            // Return -1 for fail

            pipes[i].in_use = 1;                           // Set pipe as in use
            return(i);                                     // Return i for success, and pipe ID
        }
    }

    return(-1);                                        // Return -1 for fail
}

/**
Sorry about me giving up on the rest of the comments, ill add the rest later.
For whatever reason I spit out code then comment...
**/


int WritePipe(int pipe_id, const void *data, size_t size) {
    if (pipe_id < 0 || pipe_id >= MAX_PIPES) return -1;
    if (!pipes[pipe_id].in_use) return -1;

    int fd = open(pipes[pipe_id].path, O_WRONLY);
    if (fd < 0) {
		return(-1);
	};

    write(fd, &size, sizeof(size));
    write(fd, data, size);

    close(fd);
    return(0);
}


int ReadPipe(int pipe_id, void *buffer, size_t maxSize, size_t *outSize) {
    if (pipe_id < 0 || pipe_id >= MAX_PIPES) return -1;
    if (!pipes[pipe_id].in_use) return -1;

    int fd = open(pipes[pipe_id].path, O_RDONLY);
    if (fd < 0) {
		return(-1);
	};

    size_t size;
    read(fd, &size, sizeof(size));

    if (size > maxSize) {
        close(fd);
        return(-2);
    }

    read(fd, buffer, size);

    *outSize = size;

    close(fd);
    return(0);
}