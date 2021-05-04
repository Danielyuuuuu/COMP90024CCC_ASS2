#!/usr/bin/env bash
. ./unimelb-comp90024-2021-grp-7-openrc.sh; ansible-playbook --ask-become-pass deploy_db_and_crawler.yaml -i inventory/application_hosts.ini