# pyvtlock

pyvtlock is a simple and minimalistic replacement for the vlock-original console
locking program.

It is mostly implemented in python instead of C and uses
[python-pam](https://pypi.org/project/python-pam/) to check the user's password.

Disclaimer: This project came into existance since vlock-original stopped
working on my ArchLinux system with the 2019 update of pambase. It is therefore
quite hastily developed, and a little hacky: YMMV.

# Features

- Switches to a different VT to display the lock screen in order to also work
  on an X or Wayland desktop.
- Displays a customizable lock screen message before each login try.
- Optionally forks into the background: the parent process exits as soon as the
  screen is fully locked, the child exits when the screen is unlocked (`--fork`)
- Optionally prints the PID of the locker process or writes it to a file (`--pid`
  and `--pidfile`)
- Gracefully unlocks when killed via SIGINT, SIGTERM, and SIGHUP

# Notable differences from vlock-original

- Doesn't run as root (Runs as the group `tty`, with a udev rule giving that
  group read privileges to `/dev/tty63`)
- Cannot login via the root password when the user password is wrong
  (intentional, since most modern systems have the root user only accessible via
  sudo)
- Always switches to terminal `/dev/tty63` instead of a dynamically allocated
  one (out of necessity, since the `tty` group is not allowed to read from ttys)

# Security details

The VT switching and locking is implemented via the Linux capability
`CAP_SYS_TTY_CONFIG`, and setting the group `tty` as an additional supplementary
group is done via `CAP_SETGID`.

The `tty` group is also given permission to write to `/dev/tty63` via a udev
rule.

These two capabilities are given to `/usr/lib/pyvtlock/capwrap`, which passes
the first on to the python interpreter via _ambient capabilities_, and drops the
latter capability after adding `tty` to the list of supplementary groups.

This means that in the worst case (assuming `/usr/lib/pyvtlock/capwrap` has no
vulnerabilities), the `tty` group and `CAP_SYS_TTY_CONFIG` capability will be
accessible to any attacker on the system if they can trick the python
interpreter into executing an arbitrary command.

Note that you can escape from `pyvtlock` using the Magic SysRq key combination
`Alt+SysRq+k`. You can work around this by disabling keyboard control SysRqs
(bit '4' of the `kernel.sysrq` sysctl bitmask). This also disallows the use of
`Alt+SysRq+r`, breaking the `r` in the popular Emergency Reboot sequence
`reisub`.
