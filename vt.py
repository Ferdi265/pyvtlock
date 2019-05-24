"""
Python Interface for the linux VT ioctls

- see IOCTL_CONSOLE(2) (incomplete)
- see <linux/vt.h> (not very well documented)
"""

import io
import os
import array
import fcntl
import struct

MIN_NR_CONSOLES = 1
MAX_NR_CONSOLES = 63

VT_OPENQRY = 0x5600
VT_GETMODE = 0x5601
VT_SETMODE = 0x5602
VT_GETSTATE = 0x5603
VT_SENDSIG = 0x5604
VT_RELDISP = 0x5605
VT_ACTIVATE = 0x5606
VT_WAITACTIVE = 0x5607
VT_DISALLOCATE = 0x5608
VT_RESIZE = 0x5609
VT_RESIZEX = 0x560A
VT_LOCKSWITCH = 0x560B
VT_UNLOCKSWITCH = 0x560C
VT_GETHIFONTMASK = 0x560D
VT_WAITEVENT = 0x560E
VT_SETACTIVATE = 0x560F

VT_AUTO = 0
VT_PROCESS = 1
VT_ACKACQ = 2

VT_EVENT_SWITCH = 1
VT_EVENT_BLANK = 2
VT_EVENT_UNBLANK = 4
VT_EVENT_RESIZE = 8
VT_EVENT_MAX = 0xF

class VtMode:
    FMT = "bbhhh"
    def __init__(self, m, wv, rs, qs, fs):
        self.mode = m
        self.waitv = wv
        self.relsig = rs
        self.acqsig = qs
        self.frsig = fs

    def __repr__(self):
        return "<VtMode {}>".format(self.__dict__)

class VtStat:
    FMT = "HHH"
    def __init__(self, a, si, st):
        self.active = a
        self.signal = si
        self.state = st

    def __repr__(self):
        return "<VtStat {}>".format(self.__dict__)

class VtSizes:
    FMT = "HHH"
    def __init__(self, r, c, s):
        self.rows = r
        self.cols = c
        self.scrollsize = s

    def __repr__(self):
        return "<VtSizes {}>".format(self.__dict__)

class VtConSize:
    FMT = "HHHHHH"
    def __init__(self, r, c, s, cl, vc, cc):
        self.rows = r
        self.cols = c
        self.scrollsize = s
        self.clin = cl
        self.vcol = vc
        self.ccol = cc

    def __repr__(self):
        return "<VtSizes {}>".format(self.__dict__)

class VtEvent:
    FMT = "IIIIIII"
    def __init__(self, e, o, n, p0, p1, p2, p3):
        self.event = e
        self.oldev = o
        self.newev = n
        self.pad0 = p0
        self.pad1 = p1
        self.pad2 = p2
        self.pad3 = p3

    def __repr__(self):
        return "<VtEvent {}>".format(self.__dict__)

def open_console(nr):
    return io.TextIOWrapper(open("/dev/tty{}".format(nr), "r+b", buffering = 0), encoding = "UTF-8", write_through = True)

def get_active_console():
    try:
        nr = int(os.environ["XDG_VTNR"], 10)
    except KeyError as e:
        raise RuntimeError("XDG_VTNR does not exist") from e
    except ValueError as e:
        raise RuntimeError("XDG_VTNR is not a valid number") from e

    return nr

def openqry(vt):
    newvt = array.array('i', [0])

    fcntl.ioctl(vt.fileno(), VT_OPENQRY, newvt, True)
    return newvt.tolist()[0]

def getmode(vt):
    vtmode = array.array('b', [0] * struct.calcsize(VtMode.FMT))

    fcntl.ioctl(vt.fileno(), VT_GETMODE, vtmode, True)
    return VtMode(*struct.unpack(VtMode.FMT, vtmode.tobytes()))

def setmode(vt, mode):
    vtmode = array.array('b', struct.pack(VtMode.FMT,
        mode.mode, mode.waitv, mode.relsig, mode.acqsig, mode.frsig
    ))

    fcntl.ioctl(vt.fileno(), VT_SETMODE, vtmode, False)

def getstate(vt):
    vtstat = array.array('b', [0] * struct.calcsize(VtStat.FMT))

    fcntl.ioctl(vt.fileno(), VT_GETSTATE, vtstat, True)
    return VtStat(*struct.unpack(VtStat.FMT, vtstat.tobytes()))

def sendsig(vt, stat):
    vtstat = array.array('b', struct.pack(VtStat.FMT,
        stat.active, stat.signal, stat.state
    ))

    fcntl.ioctl(vt.fileno(), VT_SENDSIG, vtstat, False)

def reldisp(vt, allow):
    fcntl.ioctl(vt.fileno(), VT_RELDISP, VT_ACKACQ if allow else 0, False)

def activate(vt, nr):
    fcntl.ioctl(vt.fileno(), VT_ACTIVATE, nr, False)

def waitactive(vt, nr):
    fcntl.ioctl(vt.fileno(), VT_WAITACTIVE, nr, False)

def disallocate(vt, nr):
    fcntl.ioctl(vt.fileno(), VT_DISALLOCATE, nr, False)

def resize(vt, siz):
    vtsiz = array.array('b', struct.pack(VtSizes.FMT,
        siz.rows, siz.cols, siz.scrollsize
    ))

    fcntl.ioctl(vt.fileno(), VT_RESIZE, vtsiz, False)

def resizex(vt, csiz):
    vtsiz = array.array('b', struct.pack(VtConSiz.FMT,
        csiz.rows, csiz.cols, csiz.scrollsize, csiz.clin, csiz.vcol, csiz.ccol
    ))

    fcntl.ioctl(vt.fileno(), VT_RESIZEX, vtsiz, False)

def gethifontmask(vt):
    hifont = array.array('H', [0])

    fcntl.ioctl(vt.fileno(), VT_GETHIFONTMASK, hifont, True)

    return hifont.tolist()[0]

def waitevent(vt, event):
    vtevent = array.array('b', struct.pack(VtEvent.FMT,
        event, 0, 0, 0, 0, 0, 0
    ))

    fcntl.ioctl(vt.fileno(), VT_WAITEVENT, vtevent, True)

    return VtEvent(*struct.unpack(VtEvent.FMT, vtevent.tobytes()))

def setactivate(vt, nr, mode):
    vtconmode = array.array('b', struct.pack("I" + VtMode.FMT,
        nr, mode.mode, mode.waitv, mode.relsig, mode.acqsig, mode.frsig
    ))

    fcntl.ioctl(vt.fileno(), VT_SETACTIVATE, vtconmode, False)
