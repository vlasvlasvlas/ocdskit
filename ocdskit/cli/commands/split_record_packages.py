from .base import BaseCommand


class Command(BaseCommand):
    name = 'split-record-packages'
    help = 'reads record packages from standard input, and prints many record packages for each'

    def add_arguments(self):
        self.add_argument('size', type=int,
                          help='the number of records per package')

    def handle(self):
        for line in self.buffer():
            package = self.json_loads(line)

            records = package['records']

            # We can't determine which records came from which packages.
            if 'packages' in package:
                del package['packages']

            for i in range(0, len(records), self.args.size):
                package.update(records=records[i:i + self.args.size])

                self.print(package)