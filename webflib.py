
# pylint: disable-msg=R0913,W0511,E1103

'''

webflib
=======

WebFaction XML-RPC API library

'''

import xmlrpclib
import logging
import os.path
import httplib

from configobj import ConfigObj


class WebFactionDBUser(object):
    def __init__(self, username, password, db_type):
        super(WebFactionDBUser, self).__init__()
        self.username = username
        self.password = password
        self.db_type = db_type
                
API_URL = 'https://api.webfaction.com/'
CONF = os.path.expanduser('~/.webfrc')
class WebFactionXmlRpc(object):

    '''WebFaction XML-RPC server proxy class'''

    def __init__(self, user=None, password=None, machine=None):
        self.log = logging.getLogger("webf")
        self.session_id = None
        self.server = None
        if not (user and password):
            try:
                user, password = WebFactionXmlRpc.get_config()
            except NotImplementedError as e:
                self.log.error("You must set a username and password. Either by passing them to __init__ or setting up your config file")
                raise e

        self.username = user
        self.password = password
        self.machine = machine
        self.login()
        
    @staticmethod
    def get_config():
        '''Get configuration file from user's directory'''
        if not os.path.exists(CONF):
            err = u"\n".join([
                u"  Set your username/password in %s" % CONF,
                u"  The format is:",
                u"      username=<username>",
                u"      password=<password>",
                ])
            raise NotImplementedError(err)
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
        extra_args = [self.machine] if self.machine else []
        self.session_id, account = self.server.login(self.username, self.password, *extra_args)

        self.log.debug("self.session_id %s account %s", self.session_id,
            account)

    def create_app(self, app_name, app_type, autostart, extra_info):
        '''Create new application'''
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
            return True
        except xmlrpclib.Fault:
            self.log.exception("Error creating app")
            return False
        except httplib.ResponseNotReady:
            self.log.exception("Response not ready")
            return False

    def delete_app(self, app_name):
        '''Create new application'''
        try:
            result = self.server.delete_app(
                    self.session_id,
                    app_name
                    )
            self.log.debug(result)
        except xmlrpclib.Fault:
            self.log.exception("Error deleting app")
            return 1
    
    def list_apps(self):
        '''List all existing webfaction apps
        https://docs.webfaction.com/xmlrpc-api/apiref.html#method-list_apps
        Returns a list of dicts'''
        try:
            return self.server.list_apps(self.session_id)
        except xmlrpclib.Fault:
            self.log.exception("Problem listing apps")
            return []
            
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
        except xmlrpclib.Fault:
            self.log.exception("Error deleting database %s of type %s", name, db_type)
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
            return True
        except xmlrpclib.Fault:
            self.log.exception("Error creating database %s of type %s", name, db_type)
            return False
        except httplib.ResponseNotReady:
            self.log.exception("Response not ready")
            return False
            
    def list_dbs(self):
        try:
            return self.server.list_dbs(self.session_id)
        except xmlrpclib.Fault:
            self.log.exception("Error listing databases")
            return []
    
    def list_db_users(self):
        try:
            return self.server.list_db_users(self.session_id)
        except xmlrpclib.Fault:
            self.log.exception("Error listing database users")
            return []
    
    def create_db_user(self, username, password, db_type):
        try:
            response = self.server.create_db_user(self.session_id, username, password, db_type)
            self.log.debug(response)
            return WebFactionDBUser(username, password, db_type)
            
        except xmlrpclib.Fault:
            self.log.exception("Error creating database user")
            return None
    
    def delete_db_user(self, db_user):
        if not isinstance(db_user, WebFactionDBUser):
            raise ValueError("db_user must be an instance of WebFactionDBUser")
        
        try:
            self.server.delete_db_user(
                        self.session_id,
                        db_user.username,
                        db_user.db_type
                        )
            return True
        except xmlrpclib.Fault:
            self.log.exception("Error deleting database user")
            return False
            
    def grant_db_permissions(self, db_user, database):
        if not isinstance(db_user, WebFactionDBUser):
            raise ValueError("db_user must be an instance of WebFactionDBUser")
            
        try:
            self.server.grant_db_permissions(
                                    self.session_id,
                                    db_user.username,
                                    database,
                                    db_user.db_type
                                    )
            return True
        except xmlrpclib.Fault:
            self.log.exception("Error granting database permissions")
            return False
            
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
        except xmlrpclib.Fault:
            self.log.exception("Error creating cron job")
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
        except xmlrpclib.Fault:
            self.log.exception("Error deleting cron job")
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
        except xmlrpclib.Fault:
            self.log.exception("Error creating website")
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
        except xmlrpclib.Fault:
            self.log.exception("Error creating email")
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
        except xmlrpclib.Fault:
            self.log.exception("Error deleting email")
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
        except xmlrpclib.Fault:
            self.log.exception("Error creating mailbox")
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
        except xmlrpclib.Fault:
            self.log.exception("Error deleting mailbox")
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
        except xmlrpclib.Fault:
            self.log.exception("Error setting apache acl")
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
        except xmlrpclib.Fault:
            self.log.exception("Error running system command %s", cmd)
            return 1

    def list_disk_usage(self):
        '''
        List disk space usage statistics about your account
        http://docs.webfaction.com/xmlrpc-api/apiref.html#method-list_disk_usage
        
        @returns: Structure containing all disk usage members (see link for details)
        @rtype: None on success or 1 on failure
        '''
        try:
            result = self.server.list_disk_usage(self.session_id)
            self.log.debug(result)
            return result
        except xmlrpclib.Fault:
            self.log.exception("Error listing disk usage")
            return 1

    def list_bandwidth_usage(self):
        '''
        List bandwidth usage statistics for your websites
        http://docs.webfaction.com/xmlrpc-api/apiref.html#method-list_bandwidth_usage
        
        @returns: Structure containing two members, daily and monthly
        @rtype: None on success or 1 on failure
        '''
        try:
            result = self.server.list_bandwidth_usage(self.session_id)
            self.log.debug(result)
            return result
        except xmlrpclib.Fault:
            self.log.exception("Error listing bandwidth usage")
            return 1
