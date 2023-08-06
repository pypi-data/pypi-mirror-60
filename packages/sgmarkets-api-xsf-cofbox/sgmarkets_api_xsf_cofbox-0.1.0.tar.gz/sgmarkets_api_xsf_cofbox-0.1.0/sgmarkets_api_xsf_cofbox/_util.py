
import os
import re
import json
import pandas as pd


class Util:

    @staticmethod
    def build_url(dic_url):
        """
        """
        return '{}{}{}'.format(dic_url['base_url'],
                               dic_url['service'],
                               dic_url['endpoint'])

    @staticmethod
    def multiple_replace(dic, text):
        """
        """
        # Create a regex from the dict keys
        regex = re.compile('(%s)' % '|'.join(map(re.escape, dic.keys())))

        # For each match, lookup corresponding value in dict
        return regex.sub(lambda mo: dic[mo.string[mo.start():mo.end()]], text)

    @staticmethod
    def load(folder, filename):
        """
        """
        path = os.path.join(folder, filename)
        with open(path, 'r') as f:
            content = f.read()
        return content

    @staticmethod
    def save_as_json(data, folder, name, tagged):
        """
        """
        now = pd.Timestamp.now()
        tag = now.strftime(format='_%Y%m%d-%H%M%S') if tagged else ''

        content = json.dumps(data)

        if not os.path.exists(folder):
            os.makedirs(folder)
        path = os.path.join(folder, name+tag+'.json')

        with open(path, 'w') as f:
            f.write(content)

        return path
