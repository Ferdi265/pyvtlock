DESTDIR =
PREFIX = /usr

COMMAND = "$(PREFIX)/bin/python3", "$(PREFIX)/lib/pyvtlock/main.py"
DEBUG = 0
OPT = -Os

CC = gcc
CFLAGS = -Wall -Wextra $(OPT) '-DDEBUG=$(DEBUG)' '-DCOMMAND=$(COMMAND)' $(EXTRACFLAGS)

all: cap/capwrap cap/captest

cap/capwrap: cap/capwrap.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap

cap/captest: cap/captest.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap

.PHONY: clean install
clean:
	rm -f cap/capwrap cap/captest

install: cap/capwrap
	install -D -m 0644 30-pyvtlock-tty63.rules '$(DESTDIR)$(PREFIX)/lib/udev/rules.d/30-pyvtlock-tty63.rules'
	install -D -g tty -m 2755 cap/capwrap '$(DESTDIR)$(PREFIX)/lib/pyvtlock/capwrap'
	setcap 'cap_sys_tty_config=ep cap_setgid=ep' '$(DESTDIR)$(PREFIX)/lib/pyvtlock/capwrap'
	mkdir -p '$(DESTDIR)$(PREFIX)/bin'
	ln -s '$(PREFIX)/lib/pyvtlock/capwrap' '$(DESTDIR)$(PREFIX)/bin/pyvtlock'
