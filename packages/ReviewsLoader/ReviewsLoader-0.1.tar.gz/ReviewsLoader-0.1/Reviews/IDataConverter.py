class IDataConverter(object):
    @staticmethod
    def get_fieldnames():
        raise NotImplementedError

    @staticmethod
    def convert(data):
        raise NotImplementedError
