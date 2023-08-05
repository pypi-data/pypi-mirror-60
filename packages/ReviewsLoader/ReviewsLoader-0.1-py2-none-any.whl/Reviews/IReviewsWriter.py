class IRewiewsWriter(object):
    async def write(self, data: dict):
        raise NotImplementedError
    
    def close(self):
        raise NotImplementedError
