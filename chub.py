#!/usr/bin/env leds_python
import sys
import os
import argparse
import shlex
import subprocess
import urwid

DESCRIPTION = "Chat on GitHub - AKA CHUB"

DEFAULT_HOST = 'https://github.com/Combatjuan/chub'
VERSION = 0.1

CURRENT_ROOM = 'public'

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

	parser.add_argument('--host', action='store', default=DEFAULT_HOST,
			help='Chat host to connect to.')

	args = parser.parse_args()

	return args

# ==============================================================================
def post(message):
	with open("data/{}.room".format(CURRENT_ROOM), "a+") as f:
		f.seek(0, os.SEEK_END)
		f.write(' ')

	run("git add data/{}.room".format(CURRENT_ROOM))
	run("git commit -m '{}'".format(message))
	# run("git push")

# ==============================================================================
def switch_rooms(room):
	global CURRENT_ROOM
	CURRENT_ROOM = room

# ==============================================================================
def clear_prompt(app):
	height, width = app.getmaxyx()
	app.move(height - 2, 2)
	app.addstr(">")

# ==============================================================================
def get_command_args(command):
	parts = command.split(" ")[1:]
	return parts

# ==============================================================================
def chat(host):
	class ConversationListBox(urwid.ListBox):
		def __init__(self):
			body = urwid.SimpleFocusListWalker([])
			super(ConversationListBox, self).__init__(body)
			self.set_focus_valign(('relative', 100))

			initial_messages = [
				"Welcome to Chub version {}".format(VERSION),
				"Available commands: !quit, !switch <room>",
			]
			for msg in initial_messages:
				self.add_meta_message(msg)

		def add_message(self, msg):
			self.body.append(urwid.Text(('message', msg)))

		def add_meta_message(self, msg):
			self.body.append(urwid.Text(('meta', msg)))

	class MessageEdit(urwid.Edit):
		def __init__(self):
			super(MessageEdit, self).__init__(caption='> ')
			urwid.register_signal(MessageEdit, ['send_message', 'send_meta_message'])

		def keypress(self, size, key):
			key = super(MessageEdit, self).keypress(size, key)
			if key != 'enter':
				return key

			msg = self.edit_text
			if msg == "!quit":
				raise urwid.ExitMainLoop()
			elif msg.startswith("!switch"):
				args = get_command_args(msg)
				switch_rooms(*args)
				urwid.emit_signal(self, 'send_meta_message', 'Switched to room {}.'.format(args[0]))
			else:
				post(msg)
				urwid.emit_signal(self, 'send_message', msg)

			self.set_edit_text('')

	palette = [
		('message', 'default', 'default'),
		('meta', 'dark blue', 'default'),
		('message_field', 'black,bold', 'light gray'),
	]
	conversation = ConversationListBox()
	message_edit = MessageEdit()
	wrapped_edit = urwid.AttrMap(message_edit, 'message_field')

	layout = urwid.Frame(conversation, footer=wrapped_edit, focus_part='footer')

	urwid.connect_signal(message_edit, 'send_message', conversation.add_message)
	urwid.connect_signal(message_edit, 'send_meta_message', conversation.add_meta_message)

	urwid.MainLoop(layout, palette).run()

# ==============================================================================
def main():
	args = parse_args()
	chat(args.host)

# ==============================================================================
if __name__ == '__main__':
	main()

