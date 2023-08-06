#Note: Converted
from __future__ import absolute_import

from sciunit2.command import AbstractCommand
from sciunit2.exceptions import CommandLineError, CommandError
from sciunit2.util import quoted
from sciunit2 import timestamp
import sciunit2.workspace

from getopt import getopt
import sys
import humanfriendly


class ShowCommand(AbstractCommand):
    name = 'show'

    @property
    def usage(self):
        return [('show [<execution id>]',
                 'Show detailed information of an execution')]

    def run(self, args):
        optlist, args = getopt(args, '')
        if len(args) > 1:
            raise CommandLineError

        emgr, repo = sciunit2.workspace.current()
        name = sciunit2.workspace.project(repo.location)
        
        rev = args[0]
        e = emgr.get(rev)

        ls = [('id', rev),
              ('sciunit', name),
              ('command', quoted(e.cmd)),
              ('size', humanfriendly.format_size(e.size)),
              ('started', timestamp.fmt_iso(e.started))]
        for ln in ls:
            sys.stdout.write('%7s: %s\n' % ln)
