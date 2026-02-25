import queue
import threading
from typing import Optional, Callable


class TTSQueue:
	def __init__(self, speak_fn: Callable[[str], None]):
		self._q: "queue.Queue[str]" = queue.Queue()
		self._speak = speak_fn
		self._thread: Optional[threading.Thread] = None
		self._running = False

	def start(self):
		if self._thread is not None:
			return
		self._running = True
		self._thread = threading.Thread(target=self._run, daemon=True)
		self._thread.start()

	def stop(self):
		self._running = False
		if self._thread is not None:
			self._thread.join(timeout=3)
			self._thread = None

	def enqueue(self, text: str):
		self._q.put(text)

	def _run(self):
		while self._running:
			try:
				text = self._q.get(timeout=0.2)
			except queue.Empty:
				continue
			try:
				self._speak(text)
			except Exception:
				pass
