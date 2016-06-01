import json
import os

test_data = {
    'models': {
        'file': 'models_data.json',
        'data': {}
    }
}


def load_models_data():
    global test_data
    with open(os.path.join(__file__, os.pardir, test_data['models']['file'])) as data:
        test_data['models']['data'] = json.load(data)


def get_models_data():
    return test_data['models']['data']
