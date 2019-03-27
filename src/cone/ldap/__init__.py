from cone.ldap.browser import static_resources
from cone.ldap.model.settings import GroupsSettings
from cone.ldap.model.settings import RolesSettings
from cone.ldap.model.settings import ServerSettings
from cone.ldap.model.settings import UsersSettings
import cone.app
import logging
import os


logger = logging.getLogger('cone.ldap')


# custom UGM styles
cone.app.cfg.merged.css.protected.append((static_resources, 'styles.css'))

# UGM settings
cone.app.register_plugin_config('ldap_server', ServerSettings)
cone.app.register_plugin_config('ldap_users', UsersSettings)
cone.app.register_plugin_config('ldap_groups', GroupsSettings)
cone.app.register_plugin_config('ldap_roles', RolesSettings)


# application startup hooks
@cone.app.main_hook
def initialize_ldap(config, global_config, local_config):
    """Initialize LDAP.
    """
    # add translation
    config.add_translation_dirs('cone.ldap:locale/')

    # static resources
    config.add_view(static_resources, name='cone.ldap.static')

    # scan browser package
    config.scan('cone.ldap.browser')

    # LDAP bases UGM
    os.environ['LDAP_CFG_FILE'] = local_config.get('cone.ldap.ldap_config', '')
    import cone.ugm
    ldap_auth = local_config.get('cone.auth_impl') == 'node.ext.ldap'
    if not ldap_auth:
        return
    reset_ldap_auth_impl()


def reset_auth_impl():
    """LDAP only at the moment.
    """
    return reset_ldap_auth_impl()


def reset_ldap_auth_impl():
    import cone.app
    root = cone.app.get_root()
    settings = root['settings']
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
    ugm = Ugm(name='ldap_ugm', props=props, ucfg=ucfg, gcfg=gcfg, rcfg=rcfg)
    cone.app.cfg.auth = ugm
    return ugm
