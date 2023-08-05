import asyncio

# We swap to correct binary based on platform
import distutils.util
platform = distutils.util.get_platform()
if platform.startswith("macosx"):
	print("LOADING FOR MACOSX")
	import uws.macosx.uwebsocketspy as uwebsocketspy
elif platform.startswith("linux"):
	print("LOADING FOR LINUX")
	import uws.linux.uwebsocketspy as uwebsocketspy
else:
	print("µWebSockets.py is only compatible with Linux and macOS systems running at 64-bit")

# We expose our own event loop for use with asyncio
class Loop(asyncio.SelectorEventLoop):
	def __init__(self):
		self.selector = uwebsocketspy.Selector()
		super().__init__(self.selector)
	def call_soon(self, *args, **kwargs):
		self.selector.tick();
		return super().call_soon(*args, **kwargs);
	def call_at(self, *args, **kwargs):
		self.selector.tick();
		return super().call_at(*args, **kwargs);

App = uwebsocketspy.App
