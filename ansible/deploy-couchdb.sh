#!/bin/bash

. ./unimelb-comp90024-2021-grp-7-openrc.sh; ansible-playbook --ask-become-pass deploy-couchdb.yaml -i inventory/hosts.ini