import aiohttp
import asyncio
import contextlib

from . import _compat
from .connection import Error
from .connection import ReconnectingConnection


class ReaderConnection(ReconnectingConnection):
	def __init__(self, addr, *, topic, channel, queue, max_in_flight=10, **kwargs):
		super().__init__(addr, **kwargs)
		self._topic = topic
		self._channel = channel
		self._queue = queue
		self._max_in_flight = max_in_flight
		self._subscribed = False

	async def _setup(self):
		await super()._setup()
		await self.sub(self._topic, self._channel, _wait_for_ready=False)
		await self.rdy(self._max_in_flight)
		self._subscribed = True

	async def on_message(self, msg):
		await self._queue.put((msg, None))

	async def on_error(self, exc):
		if not isinstance(exc, Error):
			self._subscribed = False
		await self._queue.put((None, exc))

	async def __aexit__(self, *args):
		if self._subscribed:
			self._subscribed = False
			await self.cls()
		await super().__aexit__(*args)


class DirectConnection(ReaderConnection):
	"""Manages a single direct connection to a nsqd"""

	def __init__(self, addr, *args, **kwargs):
		host, port = addr.rsplit(':', 1)
		super().__init__((host, int(port)), *args, **kwargs)


class Lookup:
	"""Manages the connections to all the producers returned by one lookup server"""

	def __init__(self, addr, topic, refresh_interval, conn_args):
		self._addr = addr
		self._topic = topic
		self._refresh_interval = refresh_interval
		self._conn_args = conn_args

	async def __aenter__(self):
		self._session = aiohttp.ClientSession()
		await self._session.__aenter__()

		self._connections = {}
		await self._refresh()
		coro = self._refresh_periodic()
		self._refresh_task = _compat.create_task(coro)

	async def __aexit__(self, *args):
		self._refresh_task.cancel()
		with contextlib.suppress(asyncio.CancelledError):
			await self._refresh_task
		del self._refresh_task

		await self._session.__aexit__(*args)
		del self._session

		await asyncio.gather(*(c.__aexit__(*args) for c in self._connections.values()))
		del self._connections

	async def _refresh(self):
		async with self._session.get(
			f'{self._addr}/lookup',
			params={'topic': self._topic},
		) as resp:
			if resp.status == 404:
				new = set()
			else:
				resp.raise_for_status()
				r = await resp.json()
				new = {(
					o.get('broadcast_address', o.get('address')),
					o['tcp_port'],
				) for o in r['producers']}

		old = set(self._connections.keys())

		async def remove(addr):
			conn = self._connections.pop(addr)
			await conn.__aexit__(None, None, None)
		async def add(addr):
			conn = ReaderConnection(addr, **self._conn_args)
			await conn.__aenter__()
			self._connections[addr] = conn

		await asyncio.gather(*(
			remove(addr)
			for addr in self._connections
			if addr not in new
		), *(
			add(addr)
			for addr in new
			if addr not in self._connections
		))

	async def _refresh_periodic(self):
		while True:
			await self._refresh()
			await asyncio.sleep(self._refresh_interval)


class Reader:
	def __init__(self, *,
		topic,
		channel,
		nsqd_tcp_addresses=None,
		lookupd_http_addresses=None,
		lookupd_refresh_interval=10, # seconds
		**kwargs,
	):
		self._topic = topic
		self._channel = channel
		self._nsqd_tcp_addresses = nsqd_tcp_addresses or []
		self._lookupd_http_addresses = lookupd_http_addresses or []
		self._lookupd_refresh_interval = lookupd_refresh_interval
		self._conn_args = kwargs

	async def __aenter__(self):
		self._messages = asyncio.Queue()
		self._stack = await _compat.AsyncExitStack().__aenter__()

		conn_args = {
			'topic': self._topic,
			'channel': self._channel,
			'queue': self._messages,
			**self._conn_args
		}

		ctxs = [
			Lookup(a, self._topic, self._lookupd_refresh_interval, conn_args)
			for a in self._lookupd_http_addresses
		] + [
			DirectConnection(a, **conn_args)
			for a in self._nsqd_tcp_addresses
		]
		await asyncio.gather(*(self._stack.enter_async_context(c) for c in ctxs))
		return self

	async def __aexit__(self, *args):
		await self._stack.__aexit__(*args)
		del self._stack
		del self._messages

	async def __aiter__(self):
		while True:
			msg, exc = await self._messages.get()
			if exc is not None:
				raise exc
			else:
				yield msg
