from queue import Queue as ThreadQueue
from queue import Empty
from multiprocessing import Queue as ProcessQueue
from concurrent.futures import ThreadPoolExecutor, as_completed

import BatchScript.config
import time

class Worker(object):

    func = None
    jobs = None
    executor = None
    results = None
    config = BatchScript.config

    def __init__(self, func, jobs: ThreadQueue, results: ProcessQueue, config=None):
        self.func = func
        self.jobs = jobs
        self.results = results
        if config:
            self.config = config
        self.executor = ThreadPoolExecutor(self.config.MaxThreadPoolSize)

    def start(self):
        while True:
            items = []
            for i in range(self.config.WorkerGetBatchSize):
                try:
                    items.append(self.jobs.get(timeout=self.config.ThreadQueueWaitTimeout))
                except Empty:
                    break
            works = []
            batch_submit = time.time()
            for item in items:
                works.append(self.executor.submit(self.func, item))
            work_results = []
            for work in as_completed(works):
                if self.config.ResultsBatchSize == 0:
                    self.results.put(work.result())
                else:
                    if len(work_results) < self.config.ResultsBatchSize:
                        work_results.append(work.result())
                    else:
                        self.results.put(work_results)
                        work_results = []
            batch_completed = time.time()
            if items:
                job_count = len(items)
                timedelta = batch_completed - batch_submit
                speed = job_count / timedelta
                print("{} batch completed in {} seconds with {} jobs speed {}/s".format(self.func.__name__, timedelta, job_count, speed))

