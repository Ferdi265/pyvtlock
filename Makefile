DESTDIR =
PREFIX = /usr

COMMAND = "$(PREFIX)/bin/python3", "$(PREFIX)/lib/pyvtlock/main.py"
DEBUG = 0
OPT = -Os

CC = gcc
CFLAGS = -Wall -Wextra $(OPT) '-DDEBUG=$(DEBUG)' '-DCOMMAND=$(COMMAND)' $(EXTRACFLAGS)

all: capwrap captest

capwrap/capwrap: capwrap/capwrap.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap

capwrap/captest: capwrap/captest.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap

.PHONY: clean install
clean:
	rm -f capwrap captest

install: capwrap/capwrap
	install -D -m 0644 '$(DESTDIR)$(PREFIX)/lib/udev/rules.d/30-pyvtlock-tty63.rules' 30-pyvtlock-tty63.rules
	install -D -g tty -m 2755 '$(DESTDIR)$(PREFIX)/lib/pyvtlock/capwrap' capwrap/capwrap
	setcap 'cap_sys_tty_config=ep cap_setgid=ep' '$(DESTDIR)$(PREFIX)/lib/pyvtlock/capwrap'
	ln -s '$(PREFIX)/lib/pyvtlock/capwrap' '$(DESTDIR)$(PREFIX)/bin/pyvtlock'
