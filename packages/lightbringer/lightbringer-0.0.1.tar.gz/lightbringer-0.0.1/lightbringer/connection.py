import asyncio
import contextlib
import datetime
import json
import logging
import re
import socket
import struct

from . import _compat


logger = logging.getLogger(__name__)
mitm_logger = logging.getLogger(__name__ + '.mitm')

class ReadTask:
	def __init__(self, reader, on_message, on_response, on_error, on_connection_drop):
		self.reader = reader
		self.on_error = on_error
		self.on_message = on_message
		self.on_response = on_response
		self.on_connection_drop = on_connection_drop

		self.task = _compat.create_task(self.run_safe())

	async def run(self):
		re = self.reader.readexactly
		while True:
			sizeb = await re(4)
			size, = struct.unpack('>l', sizeb)

			ftb = await re(4)
			ft, = struct.unpack('>l', ftb)

			data = await re(size - 4)
			mitm_logger.debug('Read: %r', sizeb + ftb + data)

			if ft == 0:
				await self.on_response(data)
			elif ft == 1:
				raise Error(data.decode('utf-8'))
			elif ft == 2:
				await self.on_message(data)
			else: # pragma: no cover
				raise NotImplementedError()

	async def run_safe(self):
		while True:
			try:
				await self.run()
			except asyncio.CancelledError as exc:
				return
			except asyncio.IncompleteReadError:
				self.on_connection_drop()
				return
			except Error as exc:
				await self.on_error(exc)
			except Exception as exc:
				logger.critical(f'Read task failed: {exc!r}', exc_info=True)
				await self.on_error(exc)
				return # not restarting the task - no idea what the state of the reader looks like

	async def cancel(self):
		self.task.cancel()
		await self.task
		del self.task


class Connection:
	def __init__(self, addr, identify_opts=None):
		self._addr = addr

		identify_opts = identify_opts or {}
		identify_opts['feature_negotiation'] = False
		identify_opts.setdefault('user_agent', 'lightbringer')
		hostname = socket.gethostname()
		identify_opts.setdefault('client_id', hostname)
		identify_opts.setdefault('hostname', hostname.split('.', 1)[0])
		self._identify_body = json.dumps(identify_opts).encode('utf-8')

	async def __aenter__(self):
		self._cmd_lock = asyncio.Lock()
		self._ready = asyncio.Event()
		try:
			await self._setup()
		except Exception:
			await self._cleanup()
			raise
		self._ready.set()
		return self

	async def __aexit__(self, *_):
		self.is_closing = True
		await self._cleanup()
		del self._ready

	async def _setup(self):
		self._reader, self._writer = await asyncio.open_connection(*self._addr)

		self._read_task = ReadTask(
			self._reader,
			self._on_message,
			self._on_response,
			self._on_error,
			self._on_connection_drop,
		)

		self._writer.write(b'  V2')
		await self._ack_cmd('IDENTIFY', body=self._identify_body, _wait_for_ready=False)

		self.is_closing = False

	async def _cleanup(self):
		self._ready = asyncio.Event()

		if hasattr(self, '_read_task'):
			t = self._read_task
			del self._read_task
			await t.cancel()

		if hasattr(self, '_conn_drop_task'):
			t = self._conn_drop_task
			del self._conn_drop_task
			t.cancel()
			with contextlib.suppress(asyncio.CancelledError):
				await t

		if hasattr(self, '_writer'):
			w = self._writer
			del self._writer
			del self._reader
			w.close()
			# todo py3.7
			#await w.wait_closed()

	async def _cmd(self, cmd, body=None):
		msg = cmd.encode('utf-8') + b'\n'
		if body:
			msg += struct.pack('>l', len(body)) + body
		mitm_logger.debug('Write: %r', msg)
		self._writer.write(msg)
		await self._writer.drain()

	async def _ack_cmd(self, *args, expected=b'OK', _wait_for_ready=True, **kwargs):
		if _wait_for_ready:
			await self._ready.wait()
		async with self._cmd_lock:
			self._response_fut = fut = asyncio.get_event_loop().create_future()
			await self._cmd(*args, **kwargs)
			res = await fut
			if res != expected:
				raise Error(f'Unexpected response from the nsqd: expected {expected}, got {res}')

	async def _on_message(self, data):
		msg = Message(self, data)
		await self.on_message(msg)

	async def on_message(self, msg): # pragma: no cover
		raise NotImplementedError()

	async def on_error(self, msg): # pragma: no cover
		raise NotImplementedError()

	async def _on_response(self, data):
		if data == b'_heartbeat_':
			await self.nop()
		else:
			self._response_fut.set_result(data)
			del self._response_fut

	async def _on_error(self, exc):
		if hasattr(self, '_response_fut'):
			self._response_fut.set_exception(exc)
			del self._response_fut
		else:
			await self.on_error(exc)

	def _on_connection_drop(self):
		self._conn_drop_task = _compat.create_task(self.on_connection_drop())

	async def on_connection_drop(self):
		logger.debug('Connection dropped %s', self)
		if hasattr(self, '_response_fut'):
			self._response_fut.set_exception(ConnectionDropped())
			del self._response_fut

	async def sub(self, topic, channel, **kwargs):
		validate_topic_name(topic)
		await self._ack_cmd(f'SUB {topic} {channel}', **kwargs)

	async def pub(self, topic, body):
		validate_topic_name(topic)
		await self._ack_cmd(f'PUB {topic}', body=body)

	async def dpub(self, topic, delay, body):
		validate_topic_name(topic)
		await self._ack_cmd(f'DPUB {topic} {delay}', body=body)

	async def rdy(self, count):
		await self._cmd(f'RDY {count}')

	async def fin(self, mid):
		await self._cmd(f'FIN {mid}')

	async def req(self, mid, timeout):
		await self._cmd(f'REQ {mid} {timeout}')

	async def touch(self, mid):
		await self._cmd(f'TOUCH {mid}')

	async def cls(self):
		await self._ack_cmd('CLS', expected=b'CLOSE_WAIT')

	async def nop(self):
		await self._cmd('NOP')


class ReconnectingConnection(Connection):
	async def on_connection_drop(self):
		await super().on_connection_drop()
		logger.debug('Connection dropped, reconnecting in .5 second')
		await self._cleanup()
		# todo: exponential backoff
		await asyncio.sleep(.5)
		await self.__aenter__()


class Error(Exception):
	pass


class InvalidTopicName(Error):
	pass


class ConnectionDropped(Error):
	pass


class Message:
	def __init__(self, connection, data):
		self._connection = connection

		ts, = struct.unpack('>q', data[:8])
		self.ts = datetime.datetime.fromtimestamp(ts / 1000 / 1000 / 1000, tz=datetime.timezone.utc)

		self.attempts, = struct.unpack('>h', data[8:10])

		self.mid = data[10:26].decode('utf-8')

		self.body = data[26:]

	async def touch(self):
		await self._connection.touch(self.mid)

	async def fin(self):
		await self._connection.fin(self.mid)

	async def req(self, timeout=0):
		await self._connection.req(self.mid, timeout)

	@property
	def nsqd_host(self):
		return '{}:{}'.format(*self._connection._addr)

	def __repr__(self):
		return f'<lightbringer.Message mid:{self.mid}, ts:{self.ts.isoformat()}, attempts:{self.attempts} body:{self.body}>'


def validate_topic_name(name):
	if len(name) >= 65:
		raise InvalidTopicName()
	if not re.match(r'^[\.a-zA-Z0-9_-]+(#ephemeral)?$', name):
		raise InvalidTopicName()
