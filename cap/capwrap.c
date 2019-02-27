#include <sys/capability.h>
#include <sys/prctl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <grp.h>

#if DEBUG
    #define LOG(...) printf(__VA_ARGS__)
#else
    #define LOG(...)
#endif

#ifndef COMMAND
    #define COMMAND "./captest"
#endif

#ifndef KEEPENV
    #define KEEPENV
#endif

#define GIDSETSIZE 256
gid_t groups[GIDSETSIZE];

char * argv[] = { COMMAND, NULL };
char * keep_env[] = { KEEPENV };
#define ARRSIZ(x) ((sizeof x) / (sizeof x[0]))

int main() {
    cap_t caps = cap_get_proc();
    LOG("[1] Capabilities: %s\n", cap_to_text(caps, NULL));

    cap_value_t newcaps[1] = { CAP_SYS_TTY_CONFIG };
    cap_set_flag(caps, CAP_INHERITABLE, 1, newcaps, CAP_SET);
    if (cap_set_proc(caps) == -1) {
        perror("[!] cap_set_proc");
        return -1;
    }
    LOG("[2] Capabilities: %s\n", cap_to_text(caps, NULL));

    if (prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_RAISE, CAP_SYS_TTY_CONFIG, 0, 0) == -1) {
        perror("[!] prctl");
        return -1;
    }
    LOG("[3] Capabilities: %s\n", cap_to_text(caps, NULL));

    gid_t egid = getegid();
    gid_t gid = getgid();
    int numgids = getgroups(GIDSETSIZE, groups);
    if (numgids == -1) {
        perror("[!] getgroups");
        return -1;
    } else if (numgids == 256) {
        LOG("[!] too many groups!");
    }
    LOG("[1] Groups: gid = %d, egid = %d, supp =", gid, egid);
    for (int i = 0; i < numgids; i++) {
        LOG(" %d", groups[i]);
    }
    LOG("\n");

    groups[numgids] = egid;
    if (setgroups(numgids + 1, groups) == -1) {
        perror("[!] setgroups");
        return -1;
    }
    if (setgid(gid) == -1) {
        perror("[!] getgid");
        return -1;
    }
    egid = getegid();
    gid = getgid();
    LOG("[2] Groups: gid = %d, egid = %d, supp =", gid, egid);
    for (int i = 0; i < numgids + 1; i++) {
        LOG(" %d", groups[i]);
    }
    LOG("\n");

    char * envp[ARRSIZ(keep_env) + 1];
    int envlen = 0;
    LOG("[1] Environment:");
    for (unsigned int i = 0; i < ARRSIZ(keep_env); i++) {
        char * v = getenv(keep_env[i]);
        if (v != NULL) {
            char * buf = malloc(strlen(keep_env[i]) + strlen(v) + 2);
            if (buf == NULL) {
                perror("[!] malloc");
                return -1;
            }
            sprintf(buf, "%s=%s", keep_env[i], v);

            LOG(" %s", buf);
            envp[envlen++] = buf;
        }
    }
    LOG("\n");
    envp[envlen] = NULL;

    execve(argv[0], argv, envp);
    perror("[!] execv");
    return -1;
}
