import csv

from aioify import aioify

from .IReviewsWriter import IRewiewsWriter


class CSVRewiewsWriter(IRewiewsWriter):
    def __init__(self, filename, fields):
        self.file = open(filename, mode='w')
        writer = csv.DictWriter(self.file, fieldnames=fields)
        writer.writeheader()
        self.aiowriter = aioify(obj=writer, name='aiowriter')
    
    async def write(self, data: dict):
        await self.aiowriter.writerow(data)
        
    def close(self):
        close(self.file)
        