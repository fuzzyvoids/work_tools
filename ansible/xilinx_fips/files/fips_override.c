/*
 * Genericization variables:
 *   Provide placeholder values such as internal_dns_domain, internal_mirror_base_url, shared_tools_path, and related service hostnames through the build or templating process before deployment.
 */
/*
 * See https://unix.stackexchange.com/questions/237636/
 *
 * capture calls to a routine and replace with your code
 * gcc -Wall -O2 -fpic -shared -ldl -o shim_open.so shim_open.c
 * LD_PRELOAD=/.../shim_open.so vitis
 */
#define _FCNTL_H 1  /* hack for open() prototype */
#define _GNU_SOURCE /* needed to get RTLD_NEXT defined in dlfcn.h */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
#define OLDNAME "/proc/sys/crypto/fips_enabled"

/* Not the best file to use, but this will also return 0 */
#define NEWNAME "{{ xilinx_tools_path }}/Vitis/fips_enabled"

int open(const char *pathname, int flags, mode_t mode) {
    static int (*real_open)(const char *pathname, int flags, mode_t mode) = NULL;
    if (!real_open) {
        real_open = dlsym(RTLD_NEXT, "open");
        char *error = dlerror();
        if (error != NULL) {
            fprintf(stderr, "%s\n", error);
            exit(1);
        }
    }

    if (strcmp(pathname, OLDNAME) == 0) {
        pathname = NEWNAME;
    }

    return real_open(pathname, flags, mode);
}

