from concurrent.futures.thread import ThreadPoolExecutor
import threading
import time
from pySmartDL import SmartDL

download_list = ["http://dl2.soft98.ir/soft/m/MKVToolnix.43.0.0.x64.zip?1580074028",
                 "http://dl2.soft98.ir/soft/m/MKVToolnix.43.0.0.x86.zip?1580074028",
                 "http://dl2.soft98.ir/soft/m/MKVToolnix.42.0.0.Portable.exe?1580074028", ]


#
# def download(url):
#     dest = "C:\\Downloads\\junkpy"  # or '~/Downloads/' on linux
#
#     obj = SmartDL(url, progress_bar=False, dest=dest)
#     obj.start()
#
#
# with ThreadPoolExecutor(max_workers=3) as executor:
#     future = executor.submit(download, download_list[0])
#     future = executor.submit(download, download_list[1])
#     future = executor.submit(download, download_list[2])
#     print("All tasks complete")

# def task(n):
#     print("Processing {}".format(n))
#
#
# def main():
#     print("Starting ThreadPoolExecutor")
#     with ThreadPoolExecutor(max_workers=3) as executor:
#         future = executor.submit(task, (2))
#         future = executor.submit(task, (3))
#         future = executor.submit(task, (4))
#     print("All tasks complete")
#


class Counter:
    def __init__(self, workers_count: int):
        self.workers_count = workers_count
        self.pos = []
        for item in range(workers_count):
            self.pos.append(0)

    def update(self, which: int, amount: int):
        self.pos[which] = amount
        print(self.pos)
        print("now = > " + str((sum(self.pos) / self.workers_count)))


class Worker(threading.Thread):
    def __init__(self, url, counter: Counter, which: int):
        super().__init__()
        self.url = url
        self.counter = counter
        self.which = which

    ns = threading.local()

    def run(self):
        dest = "C:\\Users\\Iman\\Desktop\\python\\PyDown\\downloaded\\"  # or '~/Downloads/' on linux
        obj = SmartDL(self.url, progress_bar=False, dest=dest)
        obj.start(blocking=False)
        while not obj.isFinished():
            self.counter.update(self.which, obj.get_progress() * 100)
            time.sleep(1)

        if obj.isSuccessful():
            path = obj.get_dest()
            print("downloaded file to '%s'" % obj.get_dest())
            print("download task took %ss" % obj.get_dl_time(human=True))
            print("File hashes:")
            print(" * MD5: %s" % obj.get_data_hash('md5'))
            print(" * SHA1: %s" % obj.get_data_hash('sha1'))
            print(" * SHA256: %s" % obj.get_data_hash('sha256'))
        else:
            print("There were some errors:")
            for e in obj.get_errors():
                print(str(e))


if __name__ == '__main__':
    counter = Counter(2)
    w1 = Worker(download_list[0], counter, 0)
    w2 = Worker(download_list[1], counter, 1)
    w1.start()
    w2.start()
    w1.join()
    w2.join()
