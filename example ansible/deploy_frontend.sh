#!/usr/bin/env bash
. ./unimelb-comp90024-2021-grp-7-openrc.sh; ansible-playbook --ask-become-pass deploy_frontend.yaml -i inventory/application_hosts.ini