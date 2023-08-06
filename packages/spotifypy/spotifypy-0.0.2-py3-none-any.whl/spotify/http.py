import aiohttp
import asyncio
import base64
import datetime
import inspect
import signal


BASE_URL = 'https://api.spotify.com/v1'


class Artist:
    def __init__(self, client, data):
        self._client = client
        self._update(data)

    def _update(self, data):
        self.url = data.pop('external_urls')['spotify']
        self.id = data.pop('id')
        self.name = data.pop('name')
        self.type = data.pop('type')
        self.uri = data.pop('uri')

    def __eq__(self, other):
        if not isinstance(other, Artist):
            raise TypeError('other must be of type Artist')

        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name


class Image:
    def __init__(self, data):
        self._update(data)

    def _update(self, data):
        self.dimensions = (data.pop('width'), data.pop('height'))
        self.url = data.pop('url')

    def __str__(self):
        return self.url


class Album:
    def __init__(self, client, data):
        self._client = client
        self._update(data)

    def _update(self, data):
        self.type = data.pop('album_type')
        self.artists = [Artist(self._client, a) for a in data.pop('artists')]
        self.markets = data.pop('available_markets')
        self.url = data.pop('external_urls')['spotify']
        self.id = data.pop('id')
        self.images = [Image(i) for i in data.pop('images')]
        self.name = data.pop('name')
        try:
            y, m, d = data.get('release_date').split('-')
            data.pop('release_date')
            self.release_data = datetime.datetime(year=int(y), month=int(m), day=int(d))
        except ValueError:
            y = data.pop('release_date')
            self.release_data = datetime.datetime(year=int(y), month=1, day=1)
        self.total_tracks = data.pop('total_tracks')
        self.type = data.pop('type')
        self.uri = data.pop('uri')

    def __eq__(self, other):
        if not isinstance(other, Album):
            raise TypeError('other must be of type Album')

        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name


class Time:
    def __init__(self, ms):
        self.milliseconds = ms
        self.seconds_total = ms / 100
        self.minutes_total = self.seconds_total / 60
        self.hours_total = self.seconds_total / 60
        s, ms = divmod(ms, 100)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        self.total = f'{h}:{m}:{s}.{ms}'


class AudioBar:
    def __init__(self, data):
        self._update(data)

    def _update(self, data):
        self.start = data.pop('start')
        self.duration = data.pop('duration')
        self.confidence = data.pop('confidence')


class AudioBeat:
    def __init__(self, data):
        self._update(data)

    def _update(self, data):
        self.start = data.pop('start')
        self.duration = data.pop('duration')
        self.confidence = data.pop('confidence')


class AudioTatum:
    def __init__(self, data):
        self._update(data)

    def _update(self, data):
        self.start = data.pop('start')
        self.duration = data.pop('duration')
        self.confidence = data.pop('confidence')


class AudioSection:
    def __init__(self, data):
        self._update(data)

    def _update(self, data):
        self.start = data.pop('start')
        self.duration = data.pop('duration')
        self.confidence = data.pop('confidence')
        self.loudness = data.pop('loudness')
        self.tempo = data.pop('tempo')
        self.tempo_confidence = data.pop('tempo_confidence')
        self.key = data.pop('key')
        self.key_confidence = data.pop('key_confidence')
        self.mode = data.pop('mode')
        self.mode_confidence = data.pop('mode_confidence')
        self.time_signature = data.pop('time_signature')
        self.time_signature_confidence = data.pop('time_signature_confidence')


class AudioSegment:
    def __init__(self, data):
        self._update(data)

    def _update(self, data):
        self.start = data.pop('start')
        self.duration = data.pop('duration')
        self.confidence = data.pop('confidence')
        self.loudness_start = data.pop('loudness_start')
        self.loudness_max_time = data.pop('loudness_max_time')
        self.loudness_max = data.pop('loudness_max')
        self.pitches = data.pop('pitches')
        self.timbre = data.pop('timbre')


