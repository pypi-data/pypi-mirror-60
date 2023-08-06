import threading
import asyncio


class AsyncIOExceptionThread(threading.Thread):
    def __init__ (self, loop):
        threading.Thread.__init__(self)
        self.loop = loop
        self._exc = None

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def stop_thread(self):
        self.loop.call_soon_threadsafe(self.loop.stop)