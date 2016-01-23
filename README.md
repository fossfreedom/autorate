A Rhythmbox Auto-Rating plugin

This was hidden away as a patch in bugzilla but never accepted

 - https://bugzilla.gnome.org/show_bug.cgi?id=494370
 
 Uploaded to GitHub for everyone to peruse.
 
 N.B. Shouldnt be that hard to rework this to python3 and RB 3.0+ standards

"This is my auto rating patch.  It's a python plugin, and is currently coded to do the following:
Automatically rate based on that songs play-count vs the highest played file.
  Ratings are assigned based on 1/6th of the highest play-count.
  If, for instance, the highest played file in the library has been played 60 times:
    When a song has been played 0-10 times, it receives a 0 rating.
    When a song has been played 11-20 times, it gets a 1 rating.
    21-30 times, it gets a 2 rating.
    31-40: 3
    41-50: 4
    51-60: 5
    If a song is already rated higher than what the automatic rating would be, the rating is not changed.

Increase the play-count (and set the last-played) if the file has been played through a certain (user-definable) percentage.  This defaults to 80%.

Both (play-count/last-played) and (auto-rate) can be disabled.

Caveats:
The play/pause button works in the sense that if a song is played, then paused, then played through the 'threshold', then the play-count will update.

Seeking does not work.  eg: seeking to 90% through a song won't increase the play-count or last-played time.  (Don't know how to fix this... maybe connect to a 'seeking' signal somewhere?)

The plugin must be 'configured' before the rating/playcount increase will happen.  (I know how to fix this, but haven't gotten around to it yet).

If settings are changed while the plugin is active, it must be disabled and enabled again for the new settings to take place. (Don't know how to fix this just yet, but I have an idea).

Comments, suggestions, and otherwise are welcome and appreciated."
