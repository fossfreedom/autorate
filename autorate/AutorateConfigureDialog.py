# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*-
#
# Copyright (C) 2009 John Daiker
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# The Rhythmbox authors hereby grant permission for non-GPL compatible
# GStreamer plugins to be used and distributed together with GStreamer
# and Rhythmbox. This permission is above and beyond the permissions granted
# by the GPL license by which Rhythmbox is covered. If you modify this code
# you may extend this exception to your version of the code, but you are not
# obligated to do so. If you do not wish to do so, delete this exception
# statement from your version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.


from gi.repository import GConf, Gtk, GObject
from os import system, path

class AutorateConfigureDialog (object):
	def __init__(self, builder_file, gconf_keys):
		self.gconf = GConf.Client.get_default()
		self.gconf_keys = gconf_keys

		builder = Gtk.Builder()
		builder.add_from_file(builder_file)
			
		self.dialog = builder.get_object("preferences_dialog")

		self.update_rate = builder.get_object("update_rate")
		self.update_playcount = builder.get_object("update_playcount")
		self.threshold = builder.get_object("threshold")

		self.threshold.set_range(0.00, 1.00)
		self.threshold.set_increments(0.01, 0.05)

#		self.choose_button.connect("clicked", self.choose_callback)
		self.dialog.connect("response", self.dialog_response)

		(rate, playcount, thre) = self.get_prefs_new()
		self.update_rate.set_active(rate)
		self.update_playcount.set_active(playcount)
		self.threshold.set_value(thre)


	def dialog_response(self, dialog, response):
		if response == Gtk.ResponseType.OK:
			self.set_values()
			self.dialog.hide()
		elif response == Gtk.ResponseType.CANCEL or response == Gtk.ResponseType.DELETE_EVENT:
			self.dialog.hide()
		else:
			print("unexpected response type")


	def set_values(self):
		rate = False
		playcount = False
		thre = 0.00
		if self.update_rate.get_active():
			rate = True

		if self.update_playcount.get_active():
			playcount = True

		thre = self.threshold.get_value()

		self.GConf.set_bool(self.gconf_keys['update_rate'], rate)
		self.GConf.set_bool(self.gconf_keys['update_playcount'], playcount)
		self.GConf.set_float(self.gconf_keys['threshold'], thre)

	def choose_callback(self, widget):
		def response_handler(widget, response):
			if response == Gtk.ResponseType.OK:
				path = self.chooser.get_filename()
				self.chooser.destroy()
				self.path_display.set_text(path)
			else:
				self.chooser.destroy()

		buttons = (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE,
				Gtk.STOCK_OK, Gtk.ResponseType.OK)
		self.chooser = Gtk.FileChooserDialog(title=_("Choose lyrics folder..."),
					parent=None,
					action=Gtk.FileChooserAction.SELECT_FOLDER,
					buttons=buttons)
		self.chooser.connect("response", response_handler)
		self.chooser.set_modal(True)
		self.chooser.set_transient_for(self.dialog)
		self.chooser.present()

	def get_dialog (self):
		return self.dialog
	

	def get_prefs_new (self):
		rt = GConf.Client.get_default().get_bool(self.gconf_keys['update_rate'])
		if rt is None:
			rt = True

		pc = GConf.Client.get_default().get_bool(self.gconf_keys['update_playcount'])
		if pc is None:
			pc = True

		th = GConf.Client.get_default().get_float(self.gconf_keys['threshold'])
		if th is None:
			th = 0.80

		return (rt, pc, th)

