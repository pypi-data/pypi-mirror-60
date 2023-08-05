#  Copyright  2020 Alexis Lopez Zubieta
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.

from .command import Command


class AptGetError(RuntimeError):
    pass


class AptGet(Command):
    def __init__(self, prefix, config_path):
        super().__init__('apt-get')
        self.prefix = prefix
        self.config = config_path

    def install(self, packages):
        command = self._create_apt_get_install_download_only_command(packages)
        self._run(command)
        if self.return_code != 0:
            raise AptGetError('Unable to download packages')

    def _create_apt_get_install_download_only_command(self, packages):
        command = [self.runnable, '-c', self.config, '--download-only', '-y', '--no-install-recommends', "install"]
        command.extend(packages)
        return command

    def update(self):
        command = self._create_apt_get_update_command()
        self._run(command)

        if self.return_code != 0:
            raise AptGetError("Update failed")

    def _create_apt_get_update_command(self):
        return [self.runnable, '-c', self.config, 'update']
