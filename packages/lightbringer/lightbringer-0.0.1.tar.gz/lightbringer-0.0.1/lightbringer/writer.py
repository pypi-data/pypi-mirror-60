from .connection import ReconnectingConnection


class Writer:
	def __init__(self, addr, *, topic, **kwargs):
		host, port = addr.rsplit(':', 1)
		self._server = host, int(port)
		self._topic = topic
		self._args = kwargs

	async def __aenter__(self):
		self._conn = ReconnectingConnection(self._server, **self._args)
		await self._conn.__aenter__()
		return self

	async def __aexit__(self, *args):
		await self._conn.__aexit__(*args)
		del self._conn

	async def pub(self, msg):
		return await self._conn.pub(self._topic, msg)

	async def dpub(self, delay, msg):
		return await self._conn.dpub(self._topic, delay, msg)
