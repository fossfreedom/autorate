import rb
import rhythmdb
import time
from gi.repository import GConf

from .AutorateConfigureDialog import AutorateConfigureDialog

gconf_keys = {	'update_rate' : '/apps/rhythmbox/plugins/autorate/update_rate',
		'update_playcount': '/apps/rhythmbox/plugins/autorate/update_playcount',
		'threshold': '/apps/rhythmbox/plugins/autorate/threshold'
		}

class Autorate(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)

	def activate(self, shell):
		print("activating autorate plugin")
		self.db = shell.props.db
		self.current_entry = None
		self.prev_entry = None
		self.max_count = 0
		self.start = 0
		self.prev_elap = 0
		self.state = 'paused'

		self.do_rate = GConf.Client.get_default().get_bool(gconf_keys['update_rate'])
		self.do_pc = GConf.Client.get_default().get_bool(gconf_keys['update_playcount'])
		self.pc_thresh = GConf.Client.get_default().get_float(gconf_keys['threshold'])

		print(self.do_rate)
		print(self.do_pc)
		print(str(self.pc_thresh))

		# Reference the shell player
		sp = shell.props.shell_player

		# bind to "playing-changed" signal
		self.pc_id = sp.connect(
			'playing-changed',
			self.playing_changed
		)

		# bind to "playing-song-changed" signal
		self.psc_id = sp.connect(
			'playing-song-changed',
			self.playing_song_changed
		)

		# bind to "playing-song-property-changed" signal
		self.pspc_id = sp.connect(
			'playing-song-property-changed',
			self.playing_song_property_changed
		)

		# Set current entry if player is playing
		if sp.get_playing():
			self.state = 'playing'
			self.set_entry(sp.get_playing_entry())


	def deactivate(self, shell):
		print("deactivating autorate plugin")
		# Disconnect signals
		sp = shell.props.shell_player
		sp.disconnect(self.psc_id)
		sp.disconnect(self.pc_id)
		sp.disconnect(self.pspc_id)

		# Remove references
		del self.db
		del self.current_entry


	def create_configure_dialog(self, dialog=None):
		if not dialog:
			builder_file = self.find_file("autorate-prefs.ui")
			dialog = AutorateConfigureDialog (builder_file, gconf_keys).get_dialog()
		dialog.present()
		return dialog


	# Player was stopped or started
	def playing_changed(self, sp, playing):
		if playing:
			self.state = 'playing'
			self.start = time.time()
			self.set_entry(sp.get_playing_entry())
		else:
			self.state = 'paused'
			self.prev_elap += time.time() - self.start
#			print "Elapsed before pause: " + str(self.prev_elap)

	# The playing song has changed
	def playing_song_changed(self, sp, entry):
		if sp.get_playing():
#			self.state = 'playing'
			self.set_entry(entry)

	# A property of the playing song has changed
	def playing_song_property_changed(self, sp, uri, property, old, new):
		if sp.get_playing():
			self.get_songinfo_from_entry()

	def calc_maxcount(self):
		self.max_count = 0
		self.db.entry_foreach(self.get_playcount_per_entry)
		print("Max count: " + str(self.max_count))

	def get_playcount_per_entry(self, ent):
		pc = self.get_entry_play_count(ent)
		if pc > self.max_count:
			self.max_count = pc

	# Gets current songinfo from a rhythmdb entry
	def get_songinfo_from_entry(self):
		playcount = self.get_entry_play_count(self.prev_entry)
		if (playcount >= self.max_count):
			self.calc_maxcount()

		rate = self.get_entry_rating(self.prev_entry)
		dur = self.get_entry_duration(self.prev_entry)
		if (rate == -1 and playcount == -1 and dur == -1):
			return
		else:
			self.calc_rating(self.prev_entry, playcount, rate, dur)


	def calc_rating(self, ent, cur_pc, cur_rate, dur):
		if ent is None: return

		new_rate = 0

		if cur_pc <= (self.max_count/6)*6:
			new_rate = 5
		if cur_pc <= (self.max_count/6)*5:
			new_rate = 4
		if cur_pc <= (self.max_count/6)*4:
			new_rate = 3
		if cur_pc <= (self.max_count/6)*3:
			new_rate = 2
		if cur_pc <= (self.max_count/6)*2:
			new_rate = 1
		if cur_pc <= (self.max_count/6)*1:
			new_rate = 0

#		print "Playcount:  " + str(cur_pc) + "/" + str(self.max_count)
#		print "Duration:   " + str(self.prev_elap) + "/" + str(dur)
#		print "Rating: " + str(cur_rate) + "/" + str(float(new_rate))

		if (self.do_pc):
			if ((self.prev_elap / dur) >= self.pc_thresh):
				self.set_play_count(ent, (cur_pc+1))
				self.set_last_played(ent)

		if (self.do_rate):
			if ( float(new_rate) > float(cur_rate) ):
				self.set_rating(ent, new_rate)

		self.prev_elap = 0


	def set_play_count(self, ent, newpc):
		print("Setting play-count to: " + str(newpc))
		self.db.set(ent, rhythmdb.PROP_PLAY_COUNT, newpc)
		return 0


	def set_last_played(self, ent):
		t = time.time()
		print("Setting last-played to: " + str(t))
		self.db.set(ent, rhythmdb.PROP_LAST_PLAYED, int(t))
		return 0


	def set_rating(self, ent, newrt):
		print("Setting rating to: " + str(newrt))
		self.db.set(ent, rhythmdb.PROP_RATING, newrt)
		return 0


	def get_entry_rating(self, ent):
		if ent is None: return -1
		return self.db.entry_get(ent, rhythmdb.PROP_RATING)


	def get_entry_play_count(self, ent):
		if ent is None: return -1
		return self.db.entry_get(ent, rhythmdb.PROP_PLAY_COUNT)

	def get_entry_duration(self, ent):
		if ent is None: return -1
		return self.db.entry_get(ent, rhythmdb.PROP_DURATION)


	# Sets our current RythmDB entry
	def set_entry(self, entry):
		if entry == self.current_entry: return
		if entry is None: return

#		print "Status: " + self.state

		self.prev_entry = self.current_entry
		self.current_entry = entry

		if (self.state == 'paused'):
			print("We were paused: Do not count the current time")
		else:
			self.prev_elap += time.time() - self.start

		print("Elapsed: " + str(self.prev_elap))

		# Extract songinfo from the current entry
		self.get_songinfo_from_entry()

