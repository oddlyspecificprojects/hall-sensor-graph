from typing import Tuple, Callable
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
QUEUE_COUNT = 5
QUEUE_LENGTH = 500
HEIGHT = 4095
X_DATA = range(QUEUE_LENGTH)
sensor_queues = [collections.deque(np.zeros(QUEUE_LENGTH)) for _ in range(QUEUE_COUNT)]
color_list = 'rgbmy'
segments = len(color_list) * 2 + 1
color_vertical_pos = {c: i + len(color_list) + 2 for i, c in enumerate(color_list)}

fig = plt.figure(figsize=(12, 6))
ax = plt.subplot(1, 1, 1)

ax.set_ylim(0, HEIGHT)


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


def draw_queue(q: collections.deque, color: str):
    ax.plot(X_DATA, q, color)
    min_i, min_v = find_min(q)
    max_i, max_v = find_max(q)
    ax.text(min_i, min_v, min_v, fontsize=12, c=color)
    ax.text(max_i, max_v, max_v, fontsize=12, c=color)
    ax.text(
        0,
        color_vertical_pos.get(color) * HEIGHT // segments,
        sum(q) / QUEUE_LENGTH,
        fontsize=12,
        c=color,
    )


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
            values = [int(v) for v in values if int(v) > 100]
            if len(values) != QUEUE_COUNT:
                continue
            for queue, new_value in zip(sensor_queues, values):
                queue.popleft()
                queue.append(new_value)
        except (UnicodeDecodeError, ValueError) as e:
            print(e)

    ax.cla()
    for q, c in zip(sensor_queues, color_list):
        draw_queue(q, c)
    ax.set_ylim(0, HEIGHT)
    ax.set_autoscale_on(False)


ani = FuncAnimation(fig, frame, interval=130)
plt.show()
