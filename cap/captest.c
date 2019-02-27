#include <sys/capability.h>
#include <stdio.h>
#include <unistd.h>

#define GIDSETSIZE 256
gid_t groups[GIDSETSIZE];

int main() {
    cap_t caps = cap_get_proc();
    printf("[+] Capabilities: %s\n", cap_to_text(caps, NULL));

    int numgids = getgroups(GIDSETSIZE, groups);
    if (numgids == -1) {
        perror("[!] getgroups");
        return -1;
    }

    gid_t egid = getegid();
    gid_t gid = getgid();
    printf("[+] Groups: gid = %d, egid = %d, supp =", gid, egid);
    for (int i = 0; i < numgids; i++) {
        printf(" %d", groups[i]);
    }
    printf("\n");
}