import os
import pam
import time
import getpass

CLEAR_TERM = "\x1b[2J\x1b[H"

def lock_motd(vt):
    vt.write(CLEAR_TERM + "Locked...\n\n")

def lock_iteration(vt):
    lock_motd(vt)

    p = pam.pam()
    if p.authenticate(getpass.getuser(), getpass.getpass(stream = vt)):
        return True
    else:
        vt.write("pyvtlock: {}\n".format(p.reason))
        getpass.getpass(prompt = "", stream = vt)
        return False

def lock_loop(vt):
    while not lock_iteration(vt):
        pass

if __name__ == '__main__':
    vt = open("/dev/tty", "w")
    lock_loop(vt)
