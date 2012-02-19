"""
Zeitgeist base code to register mpris2 playing information.

Thanks to: http://milky.manishsinha.net/2010/11/27/zeitgeist-daemon-extensions-explained/
Require:
https://github.com/hugosenari/mpris2 and https://github.com/hugosenari/pydbusdecorator

Install it at:
$HOME/.local/share/zeitgeist/extensions/
"""
#my mpris2 lib
from mpris2 import Player
from mpris2.interfaces import Interfaces
from mpris2.types import Metadata_Map
from mpris2.utils import get_session
#zeitgeist lib
from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Interpretation, Manifestation, Subject

class Mpris2Source(object):
	def __init__ (self, bus_name,
		      app_uri,
		      app_name=None,
		      app_description=None,
		      event_template=None,
		      minetype="audio/mpeg",
		      interpretation=Interpretation.AUDIO,
		      storage="local"):
		"""
		Constructor
		Values that are used to create event and subject can be changed by direct access overriding functions
		ie:
		def register_media_event(media, interpretation, *args, **kw):
			self.minetype = self.your_function_to_know_this(media)
			self.interpretation = self.your_function_to_know_this_too(media)
			self.storage = self.your_function_to_know_this_too_again(media)
			super(YourExentionName, self).register_media_event(media, interpretation, *args, **kw)
		
		:param bus_name: mpris2 player uri
		:param app_uri: application uri for zeitgeist
		:param app_name: application name
		:param app_description: application description
		:param event_template: event template for zeitgeist
		:param minetype: default minetype since this code don't know to get it for each media
		:param interpretation: default subject interpretation, default value is zeitgeist.datamodel.Interpretation.AUDIO
		:param storage: default subject storage since this code don't know to get it for each media
		"""
		self.playing = None
		self.player = Player(dbus_uri=bus_name)
		self.app_uri = app_uri
		self.minetype = minetype
		self.interpretation = interpretation
		self.storage = storage
		self.client = None

		def _handler(*args, **kw):
			#when extension is loading there is no Zeitgeist to connect
			#then try to connect after when song changes
			if not self.client:
				self.client = self._get_client(bus_name,
								app_uri,
								app_name,
								app_description,
								event_template)

			if self.client:
				self.property_changed(*args, **kw)

		session = get_session()
		session.add_signal_receiver(
			_handler,
			Interfaces.SIGNAL,
			Interfaces.PROPERTIES,
			bus_name=bus_name,
			path=Interfaces.OBJECT_PATH)

	def property_changed(*args, **kw):
		""" Callback for mpris2 property change
		With *args and **kw, that player pass from signal org.freedesktop.DBus.Properties.PropertiesChanged
		
		
		:param *args: *args from property_changed (player mpris signal)
		:param **kw: **kw from property_changed (player mpris signal)
		"""
		now_playing = kw.get("now_playing", player.Metadata)
		if self.playing and \
			now_playing and \
			self.playing.get(Metadata_Map.TRACKID) == \
				now_playing.get(Metadata_Map.TRACKID):
			return self.register_same_media_event(now_playing, *args, **kw)

		if now_playing:
			#register leave if has previous media as playing
			if self.playing:
				self.register_previous_event(self.playing, *args, **kw)
			#register new media as playing
			self.register_now_playing_event(now_playing, *args, **kw)
			#override playing with new media
			self.playing = playing

	def register_same_media_event(media, *args, **kw):
		""" Called when property changed but the song is the same,
		Now it is doing nothing but you can override it to register one event calling
		self.register_media_event(media, event_interpretation, *args, **kw)
		
		:param media: mpris2.types.Metadata_Map, media metadata
		:param *args: *args from property_changed (player mpris signal)
		:param **kw: **kw from property_changed (player mpris signal)
		"""
		pass

	def register_now_playing_event(media, *args, **kw):
		""" Called when has new media to be registered as "ACCESS_EVENT",
		this is when media starts.
		You can override it and register one event calling:
		self.register_media_event(media, event_interpretation, *args, **kw)
		
		:param media: mpris2.types.Metadata_Map, media metadata
		:param *args: *args from property_changed (player mpris signal)
		:param **kw: **kw from property_changed (player mpris signal)
		"""
		self.register_media_event(media, Interpretation.EVENT_INTERPRETATION.ACCESS_EVENT, *args, **kw)

	def register_previous_event(media, *args, **kw):
		""" Called when has previous media to be registered as "LEAVE_EVENT", 
		this is when media stops (only when is has new song to play not when stops)
		You can override it and register one event calling:
		self.register_media_event(media, event_interpretation, *args, **kw)
		
		:param media: mpris2.types.Metadata_Map, media metadata
		:param *args: *args from property_changed (player mpris signal)
		:param **kw: **kw from property_changed (player mpris signal)
		"""
		self.register_media_event(media, Interpretation.EVENT_INTERPRETATION.LEAVE_EVENT, *args, **kw)

	def register_media_event(media, interpretation, *args, **kw):
		""" Called as last in line to register event.
		This function was designed to not require overrided
		
		:param media: mpris2.types.Metadata_Map, media metadata
		:param interpretation: event interpretation
		:param *args: *args from property_changed (player mpris signal)
		:param event: to override event to be registered
		:param subject: to override subject of event to be registered
		:param actor: event actor, default is self.app_uri
		:param event_interpretation:  event interpretation, default is interpretation param
		:param event_manifestation: event manifestation, default is Manifestation.SCHEDULED_ACTIVITY
		:param subject_interpretation: subject interpretation, default is self.interpretation
		:param uri: media uri, default is media Metadata_Map.URL
		:param origin: media folder uri, default is media Metadata_Map.URL without filename
		:param minetype: minetype of media, deafult is self.minetype
		:param text: register description, default is track - title - artist - album
		:param storage: storage of media, defaul is self.storage
		"""
		#subject
		subject_values = kw.get("subject_values", {
			"interpretation" : kw.get("subject_interpretation", self.interpretation), #FIXME get information from file
			"manifestation" : kw.get("subject_manifestation", Manifestation.FILE_DATA_OBJECT),
			"uri" : kw.get("uri", media.get(Metadata_Map.URL)),
			"current_uri" : kw.get("current_uri", media.get(Metadata_Map.URL)),
			"origin" : kw.get("origin", media.get(Metadata_Map.URL, "").replace(".\/+", "\/")),
			"mimetype" : kw.get("mimetype", self.minetype), #FIXME get information from file
			"text" : kw.get("text", "%s - %s - %s - %s" % (
					media.get(Metadata_Map.TRACK_NUMBER, ""),
					media.get(Metadata_Map.TITLE, ""),
					media.get(Metadata_Map.ARTIST, ""),
					media.get(Metadata_Map.ALBUM, ""))),
			"storage": kw.get("storage", self.storage), #FIXME get information from file
		})
		subject = kw.get("subject", Subject.new_for_values(**subject_values))
		#event
		event_values = kw.get("event_values", {
			"actor" : kw.get("actor", self.app_uri),
			"interpretation": kw.get("event_interpretation", interpretation),
			"manifestation": kw.get("event_manifestation", Manifestation.EVENT_MANIFESTATION.SCHEDULED_ACTIVITY),
		})
		event = kw.get("event", Event.new_for_values(**event_values))
		event.append_subject(subject)
		#send this to zeitgeist
		self.client.insert_event(event)

	def _get_client(self, bus_name, app_uri, app_name, app_description,
				event_template):
		client = None
		try:
			client = ZeitgeistClient()
			if hasattr(self.client, "register_data_source"):
				client.register_data_source(
					bus_name,
					app_name or bus_name,
					app_description or bus_name,
					event_template or \
					[Event.new_for_values(actor=app_uri)])
		except:
			pass
		return client
