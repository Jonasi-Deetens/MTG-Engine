# axis3/rules/events/queue.py

from collections import deque
from axis3.rules.events.event import Event


class EventQueue:
    def __init__(self):
        self._queue = deque()

    def push(self, event: Event):
        self._queue.append(event)

    def pop(self) -> Event:
        return self._queue.popleft()

    def is_empty(self) -> bool:
        return not self._queue

    def clear(self):
        self._queue.clear()
