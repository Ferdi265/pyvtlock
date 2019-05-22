import os
import sys
import pam
import time
import signal
import socket
import termios
import textwrap
import traceback
from argparse import ArgumentParser, RawDescriptionHelpFormatter

sys.path.append("/usr/lib/pyvtlock/")
import vt
from forksignal import Signal

CLEAR_TERM = b"\x1b[2J\x1b[H"
USER = os.environ["USER"]
HOST = socket.gethostname()
MOTD = os.environb.get(b"MOTD", b"\x1b[1;37m<< \x1b[1;36mpyvtlock \x1b[1;37m>>\x1b[0m\n")

cnr = vt.get_active_console()
cvt = vt.open_console(cnr)
nnr = None
nvt = None
oldmode = None
oldattr = None
chan = None
pidfile = None

def parse():
    parser = ArgumentParser(
        "pyvtlock",
        formatter_class = RawDescriptionHelpFormatter,
        description = "A python-based console locking program",
        epilog = textwrap.dedent("""\
        environment variables:
          USER               the user whose password can be used to unlock the session
          XDG_VTNR           the tty number to open and return to after unlocking
          MOTD               the message to display while locked
        """)
    )

    parser.add_argument(
        "-f", "--fork",
        action = "store_true", default = False,
        help = "fork into the background once the screen is locked"
    )

    parser.add_argument(
        "-p", "--pid",
        action = "store_true", default = False,
        help = "print the process id of the console locker"
    )

    parser.add_argument(
        "-P", "--pidfile",
        action = "store", default = None, metavar = "f",
        help = "write the process id of the console locker to f"
    )

    args = parser.parse_args()
    main(args)

def main(args):
    global chan
    global pidfile

    if args.fork:
        chan = Signal()
        if chan.PARENT:
            chan.wait()
            sys.exit(0)

    if args.pid:
        print(os.getpid())

    if args.pidfile != None:
        pidfile = args.pidfile
        with open(pidfile, "w") as f:
            f.write("{}\n".format(os.getpid()))

    time.sleep(.1)

    try:
        success = True
        setup()
        lock_loop()
    except Exception:
        success = False
        traceback.print_exc()

    cleanup()
    if not success:
        sys.exit(1)

def setup():
    setup_sig()
    setup_vt()

def cleanup():
    cleanup_vt()

    if pidfile != None:
        os.remove(pidfile)

    cvt.close()

def setup_sig():
    signal.signal(signal.SIGINT, unlock_hook)
    signal.signal(signal.SIGTERM, unlock_hook)
    signal.signal(signal.SIGHUP, unlock_hook)

def unlock_hook(sn, f):
    cleanup()
    sys.exit(sn == signal.SIGINT)

def setup_vt():
    global nnr
    global nvt
    global oldmode

    nnr = 63
    nvt = vt.open_console(nnr)
    setup_term()

    vt.activate(cvt, nnr)

    signal.signal(signal.SIGUSR1, lambda sn, f: vt.reldisp(nvt, False))
    signal.signal(signal.SIGUSR2, lambda sn, f: vt.reldisp(nvt, True))

    oldmode = vt.getmode(nvt)
    newmode = vt.VtMode(vt.VT_PROCESS, 0, signal.SIGUSR1, signal.SIGUSR2, signal.SIGHUP)
    vt.setmode(nvt, newmode)

    if chan != None:
        chan.signal()

def cleanup_vt():
    if nnr == None or nvt == None or oldmode == None:
        return

    vt.setmode(nvt, oldmode)
    vt.activate(cvt, cnr)

    signal.signal(signal.SIGUSR1, signal.SIG_DFL)
    signal.signal(signal.SIGUSR2, signal.SIG_DFL)

    cleanup_term()

def setup_term():
    global oldattr

    oldattr = termios.tcgetattr(nvt.fileno())
    newattr = termios.tcgetattr(nvt.fileno())
    newattr[3] &= ~termios.ECHO

    termios.tcsetattr(nvt.fileno(), termios.TCSADRAIN, newattr)
    nvt.buffer.write(CLEAR_TERM)

def cleanup_term():
    global oldattr
    global nnr
    global nvt
    global oldmode

    termios.tcsetattr(nvt.fileno(), termios.TCSADRAIN, oldattr)
    oldattr = None

    nvt.buffer.write(CLEAR_TERM)
    nvt.close()

    nnr = None
    nvt = None
    oldmode = None

def lock_loop():
    while not lock_iteration():
        pass

def lock_iteration():
    lock_motd()
    read_pwd("", False)

    p = pam.pam()
    pwd = read_pwd("Password: ")
    if p.authenticate(USER, pwd):
        return True
    else:
        print("pyvtlock: {}".format(p.reason), file = nvt)
        time.sleep(1.5)
        return False

def lock_motd():
    nvt.buffer.write(CLEAR_TERM)
    nvt.buffer.write(MOTD + b"\n")
    print("{} locked by {}".format(HOST, USER), file = nvt)

def read_pwd(prompt, newline = True):
    print(prompt, end = "", file = nvt)

    data = nvt.readline()
    if data[-1] == "\n":
        data = data[:-1]

    if newline:
        print(file = nvt)

    return data

if __name__ == '__main__':
    parse()
