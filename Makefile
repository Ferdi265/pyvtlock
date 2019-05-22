DESTDIR =
PREFIX  = /usr/local
PYTHON_PREFIX = /usr

COMMAND = "$(PYTHON_PREFIX)/bin/python3", "-I", "$(PREFIX)/lib/pyvtlock/main.py"
KEEPENV = "USER", "MOTD", "XDG_VTNR"
DEBUG = 0
OPT = -Os

CC = gcc
CFLAGS = -Wall -Wextra $(OPT) '-DDEBUG=$(DEBUG)' '-DCOMMAND=$(COMMAND)' '-DKEEPENV=$(KEEPENV)' $(EXTRACFLAGS)

all: cap/capwrap cap/captest

cap/capwrap: cap/capwrap.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap

cap/captest: cap/captest.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap

.PHONY: clean install setgid setcap install_setcap
clean:
	rm -f cap/capwrap cap/captest

install: cap/capwrap
	install -D -m 0644 99-pyvtlock-tty63.rules '$(DESTDIR)/$(PREFIX)/lib/udev/rules.d/99-pyvtlock-tty63.rules'
	install -D -g tty -m 2755 cap/capwrap '$(DESTDIR)/$(PREFIX)/lib/pyvtlock/capwrap'
	install -D -m 644 main.py '$(DESTDIR)/$(PREFIX)/lib/pyvtlock/main.py'
	install -D -m 644 vt.py '$(DESTDIR)/$(PREFIX)/lib/pyvtlock/vt.py'
	install -D -m 644 forksignal.py '$(DESTDIR)/$(PREFIX)/lib/pyvtlock/forksignal.py'
	mkdir -p '$(DESTDIR)/$(PREFIX)/bin'
	ln -sf '$(PREFIX)/lib/pyvtlock/capwrap' '$(DESTDIR)/$(PREFIX)/bin/pyvtlock'

setgid: cap/capwrap
	chgrp tty cap/capwrap
	chmod 2755 cap/capwrap

setcap: cap/capwrap
	setcap 'cap_sys_tty_config=ep cap_setgid=ep' cap/capwrap

install_setcap: install
	setcap 'cap_sys_tty_config=ep cap_setgid=ep' '$(DESTDIR)/$(PREFIX)/lib/pyvtlock/capwrap'
