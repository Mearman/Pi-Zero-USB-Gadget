#!/usr/bin/python3
# source: https://magpi.raspberrypi.org/articles/pi-zero-w-smart-usb-flash-drive
# https://gist.githubusercontent.com/davidhoness/0f45ef6a41bac6311614f109acbf92db/raw/970badd0ae4b097e3af8d5142e65c34b21f5cfab/usb_share.py

import time
import os
from watchdog.observers import Observer
from watchdog.events import *

CMD_MOUNT = "mount -a; modprobe g_mass_storage file=/piusb.bin stall=0 removable=y"
CMD_UNMOUNT = "modprobe -r g_mass_storage; umount /mnt/usb_share"
CMD_SYNC = "sync"

WATCH_PATH = "/mnt/usb_share"
ACT_EVENTS = [DirDeletedEvent, DirMovedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent]
ACT_TIME_OUT = 30

class DirtyHandler(FileSystemEventHandler):
    def __init__(self):
        self.reset()

    def on_any_event(self, event):
        if type(event) in ACT_EVENTS:
            self._dirty = True
            self._dirty_time = time.time()

    @property
    def dirty(self):
        return self._dirty

    @property
    def dirty_time(self):
        return self._dirty_time

    def reset(self):
        self._dirty = False
        self._dirty_time = 0
        self._path = None


os.system(CMD_MOUNT)

evh = DirtyHandler()
observer = Observer()
observer.schedule(evh, path=WATCH_PATH, recursive=True)
observer.start()

try:
    while True:
        while evh.dirty:
            time_out = time.time() - evh.dirty_time

            if time_out >= ACT_TIME_OUT:
                os.system(CMD_UNMOUNT)
                time.sleep(1)
                os.system(CMD_SYNC)
                time.sleep(1)
                os.system(CMD_MOUNT)
                evh.reset()

            time.sleep(1)

        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()