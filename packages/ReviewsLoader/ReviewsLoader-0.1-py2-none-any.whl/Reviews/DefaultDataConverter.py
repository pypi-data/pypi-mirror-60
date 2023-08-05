from .IDataConverter import IDataConverter


class DefaultDataConverter(IDataConverter):
    @staticmethod
    def get_fieldnames():
        return ['title', 'rating', 'review', 'date', 'userName', 'response', 'responseDate']
    
    @staticmethod
    def convert(data):
        try:
            result = {
                'title': data['attributes']['title'],
                'rating': data['attributes']['rating'],
                'review': data['attributes']['review'],
                'date': data['attributes']['date'],
                'userName': data['attributes']['userName'],
            }
            if 'developerResponse' in data['attributes']:
                result['response'] = data['attributes']['developerResponse']['body']
                result['responseDate'] = data['attributes']['developerResponse']['modified']
            return result
        except KeyError:
            return None