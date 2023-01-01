from dataclasses import dataclass
from typing import Tuple, Callable
import itertools
from operator import __gt__, __lt__
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from serial import Serial, SerialException
import collections


try:
    p = Serial("/dev/ttyACM0", baudrate=115200, timeout=0)
except:
    p = Serial("/dev/ttyACM1", baudrate=115200, timeout=0)
QUEUE_COUNT = 4
QUEUE_LENGTH = 500
HEIGHT = 4095
X_DATA = range(QUEUE_LENGTH)
color_list = "rgbm"

fig, axs = plt.subplots(1, 1)
# axs = itertools.chain.from_iterable(axs)


def search_algo(
    q: collections.deque, cmp: Callable[[int, int], bool]
) -> Tuple[int, int]:
    target_index = None
    target_value = None
    for i, v in enumerate(q):
        if target_value is None or cmp(target_value, v):
            target_index = i
            target_value = v
    return target_index, target_value


def find_min(q: collections.deque) -> Tuple[int, int]:
    return search_algo(q, __gt__)


def find_max(q: collections.deque) -> Tuple[int, int]:
    return search_algo(q, __lt__)


@dataclass
class LogEntry:
    sensor_value: int
    vcc: int

    def __lt__(self, other):
        return self.sensor_value < other.sensor_value

    def __gt__(self, other):
        return self.sensor_value > other.sensor_value


def parse_log_entry(raw: str) -> LogEntry:
    sensor_value, vcc = raw.split("|")
    return LogEntry(int(sensor_value), int(vcc))


class SesnorLog:
    def __init__(self, ax, color, avg_pos=HEIGHT * 7 / 8, queue_length=QUEUE_LENGTH):
        self._queue = collections.deque(((0, 0),) * queue_length)
        self._ax = ax
        self._color = color
        self._avg_pos = avg_pos

    def push(self, item: LogEntry):
        self._queue.popleft()
        self._queue.append((item.sensor_value, item.vcc))

    def min(self) -> LogEntry:
        return find_min(self._queue)

    def max(self) -> LogEntry:
        return find_max(self._queue)

    def draw(self):
        self._ax.plot(X_DATA, self._queue, self._color)
        min_i, min_v = self.min()
        max_i, max_v = self.max()
        self._ax.text(min_i, min_v[0], min_v, fontsize=12, c=self._color)
        self._ax.text(max_i, max_v[0], max_v, fontsize=12, c=self._color)
        self._ax.text(
            0,
            self._avg_pos,
            sum(i[0] for i in self._queue) / QUEUE_LENGTH,
            fontsize=12,
            c=self._color,
        )
        self._ax.text(
            QUEUE_LENGTH - 20,
            self._avg_pos,
            sum(i[1] for i in self._queue) / QUEUE_LENGTH,
            fontsize=12,
            c="k",
        )
        self._ax.set_ylim(0, HEIGHT)
        self._ax.set_autoscale_on(False)


# sensor_queues = [SesnorLog(ax, c) for ax, c in zip(axs, color_list)]
sensor_queues = [SesnorLog(axs, c) for c in color_list]


def frame(i):
    global p
    try:
        data_lines = p.readlines()
    except SerialException:
        print("DC")
        try:
            try:
                p = Serial("/dev/ttyACM0", baudrate=115200, timeout=0)
            except:
                p = Serial("/dev/ttyACM1", baudrate=115200, timeout=0)
        except:
            return
        data_lines = p.readlines()

    for line in data_lines:
        try:
            line = line.decode("ascii")
            values = line.split(",")
            if len(values) != QUEUE_COUNT:
                continue
            for queue, new_value in zip(sensor_queues, values):
                parsed = parse_log_entry(new_value)
                queue.push(parsed)
        except (UnicodeDecodeError, ValueError) as e:
            print(e)
    axs.cla()
    for q in sensor_queues:
        q.draw()


ani = FuncAnimation(fig, frame, interval=130)
plt.show()
