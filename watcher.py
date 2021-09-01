from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

import os
import time
import csv
import shutil

class FileChangeHandler(PatternMatchingEventHandler):
    def __init__(self, patterns, copy_path, degs, margin_time):
        super(FileChangeHandler, self).__init__(patterns=patterns)
        self.copy_path = copy_path
        self.finish = False
        self.degs = degs
        self.index = {}
        self.old_time = {}
        self.margin_time = margin_time

        for p in patterns:
            self.index[p] = -1
            self.old_time[p] = time.time()

        # time.sleep(1)

    def on_created(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        self.copy_file(event.src_path)

    def on_modified(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        self.copy_file(event.src_path)

    def on_deleted(self, event):
        pass

    def on_moved(self, event):
        pass

    def copy_file(self, src_path):
        if self.index[src_path] < len(self.degs):

            now = time.time()

            is_update = (now - self.old_time[src_path] >= self.margin_time)
            # print(now - self.old_time[src_path])
            self.old_time[src_path] = now

            if is_update:    
                self.index[src_path] += 1

            if self.index[src_path] < len(degs):

                path_deg = (self.copy_path+'/{:d}'.format(self.degs[self.index[src_path]]))
                if not os.path.exists(path_deg):
                    os.makedirs(path_deg)
                
                save_path = path_deg+'/{:s}'.format(os.path.basename(src_path))

                shutil.copyfile(src_path, save_path)

                if is_update:
                    print("save: {:s}".format(save_path))

    def check_finish(self):
        flag = True
        for v in self.index.values():
            flag = flag and (v >= len(degs)-1)
        self.finish = self.finish or flag
        return self.finish

if __name__ == "__main__":

    ###### read parameter.csv ######

    restartFlag = True

    while restartFlag:

        param = {}

        if not os.path.exists('./parameter.csv'):
            print("can't find parameter.csv")
            time.sleep(3)
            exit()

        with open('./parameter.csv') as f:
            reader = csv.reader(f, skipinitialspace=True)
            for row in reader:
                if row[0] == 'copy_path':
                    param[row[0]] = row[1]
                elif row[0] == 'restart':
                    param[row[0]] = int(row[1])
                    restartFlag   =  not (0 == int(row[1]))
                else:
                    param[row[0]] = int(row[1])

        dir_split = param['copy_path'].split('_')
        dir_base = '_'.join(dir_split[:-1])
        dir_number = int(dir_split[-1]) 
        # dir_base = param['copy_path'].split('_')[:-1]
        # print(dir_base)
        # print(dir_number)

        # print('{:02}'.format(dir_number))
        # print('{:02}'.format(111))

        degs = list(range(param['start_deg'], param['end_deg']+1, param['deg_step']))

        if len(degs) < 1:
            print("degree setting is wrong!")
            time.sleep(3)
            exit()

        if param['repeat'] == 1:    
            dist_path = [param['copy_path']]
        elif param['repeat'] > 1:
            dist_path = [param['copy_path'] + '/{:d}'.format(i+1) for i in range(param['repeat'])]
        else:
            print("repeat setting is wrong!")
            time.sleep(3)
            exit()

        if param['check_time'] < 10:
            print("check_time must be at least 10!")
            time.sleep(3)
            exit()

        if param['margin_time'] < 10:
            print("margin_time must be at least 10!")
            time.sleep(3)
            exit()

        if param['finish_wait'] < 10:
            print("finish_wait must be at least 10!")
            time.sleep(3)
            exit()

        print("read parameter.csv")


        ###### read file_path_list.txt ######

        if not os.path.exists('./file_path_list.txt'):
            print("can't find file_path_list.txt")
            time.sleep(3)
            exit()

        with open('./file_path_list.txt') as f:
            file_paths = [l.replace("\n", "") for l in f.readlines()]

        print("read file_path_list.txt")


        ###### watch files ######

        for i in range(param['repeat']):
            event_handler = FileChangeHandler(file_paths, dist_path[i], degs, param['margin_time']/1000)
            observer = Observer()

            observer.schedule(event_handler, os.path.dirname(file_paths[0]), recursive=True)
            
            observer.start()

            print("watching...")

            try:
                while True:
                    time.sleep(param['check_time']/1000)
                    if event_handler.check_finish():
                        time.sleep(param['finish_wait']/1000)
                        if param['repeat'] > 1:
                            print("finish:{:d}".format(i+1))
                        else:
                            print("finish")
                        observer.stop()
                        break
            except KeyboardInterrupt:
                observer.stop()
                exit()
            observer.join()

        if restartFlag:
            with open('./parameter.csv', 'w') as f:
                for key in param:
                    if key == 'copy_path':
                        f.write(key + ',' + dir_base + '_' + '{:02}'.format(dir_number+1) + '\n')
                    else:
                        f.write(key + ',' + str(param[key]) + '\n')