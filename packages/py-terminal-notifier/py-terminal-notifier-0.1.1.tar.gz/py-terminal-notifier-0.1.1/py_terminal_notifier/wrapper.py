import subprocess
import shlex
import re

from .exceptions import TerminalNotifierException


class TerminalNotifier(object):
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        self.subtitle = kwargs.get('subtitle', '')
        self.message = kwargs.get('message', '')
        self.open = kwargs.get('open', '')
        self.app_icon = kwargs.get('app_icon', '')

    def _make_command(self):
        if not self.message:
            raise TerminalNotifierException("Message is required")

        cmd_map = {
            "-title": f'"{self.title}"',
            "-subtitle": f'"{self.subtitle}"',
            "-message": f'"{self.message}"',
            "-open": f'"{self.open}"',
            "-appIcon": f'{self.app_icon}'
        }
        cmd = "/usr/local/bin/terminal-notifier " + \
            " ".join([f"{k} {v}" for k, v in cmd_map.items() if v != '""'])

        shlex_cmd = shlex.split(cmd)
        return shlex_cmd

    def run_cmd(self):
        cmd = self._make_command()
        ps = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        out, err = ps.communicate()