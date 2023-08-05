from __future__ import absolute_import
from enum import Enum

__all__ = ['ProcessState']


class ProcessState(Enum):
    """The possible states that a :class:`Process` can be in."""

    CREATED = 'created'
    RUNNING = 'running'
    WAITING = 'waiting'
    FINISHED = 'finished'
    EXCEPTED = 'excepted'
    KILLED = 'killed'
