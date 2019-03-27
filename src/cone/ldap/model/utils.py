import os


def ldap_cfg_file():
    return os.environ['LDAP_CFG_FILE']


def ldap_server(model):
    return model.root['settings']['ldap_server']


def ldap_users(model):
    return model.root['settings']['ldap_users']


def ldap_groups(model):
    return model.root['settings']['ldap_groups']


def ldap_roles(model):
    return model.root['settings']['ldap_roles']
