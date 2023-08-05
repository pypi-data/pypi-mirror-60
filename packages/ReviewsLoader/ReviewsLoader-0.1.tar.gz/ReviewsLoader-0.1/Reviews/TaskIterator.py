class TaskIterator(object):
    STEP_SIZE = 10
    
    def __init__(self, func, batch_size=2000):
        assert batch_size % self.STEP_SIZE == 0
        self.batch_size = batch_size
        self.offset = 0
        self.batch_offset = 0
        self.func = func
        self.complete = False
        self.backlog = list()

    def __iter__(self):
        return self

    def __next__(self):
        if self.complete:
            if self.backlog:
                return self.get_backlog()
            raise StopIteration
        tasks = list()
        while self.offset < (self.batch_offset + self.batch_size):
            tasks.append(self.func(
                offset=self.offset,
                complete_callback=self.complete_callback,
                backlog_callback=self.backlog_callback    
            ))
            self.offset += self.STEP_SIZE
        self.batch_offset += self.batch_size
        return tasks

    def complete_callback(self):
        """
        Call from task if it is last reviews batch
        """
        self.complete = True
        
    def backlog_callback(self, offset):
        """
        Call from task if errors occurred in it and you want to repeat the download
        """
        self.backlog.append(offset)
        
    def get_backlog(self):
        current_backlog = self.backlog[0:self.batch_size]
        del self.backlog[0:self.batch_size]
        return list(map(
            lambda offset:
            self.func(
                offset=offset,
                complete_callback=self.complete_callback,
                backlog_callback=self.backlog_callback
            ),
            current_backlog
        ))