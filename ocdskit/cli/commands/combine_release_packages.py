import json
from datetime import datetime

from .base import BaseCommand


class Command(BaseCommand):
    name = 'combine-release-packages'
    help = 'reads release packages from standard input, collects releases, and prints one release package'

    def handle(self):
        output = {'releases': []}

        for line in self.buffer():
            package = json.loads(line)

            # Use sample metadata.
            output['uri'] = package['uri']
            output['publishedDate'] = package['publishedDate']
            output['publisher'] = package['publisher']

            if 'extensions' in package:
                output['extensions'].update(package['extensions'])

            for field in ('license', 'publicationPolicy', 'version'):
                if field in package:
                    output[field] = package[field]

            output['releases'].extend(package['releases'])

        self.print(output)
