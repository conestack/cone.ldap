from cone.app import get_root
from cone.app import main_hook
from cone.app import register_plugin_config
from cone.app.ugm import ugm_backend
from cone.app.ugm import UGMFactory
from cone.ldap import browser
from cone.ldap.settings import ldap_cfg
from cone.ldap.settings import LDAPGroupsSettings
from cone.ldap.settings import LDAPRolesSettings
from cone.ldap.settings import LDAPServerSettings
from cone.ldap.settings import LDAPUsersSettings
from node.ext.ldap.ugm import Ugm
import logging


logger = logging.getLogger('cone.ldap')


@main_hook
def initialize_ldap(config, global_config, settings):

    #######################
    # XXX: move to cone.ugm

    from cone.ldap.settings import ugm_cfg
    from cone.ldap.settings import UGMGeneralSettings

    ugm_cfg.ugm_settings = settings.get('ugm.config', '')
    register_plugin_config('ugm', UGMGeneralSettings)

    # XXX: end move to cone.ugm
    ###########################

    # Set LDAP related config file paths
    ldap_cfg.server_config = settings.get('ldap.server_config', '')
    ldap_cfg.users_config = settings.get('ldap.users_config', '')
    ldap_cfg.groups_config = settings.get('ldap.groups_config', '')
    ldap_cfg.roles_config = settings.get('ldap.roles_config', '')

    # Register general LDAP server settings
    register_plugin_config('ldap_server', LDAPServerSettings)

    # Register user, groud and role related settings only if LDAP used
    # as UGM backend
    if settings.get('ugm.backend') == 'ldap':
        register_plugin_config('ldap_users', LDAPUsersSettings)
        register_plugin_config('ldap_groups', LDAPGroupsSettings)
        register_plugin_config('ldap_roles', LDAPRolesSettings)

    config.scan(browser)


@ugm_backend('ldap')
class LDAPUGMFactory(UGMFactory):
    """UGM backend factory for LDAP based UGM implementation.
    """

    def __init__(self, settings):
        """UGM Settings are written to config object by main hook.
        """

    def __call__(self):
        settings = get_root()['settings']
        server_settings = settings['ldap_server']
        if not server_settings.ldap_connectivity:
            logger.error(u"Could not initialize authentication implementation. "
                         u"LDAP Server is not available or invalid credentials.")
            return
        props = server_settings.ldap_props
        users_settings = settings['ldap_users']
        if not users_settings.ldap_users_container_valid:
            logger.error(u"Could not initialize authentication implementation. "
                         u"Configured users container invalid.")
            return
        ucfg = users_settings.ldap_ucfg
        groups_settings = settings['ldap_groups']
        gcfg = None
        if groups_settings.ldap_groups_container_valid:
            gcfg = groups_settings.ldap_gcfg
        else:
            logger.warning(u"Configured groups container invalid.")
        roles_settings = settings['ldap_roles']
        rcfg = None
        if roles_settings.ldap_roles_container_valid:
            rcfg = roles_settings.ldap_rcfg
        else:
            logger.warning(u"Configured roles container invalid.")
        return Ugm(
            name='ldap_ugm',
            props=props,
            ucfg=ucfg,
            gcfg=gcfg,
            rcfg=rcfg
        )
