#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Yesudeep Mangalapilly <yesudeep@gmail.com>
# Copyright 2012 Google, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
:module: watchdog.observers.fsevents
:synopsis: FSEvents based emitter implementation.
:author: yesudeep@google.com (Yesudeep Mangalapilly)
:platforms: Mac OS X
"""

from __future__ import with_statement

import sys
import threading
import unicodedata
import _watchdog_fsevents as _fsevents

from watchdog.events import (
    FileDeletedEvent,
    FileModifiedEvent,
    FileCreatedEvent,
    FileMovedEvent,
    DirDeletedEvent,
    DirModifiedEvent,
    DirCreatedEvent,
    DirMovedEvent
)

from .dirsnapshot import DirectorySnapshot
from watchdog.observers.api import (
    BaseObserver,
    EventEmitter,
    DEFAULT_EMITTER_TIMEOUT,
    DEFAULT_OBSERVER_TIMEOUT
)


class FSEventsEmitter(EventEmitter):

    """
    Mac OS X FSEvents Emitter class.

    :param event_queue:
        The event queue to fill with events.
    :param watch:
        A watch object representing the directory to monitor.
    :type watch:
        :class:`watchdog.observers.api.ObservedWatch`
    :param timeout:
        Read events blocking timeout (in seconds).
    :type timeout:
        ``float``
    """

    def __init__(self, event_queue, watch, timeout=DEFAULT_EMITTER_TIMEOUT):
        EventEmitter.__init__(self, event_queue, watch, timeout)
        self._lock = threading.Lock()
        self.snapshot = DirectorySnapshot(watch.path, watch.is_recursive)

    def on_thread_stop(self):
        _fsevents.remove_watch(self.watch)
        _fsevents.stop(self)

    def queue_events(self, timeout):
        with self._lock:
            if not self.watch.is_recursive and self.watch.path not in self.pathnames:
                return
            new_snapshot = DirectorySnapshot(self.watch.path, self.watch.is_recursive)
            events = new_snapshot - self.snapshot
            self.snapshot = new_snapshot

            for _, path_tuple in events.change_list.items():
                for ((src_path, dst_path), e_type) in path_tuple:
                    if e_type == 'CR':
                        self.queue_event(FileCreatedEvent(src_path))
                    elif e_type == 'CR_D':
                        self.queue_event(DirCreatedEvent(src_path))
                    elif e_type == 'MV':
                        self.queue_event(FileMovedEvent(src_path, dst_path))
                    elif e_type == 'MV_D':
                        self.queue_event(DirMovedEvent(src_path, dst_path))
                    elif e_type == 'DL':
                        self.queue_event(FileDeletedEvent(src_path))
                    elif e_type == 'DL_D':
                        self.queue_event(DirDeletedEvent(src_path))
                    elif e_type == 'MD':
                        self.queue_event(FileModifiedEvent(src_path))
                    elif e_type == 'MD_D':
                        self.queue_event(DirModifiedEvent(src_path))

    def run(self):
        try:
            def callback(pathnames, flags, emitter=self):
                emitter.queue_events(emitter.timeout)

            self.pathnames = [self.watch.path]
            _fsevents.add_watch(self, self.watch, callback, self.pathnames)
            _fsevents.read_events(self)
        except:
            pass


class FSEventsObserver(BaseObserver):

    def __init__(self, timeout=DEFAULT_OBSERVER_TIMEOUT):
        BaseObserver.__init__(self, emitter_class=FSEventsEmitter,
                              timeout=timeout)

    def schedule(self, event_handler, path, recursive=False):
        # Python 2/3 compat
        try:
            str_class = unicode
        except NameError:
            str_class = str

        # Fix for issue #26: Trace/BPT error when given a unicode path
        # string. https://github.com/gorakhargosh/watchdog/issues#issue/26
        if isinstance(path, str_class):
            #path = unicode(path, 'utf-8')
            path = unicodedata.normalize('NFC', path)
            # We only encode the path in Python 2 for backwards compatibility.
            # On Python 3 we want the path to stay as unicode if possible for
            # the sake of path matching not having to be rewritten to use the
            # bytes API instead of strings. The _watchdog_fsevent.so code for
            # Python 3 can handle both str and bytes paths, which is why we
            # do not HAVE to encode it with Python 3. The Python 2 code in
            # _watchdog_fsevents.so was not changed for the sake of backwards
            # compatibility.
            if sys.version_info < (3,):
                path = path.encode('utf-8')
        return BaseObserver.schedule(self, event_handler, path, recursive)
