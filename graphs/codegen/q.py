import threading
import queue
import time

message_queue = queue.Queue()


def publish(msg):
    message_queue.put(msg)


def route(msg):
    pass


def consumer():
    while True:
        msg = message_queue.get()
        route(msg)
        message_queue.task_done()


consumer_thread = threading.Thread(target=consumer, daemon=True)
consumer_thread.start()

# message_queue.join()
