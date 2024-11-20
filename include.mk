##############################################################################
# test ldap server
##############################################################################

.PHONY: start-ldap-base
start-ldap-base:
	@(VENV_FOLDER)/bin/testldap start base

.PHONY: start-ldap-gon-10-10
start-ldap-gon-10-10:
	@(VENV_FOLDER)/bin/testldap start groupOfNames_10_10

.PHONY: start-ldap-gon-100-100
start-ldap-gon-100-100:
	@(VENV_FOLDER)/bin/testldap start groupOfNames_100_100

.PHONY: start-ldap-posix
start-ldap-posix:
	@(VENV_FOLDER)/bin/testldap start posixGroups

.PHONY: stop-ldap
stop-ldap:
	@(VENV_FOLDER)/bin/testldap stop

##############################################################################
# test instance
##############################################################################

.PHONY: run-base
run-base:
	@(VENV_FOLDER)/bin/pserve cfg/base/ldap_base.ini

.PHONY: run-gon-10-10
run-gon-10-10:
	@(VENV_FOLDER)/bin/pserve cfg/gon_10_10/ldap_gon_10_10.ini

.PHONY: run-gon-100-100
run-gon-100-100:
	@(VENV_FOLDER)/bin/pserve cfg/gon_100_100/ldap_gon_100_100.ini

.PHONY: run-posix
run-posix:
	@(VENV_FOLDER)/bin/pserve cfg/posix/ldap_posix.ini
