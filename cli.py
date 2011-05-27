
# pylint: disable-msg=W0142
'''

cli.py
======

Command-line tool for WebFaction's XML-RPC API http://api.webfaction.com/

Author: Rob Cakebread <rob@cakebread.info>

License : BSD-2

'''

__docformat__ = 'epytext'
__revision__ = '$Revision:  $'[11:-1].strip()


import sys
import logging
import optparse

from webf.__init__ import __version__ as VERSION
from webf import webflib


class WebFaction(object):

    '''``WebFaction`` class'''

    def __init__(self):
        '''Initialize attributes, set logger'''
        self.options = None
        self.log = logging.getLogger('webf')
        self.log.addHandler(logging.StreamHandler())
        self.group_api = None

    def set_log_level(self):
        '''Set log level according to command-line options'''
        if self.options.debug:
            self.log.setLevel(logging.DEBUG)

    def run(self):
        '''
        Run WebFaction command

        @rtype: int 
        @returns: 0 success or 1 failure
        
        '''
        opt_parser = self.setup_opt_parser()
        (self.options, remaining_args) = opt_parser.parse_args()
        if remaining_args:
            opt_parser.print_help()
        self.set_log_level()

        if self.options.webfaction_version:
            return webfaction_version()

        #Go through list of options in ``group_api`` and execute
        #activated callable for enabled option
        #Looks a bit magic, but saves a ton of if/then branching
        for action in [p for p in self.group_api.option_list]:
            action = str(action)[2:].replace('-', '_')
            if getattr(self.options, action):
                opts = getattr(self.options, action)
                if not isinstance(opts, tuple):
                    opts = [opts]
                server = webflib.WebFactionXmlRpc()
                return getattr(server, action)(*opts)
        else:
            opt_parser.print_help()
        return 1

    def setup_opt_parser(self):
        '''
        Setup the optparser

        @rtype: opt_parser.OptionParser
        @return: Option parser

        '''
        usage = 'usage: %prog [options]'
        opt_parser = optparse.OptionParser(usage=usage)
        group_api = optparse.OptionGroup(opt_parser,
                'WebFaction Commands',
                'Options for calling WebFaction XML-RPC API methods')

        group_api.add_option('--create-app',
                action='store', 
                dest='create_app',
                nargs=4,
                help='Create application',
                metavar='NAME TYPE AUTOSTART EXTRA_INFO'
                )

        group_api.add_option('--delete-app',
                action='store', 
                dest='delete_app',
                help='Delete application',
                metavar='NAME'
                )

        group_api.add_option('--create-cronjob',
                action='store', 
                dest='create_cronjob',
                help='Create cronjob',
                metavar='CRONJOB'
                )

        group_api.add_option('--delete-cronjob',
                action='store', 
                dest='delete_cronjob',
                help='Delete cronjob',
                metavar='CRONJOB'
                )

        group_api.add_option('--create-db',
                action='store', 
                dest='create_db',
                nargs=3,
                help='Create Database',
                metavar='NAME DB_TYPE PASSWORD'
                )

        group_api.add_option('--delete-db',
                action='store', 
                dest='delete_db',
                nargs=2,
                help='Delete Database',
                metavar='NAME DB_TYPE'
                )

        group_api.add_option('--create-domain',
                action='store', 
                dest='create_domain',
                help='Create domain',
                nargs=2,
                metavar='DOMAIN SUBDOMAIN'
                )

        group_api.add_option('--create-website',
                action='store', 
                dest='create_website',
                help='Create website',
                nargs=5,
                metavar='NAME IP HTTPS SUBDOMAINS *SITE_APPS'
                )

        group_api.add_option('--create-dns-override',
                action='store', 
                dest='create_dns_override',
                help='Create DNS override',
                nargs=6,
                metavar='DOMAIN A_IP CNAME MX_NAME MX_PRIORITY SPF_RECORD'
                )

        group_api.add_option('--delete-dns-override',
                action='store', 
                dest='delete_dns_override',
                help='Delete DNS override',
                nargs=6,
                metavar='DOMAIN A_IP CNAME MX_NAME MX_PRIORITY SPF_RECORD'
                )

        group_api.add_option('--create-email',
                action='store', 
                dest='create_email',
                help='Create email address',
                nargs=6,
                metavar='EMAIL_ADDRESS TARGETS AR_ON AR_SUBJECT AR_MSG AR_FROM'
                )

        group_api.add_option('--delete-email',
                action='store', 
                dest='delete_email',
                help='Delete email address',
                metavar='EMAIL_ADDRESS'
                )

        group_api.add_option('--create-mailbox',
                action='store', 
                dest='create_mailbox',
                help='Create mailbox',
                nargs=5,
                metavar='MBOX_NAME SPAM_PROT SHARE SPAM_LEARN HAM_LEARN'
                )

        group_api.add_option('--delete-mailbox',
                action='store', 
                dest='delete_mailbox',
                help='Delete mailbox',
                metavar='MBOX_NAME'
                )

        group_api.add_option('--set-apache-acl',
                action='store', 
                dest='set_apache_acl',
                nargs=3,
                help='Set Apache ACL',
                metavar='PATHS PERMS RECURSIVE'
                )

        group_api.add_option('--system',
                action='store', 
                dest='system',
                help='Run system command.',
                metavar='CMD'
                )
        group_api.add_option('--write-file',
                action='store', 
                dest='write_file',
                help='Write file',
                metavar='FILENAME STRING MODE'
                )

        self.group_api = group_api
        opt_parser.add_option_group(group_api)
        #Common options
        opt_parser.add_option('--version', action='store_true', dest=
                              'webfaction_version', default=False, help=
                              "Show this program's version and exit.")

        opt_parser.add_option('--debug', action='store_true', dest=
                              'debug', default=False, help=
                              'Show debugging information')

        return opt_parser


def webfaction_version():
    '''Print webfaction version'''
    print VERSION

def main():
    '''Let's do it.'''
    client = WebFaction()
    return client.run()


if __name__ == '__main__':
    sys.exit(main())

