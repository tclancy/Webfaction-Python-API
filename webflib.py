
# pylint: disable-msg=R0913,W0511,E1103

'''

webflib
=======

WebFaction XML-RPC API library

'''

import sys
import xmlrpclib
import logging
import os.path

from configobj import ConfigObj


API_URL = 'https://api.webfaction.com/'
CONF = os.path.expanduser('~/.webfrc')

class WebFactionXmlRpc(object):

    '''WebFaction XML-RPC server proxy class'''

    def __init__(self, user, password):
        self.log = logging.getLogger('webf')
        self.session_id = None
        self.server = None
        self.username = user
        self.password = password
        self.login()

    def get_config(self):
        '''Get configuration file from user's directory'''
        if not os.path.exists(CONF):
            self.log.error("Set your username/password in %s" % CONF)
            self.log.error("The format is:")
            self.log.error("  username=<username>")
            self.log.error("  password=<password>")
            sys.exit(1)
        config = ConfigObj(CONF)
        username = config['username']
        password = config['password']
        return (username, password)

    def login(self):
        '''Login to WebFaction and get a session_id'''
        try:
            http_proxy = os.environ['http_proxy']
        except KeyError:
            http_proxy = None
        self.server = xmlrpclib.Server(API_URL, transport=http_proxy)
        self.session_id, account = self.server.login(self.username, self.password)
        self.log.debug("self.session_id %s account %s" % (self.session_id,
            account))

    def create_app(self, app_name, app_type, autostart, extra_info):
        '''Create new application'''
        if autostart.lower() == 'true':
            autostart = True
        else:
            autostart = False
        if extra_info.lower() == 'none':
            extra_info = ''
        try:
            result = self.server.create_app(
                    self.session_id,
                    app_name,
                    app_type,
                    autostart,
                    extra_info 
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def delete_app(self, app_name):
        '''Create new application'''
        try:
            result = self.server.delete_app(
                    self.session_id,
                    app_name
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def delete_db(self, name, db_type):
        '''
        Delete database

        @param name: name of database
        @type name: string

        @param db_type: mysql or postgres
        @type db_type: string
        '''
        #XXX: Validate db_type
        try:
            result = self.server.delete_db(
                    self.session_id,
                    name,
                    db_type
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def create_db(self, name, db_type, password):
        '''
        Create database

        @param name: name of database
        @type name: string

        @param db_type: mysql or postgres
        @type db_type: string

        @param password: password
        @type password: string

        @returns: Nothing
        @rtype: None on success or 1 on failure
        
        '''
        #XXX: Validate db_type
        #XXX: Use interactive method to get password?
        try:
            result = self.server.create_db(
                    self.session_id,
                    name,
                    db_type,
                    password
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def create_cronjob(self, line):
        '''
        Create a cronjob

        @param line: A line you want in your cronjob
        @type line: string

        @returns: Nothing
        @rtype: None on success or 1 on failure
        
        '''
        try:
            result = self.server.create_cronjob(
                    self.session_id,
                    line
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def delete_cronjob(self, line):
        '''
        Delete a cronjob

        @param line: A line you want removed from your cronjob
        @type line: string

        @returns: Nothing
        @rtype: None on success or 1 on failure
        
        '''
        try:
            result = self.server.delete_cronjob(
                    self.session_id,
                    line
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    # pylint: disable-msg=C0103
    def create_website(self, website_name, ip, https, subdomains, site_apps):
        '''
        Create a website

        @param website_name: Name of website
        @type website_name: string

        @param ip: IP Address
        @type ip: string

        @param https: Use https protocol
        @type https: boolean

        @param subdomains: List of subdomains for this website
        @type subdomains: list

        @param site_apps: 
        @type site_apps: list

        @returns: Nothing
        @rtype: None on success or 1 on failure
        
        '''
        if https.lower() == 'true':
            https = True
        else:
            https = False
        subdomains = subdomains.split(',')
        print subdomains
        #XXX: Limitation of only one site_app
        site_apps = site_apps.split(',')
        print site_apps
        try:
            result = self.server.create_website(
                    self.session_id,
                    website_name,
                    ip,
                    https,
                    subdomains,
                    site_apps
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def create_email(self, email_address, targets, autoresponder_on=False,
            autoresponder_subject='', autoresponder_message='',
            autoresponder_from=''):
        '''
        Create an email address for a mailbox

        @param email_address: 
        @type email_address: string

        @param targets: mailbox names
        @type targets: string
 
        @returns: Success code
        @rtype: None on success or 1 on failure
        
        '''
        if autoresponder_on.lower() == 'true':
            autoresponder_on = True
        else:
            autoresponder_on = False
        if autoresponder_subject.lower() == 'none':
            autoresponder_subject = ''
        if autoresponder_message.lower() == 'none':
            autoresponder_message = ''
        if autoresponder_from.lower() == 'none':
            autoresponder_from = ''
        try:
            result = self.server.create_email(
                    self.session_id,
                    email_address,
                    targets,
                    autoresponder_on,
                    autoresponder_subject,
                    autoresponder_message,
                    autoresponder_from,
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def delete_email(self, email_address):
        '''
        Delete an email address

        @param email_address: An email address you want removed from a mailbox
        @type email_address: string

        @returns: Success code
        @rtype: None on success or 1 on failure
        
        '''
        try:
            result = self.server.delete_email(
                    self.session_id,
                    email_address
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def create_mailbox(self, mailbox, enable_spam_protection=True, share=False,
            spam_to_learn_folder='spam_to_learn',
            ham_to_learn_folder='ham_to_learn'):
        '''
        Delete a mailbox

        @param mailbox: Mailbox name you want to create
        @type mailbox: string

        @param enable_spam_protection: Use WebFaction's spam filtering
        @type enable_spam_protection: boolean

        @param share: Unknown
        @type share: boolean

        @returns: Success code
        @rtype: None on success or 1 on failure
        
        '''
        if enable_spam_protection.lower() == 'true':
            enable_spam_protection = True
        elif enable_spam_protection.lower() == 'false':
            enable_spam_protection = False
        else:
            self.log.error(\
                    "Error: enable_spam_protection must be True or False")
            return 1
        try:
            result = self.server.create_mailbox(
                    self.session_id,
                    mailbox,
                    enable_spam_protection,
                    share,
                    spam_to_learn_folder,
                    ham_to_learn_folder
                    )
            self.log.debug(result)
            print "Password for the new mailbox is: %s" % result['password']
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def delete_mailbox(self, mailbox):
        '''
        Delete a mailbox

        @param mailbox: A mailbox name you wanted deleted
        @type mailbox: string

        @returns: Success code
        @rtype: None on success or 1 on failure
        
        '''
        try:
            result = self.server.delete_mailbox(
                    self.session_id,
                    mailbox
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def set_apache_acl(self, paths, permission='rwx', recursive=False):
        '''
        Set Apache ACL

        @param paths:
        @type paths: string

        @param permission: Unix file permissions
        @type permission: string

        @param recursive: Recurse sub-directories
        @type recursive: boolean

        @returns: Success code
        @rtype: None on success or 1 on failure
        
        '''
        try:
            result = self.server.set_apache_acl(
                    self.session_id,
                    paths,
                    permission,
                    recursive,
                    )
            self.log.debug(result)
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

    def system(self, cmd):
        '''
        Runs a Linux command in your homedir and prints the result

        @param cmd: Command you want to run
        @type cmd: string

        @returns: Success code
        @rtype: None on success or 1 on failure
        
        '''
        try:
            result = self.server.system(
                    self.session_id,
                    cmd
                    )
            print result
        except xmlrpclib.Fault, errmsg:
            self.log.error(errmsg)
            return 1

