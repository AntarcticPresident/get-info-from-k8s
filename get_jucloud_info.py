#!/usr/bin/env python
# -*- coding: utf8 -*-


from __future__ import absolute_import
from kubernetes import client, config
import logging.config

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from func import *


# init log set
logpath = '../addnode/addnode/log.conf'
logging.config.fileConfig(logpath)
logger = logging.getLogger('kubapi')


def main():
    with open('token.txt', 'r') as file:
        Token = file.read().strip('\n')

    APISERVER = 'https://10.18.210.7:6443'

    configuration = client.Configuration()
    configuration.host = APISERVER
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + Token}

    # Do calls
    v1 = client.CoreV1Api()
    # 搜集pod信息
    print "collect nginx info!"
    pod_list = v1.list_pod_for_all_namespaces(watch=False)
    if pod_list.items == None:
        logger.info("request failed in getting pods' info!")
    else:
        get_pod_info(pod_list, 'nginx')

#    # 搜集node信息
#    print "collect node info!"
#    node_list = v1.list_node(watch=False)
#    if node_list.items == None:
#        logger.info("request failed in getting nodes' info!")
#    else:
#	print "chu li"
#        get_node_info(node_list)

#    # 搜集project信息
#    print "collect project info!"
#    project_list = v1.list_namespace(watch=False)
#    if project_list.items ==None:
#        logger.info("request failed in getting projects' info!")
#    else:
#        get_project_info(project_list)
#
#    # 搜集mycat信息
#    print "collect mycat info!"
#    update_mycat()


if __name__ == '__main__':
    main()
