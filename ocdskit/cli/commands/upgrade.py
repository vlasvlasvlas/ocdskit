from ocdskit import upgrade
from ocdskit.cli.commands.base import BaseCommand
from ocdskit.exceptions import CommandError


class Command(BaseCommand):
    name = 'upgrade'
    help = 'upgrades packages and releases from an old version of OCDS to a new version'

    def add_arguments(self):
        self.add_argument('versions', help='the colon-separated old and new versions')

    def handle(self):
        versions = self.args.versions

        version_from, version_to = versions.split(':')
        if version_from < version_to:
            direction = 'up'
        else:
            direction = 'down'

        try:
            upgrade_method = getattr(upgrade, 'upgrade_{}'.format(versions.replace('.', '').replace(':', '_')))
        except AttributeError:
            raise CommandError('{}grade from {} is not supported'.format(direction, versions.replace(':', ' to ')))

        for line in self.buffer():
            data = self.json_loads(line)
            upgrade_method(data)
            self.print(data)