DESTDIR =

COMMAND = "/usr/bin/python3", "/usr/lib/pyvtlock/main.py"
DEBUG = 0
OPT = -Os

CC = gcc
CFLAGS = -Wall -Wextra $(OPT) '-DDEBUG=$(DEBUG)' '-DCOMMAND=$(COMMAND)' $(EXTRACFLAGS)

all: cap/capwrap cap/captest

cap/capwrap: cap/capwrap.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap

cap/captest: cap/captest.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap

.PHONY: clean install setcap
clean:
	rm -f cap/capwrap cap/captest

install: cap/capwrap
	install -D -m 0644 30-pyvtlock-tty63.rules '$(DESTDIR)/usr/lib/udev/rules.d/30-pyvtlock-tty63.rules'
	install -D -g tty -m 2755 cap/capwrap '$(DESTDIR)/usr/lib/pyvtlock/capwrap'
	install -D -m 644 main.py '$(DESTDIR)/usr/lib/pyvtlock/main.py'
	install -D -m 644 vt.py '$(DESTDIR)/usr/lib/pyvtlock/vt.py'
	mkdir -p '$(DESTDIR)/usr/bin'
	ln -s '/usr/lib/pyvtlock/capwrap' '$(DESTDIR)/usr/bin/pyvtlock'

setcap:
	setcap 'cap_sys_tty_config=ep cap_setgid=ep' '$(DESTDIR)/usr/lib/pyvtlock/capwrap'
