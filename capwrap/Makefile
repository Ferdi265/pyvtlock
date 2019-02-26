COMMAND = "/usr/bin/env", "python3", "/home/yrlf/Programming/py/pyvtlock/main.py"
DEBUG = 0
OPT = -Os

CC = gcc
CFLAGS = -Wall -Wextra $(OPT) '-DDEBUG=$(DEBUG)' '-DCOMMAND=$(COMMAND)' $(EXTRACFLAGS)

all: capwrap captest

capwrap: capwrap.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap
	sudo chown :tty $@
	sudo chmod g+s $@
	sudo setcap "cap_sys_tty_config=ep cap_setgid=ep" $@

captest: captest.c
	$(CC) $(CFLAGS) -o $@ $^ -lcap

.PHONY: clean
clean:
	rm -f capwrap captest
