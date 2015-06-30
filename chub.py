#!/usr/bin/env leds_python
import sys
import os
import argparse
import curses
import shlex
import subprocess

DESCRIPTION = "Chat on GitHub - AKA CHUB"

DEFAULT_HOST = 'https://github.com/Combatjuan/chub'
VERSION = 0.1

#===============================================================================
def run(command, cwd=None):
	"""
	Runs a command an returns the result code, stdout and stderr.
	The command is a string parseable as a shell command.

	The cwd option (default current directory) causes the command to be run as though from that directory.
	"""
	c = shlex.split(command)
	p = subprocess.Popen(c, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
	return (p.returncode, stdout, stderr)

#===============================================================================
def print_usage(option, opt, value, parser):
	parser.print_help()
	sys.exit(0)

# ==============================================================================
def parse_args():
	parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=False)

	parser.add_argument("-?", "--help", action="help")

	parser.add_argument('host', action='store', nargs=1, default=DEFAULT_HOST,
			help='Chat host to connect to.')

	args = parser.parse_args()

	return args

# ==============================================================================
def begin_chat(host):
	screen = curses.initscr()
	curses.start_color()
	height, width = screen.getmaxyx()
	vcenter = int(height / 2)
	screen.move(vcenter, 2)
	screen.addstr("Welcome to Chub Version {}".format(VERSION))
	screen.move(vcenter + 1, 2)
	screen.addstr("'quit' to quit.")
	return screen

# ==============================================================================
def post(message):
	with open("data/public.room", "a+") as f:
		f.seek(0, os.SEEK_END)
		f.write(' ')

	run("git add data/public.room")
	run("git commit -m '{}'".format(message))
	run("git push")

# ==============================================================================
def clear_prompt(app):
	app.addstr(">")

# ==============================================================================
def chat(host, app):
	input = ''
	height, width = app.getmaxyx()
	app.move(height - 2, 2)
	clear_prompt(app)
	while input != 'quit':
		input = app.getstr(height - 2, 4)
		post(input)

		clear_prompt(app)

# ==============================================================================
def end_chat(host):
	curses.endwin()

# ==============================================================================
def main():
	args = parse_args()
	try:
		app = begin_chat(args.host)
		chat(args.host, app)
	# You do not want to accidentally forget to end your curses sessions.  Leaves a bit mess.
	finally:
		end_chat(args.host)

# ==============================================================================
if __name__ == '__main__':
	main()

