##############################################################################
# test ldap server
##############################################################################

define set_testldap_env
	@export LDAP_ADD_BIN=$(OPENLDAP_DIR)/bin/ldapadd
	@export LDAP_DELETE_BIN=$(OPENLDAP_DIR)/bin/ldapdelete
	@export SLAPD_BIN=$(OPENLDAP_DIR)/libexec/slapd
	@export SLAPD_URIS=ldap://127.0.0.1:12345
	@export ADDITIONAL_LDIF_LAYERS=
endef

.PHONY: start-ldap-base
start-ldap-base:
	$(call set_testldap_env)
	@$(VENV_FOLDER)/bin/testldap start base

.PHONY: start-ldap-gon-10-10
start-ldap-gon-10-10:
	$(call set_testldap_env)
	@$(VENV_FOLDER)/bin/testldap start groupOfNames_10_10

.PHONY: start-ldap-gon-100-100
start-ldap-gon-100-100:
	$(call set_testldap_env)
	@$(VENV_FOLDER)/bin/testldap start groupOfNames_100_100

.PHONY: start-ldap-posix
start-ldap-posix:
	$(call set_testldap_env)
	@$(VENV_FOLDER)/bin/testldap start posixGroups

.PHONY: stop-ldap
stop-ldap:
	$(call set_testldap_env)
	@$(VENV_FOLDER)/bin/testldap stop

##############################################################################
# test instance
##############################################################################

.PHONY: run-base
run-base:
	@$(VENV_FOLDER)/bin/pserve cfg/base/ldap_base.ini

.PHONY: run-gon-10-10
run-gon-10-10:
	@$(VENV_FOLDER)/bin/pserve cfg/gon_10_10/ldap_gon_10_10.ini

.PHONY: run-gon-100-100
run-gon-100-100:
	@$(VENV_FOLDER)/bin/pserve cfg/gon_100_100/ldap_gon_100_100.ini

.PHONY: run-posix
run-posix:
	@$(VENV_FOLDER)/bin/pserve cfg/posix/ldap_posix.ini