class TrackAnalysisInfo:
    def __init__(self, data):
        self._update(data)

    def _update(self, data):
        self.samples = data.pop('num_samples')
        self.duration = data.pop('duration')
        self.sample_rate = data.pop('analysis_sample_rate')
        self.channels = data.pop('analysis_channels')
        self.fade_in_end = data.pop('end_of_fade_in')
        self.fade_out_start = data.pop('start_of_fade_out')
        self.loudness = data.pop('loudness')
        self.tempo = data.pop('tempo')
        self.tempo_confidence = data.pop('tempo_confidence')
        self.time_signature = data.pop('time_signature')
        self.time_signature_confidence = data.pop('time_signature_confidence')
        self.key = data.pop('key')
        self.key_confidence = data.pop('key_confidence')
        self.mode = data.pop('mode')
        self.mode_confidence = data.pop('mode_confidence')


class AudioAnalysis:
    def __init__(self, client, data):
        self._client = client
        self._update(data)

    def _update(self, data):
        self.bars = [AudioBar(b) for b in data.pop('bars')]
        self.beats = [AudioBeat(b) for b in data.pop('beats')]
        self.tatums = [AudioTatum(b) for b in data.pop('tatums')]
        self.sections = [AudioSection(b) for b in data.pop('sections')]
        self.segments = [AudioSegment(b) for b in data.pop('segments')]
        self.info = TrackAnalysisInfo(data.pop('track'))


class Track:
    def __init__(self, client, data):
        self._client = client
        self._update(data)

    async def audio_analysis(self):
        res = await self._client.get(f'/audio-analysis/{self.id}')
        return AudioAnalysis(self._client, await res.json())

    def _update(self, data):
        self.album = Album(self._client, data.pop('album'))
        self.artists = [Artist(self._client, a) for a in data.pop('artists')]
        self.id = data.pop('id')
        self.name = data.pop('name')
        self.uri = data.pop('uri')
        self.markets = data.pop('available_markets')
        self.disk_number = data.pop('disc_number')
        self.track_number = data.pop('track_number')
        self.explicit = data.pop('explicit')
        self.type = data.pop('type')
        self.duration = Time(data.pop('duration_ms'))
        self.url = data.pop('external_urls')['spotify']

    def __eq__(self, other):
        if not isinstance(other, Track):
            raise TypeError('other must be of type Track')

        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Track name={self.name} artists={"[" + ", ".join(x.name for x in self.artists) + "]"}>'


class SpotifyClient:
    def __init__(self, client_id, client_secret, loop=None):
        self._id = client_id
        self._secret = client_secret
        self._auth = base64.b64encode(f'{self._id}:{self._secret}'.encode('utf8'))
        self._access_token = None
        self._client = aiohttp.ClientSession()
        self._auth_headers = {
            'Authorization': f'Basic {self._auth.decode("utf8")}'
        }
        self._headers = {}
        self.loop = asyncio.get_event_loop() if loop is None else loop
        if loop is None:
            self.loop.add_signal_handler(signal.SIGINT, lambda: self.close())
            self.loop.add_signal_handler(signal.SIGTERM, lambda: self.close())

    def close(self):
        self.loop.stop()

    async def _new_token(self):
        res = await self._client.post(
            f'https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'client_credentials'
            },
            headers=self._auth_headers
        )

        data = await res.json()
        res.raise_for_status()

        self._access_token = data['access_token']
        self._headers = {
            'Authorization': f'Bearer {self._access_token}'
        }

    async def _try_again(self, method):
        if not inspect.iscoroutine(method):
            raise Exception('Provided method is not a coroutine')

        await self._new_token()

        return await method

    async def get(self, endpoint):
        res = await self._client.get(f'{BASE_URL}{endpoint}', headers=self._headers)

        s = res.headers.get('Retry-After')
        if s:
            await asyncio.sleep(int(s))
            return await self._try_again(self.get(endpoint))

        d = await res.json()
        if 'error' in d:
            if d['error']['status'] == 401:
                return await self._try_again(self.get(endpoint))
        return res

    async def fetch_track(self, *, name=None, track_id=None):
        """
        If given name, fuzzy search and return first result
        """
        if name is not None and track_id is not None:
            raise Exception('Only one of name and track_id should be provided')
        if name is None and track_id is None:
            raise Exception('Must provide either name or track_id')
        if name == '' or track_id == '':
            raise Exception('Name nor track_id can be an empty string')

        if name is not None:
            res = await self.get(f'/search?q={"+".join(name.split(" "))}&type=track&limit=1')
            tracks = [Track(self, t) for t in (await res.json())['tracks']['items']]
            return tracks[0]

        res = await self.get(f'/tracks/{track_id}')
        return Track(self, await res.json())
