from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

import os
import time
import csv
import shutil

class FileChangeHandler(PatternMatchingEventHandler):
    def __init__(self, patterns, copy_path, degs):
        super(FileChangeHandler, self).__init__(patterns=patterns)
        self.copy_path = copy_path
        self.finish = False
        self.degs = degs
        self.index = {}

        for p in patterns:
            self.index[p] = 0

    def on_created(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        # print('%s created' % filename)
        self.copy_file(event.src_path)

    def on_modified(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        # print('%s changed' % filename)
        self.copy_file(event.src_path)

    def on_deleted(self, event):
        # filepath = event.src_path
        # filename = os.path.basename(filepath)
        # print('%s deleted' % filename)
        pass

    def on_moved(self, event):
        # filepath = event.src_path
        # filename = os.path.basename(filepath)
        # print('%s moved' % filename)
        pass

    def copy_file(self, src_path):
        # print("copy")
        if self.index[src_path] < len(degs):
            path_deg = (self.copy_path+'/{:d}'.format(self.degs[self.index[src_path]]))
            if not os.path.exists(path_deg):
                os.makedirs(path_deg)
            
            save_path = path_deg+'/{:s}'.format(os.path.basename(src_path))
            shutil.copyfile(src_path, save_path)

            print("save: {:s}".format(save_path))

            self.index[src_path] += 1

            flag = True
            for v in self.index.values():
                flag = flag and (v >= len(degs))
            self.finish = self.finish or flag

if __name__ == "__main__":
    param = {}

    with open('./parameter.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == 'copy_path':
                param[row[0]] = row[1]
            else:
                param[row[0]] = int(row[1])

    degs = list(range(param['start_deg'], param['end_deg']+1, param['deg_step']))

    print("read parameter.csv")

    with open('./file_path_list.txt') as f:
        file_paths = [l.replace("\n", "") for l in f.readlines()]

    print("read file_path_list.txt")

    f = file_paths[0]

    event_handler = FileChangeHandler(file_paths, param['copy_path'], degs)
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(file_paths[0]), recursive=True)
    observer.start()

    print("watching...")
    
    try:
        while True:
            time.sleep(0.1)
            if event_handler.finish:
                print("finish")
                observer.stop()
                break
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
