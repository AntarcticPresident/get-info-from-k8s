#!/usr/bin/env python
# -*- coding: utf8 -*-


import pymysql, datetime, re


config={
    "host":"127.0.0.1",
    "user":"root",
    "password":"",
    "database":"config"
}


db = pymysql.connect(**config)
cursor = db.cursor()


def get_pod_info(pod_list, service):
   # try:
        db = pymysql.connect(**config)
        cursor = db.cursor()
        info_list = {}
        for i in pod_list.items:
            if service in i.metadata.name:
    	        nginx_ip1 = i.status.host_ip
    	        project1 = i.metadata.namespace
    	        hostname1 = i.spec.node_name
    	        info_list[nginx_ip1] = [hostname1,]
    	        if project1 in info_list[nginx_ip1]:
    	            pass
    	        else:
    	            info_list[nginx_ip1].append(project1)
    
        for key in info_list.keys():
    	    nginx_ip2 = key
    	    project2 = []
    	    for i in info_list[key][1:]:
    	        project2.append(i)
    	    hostname2 = info_list[key][0]
	    print "project2:", project2
    	
    	    # 在本地库查找是否存在
    	    sql = "select tenant_project, hostname, deleted_flag from nginx where nginx_ip = '%s';" %nginx_ip2
    	    cursor.execute(sql)
            result = cursor.fetchone()
    	    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    	    if result:
    	        # update sql info
    	        tenant_project = result[0]
    	        sql_hostname = result[1]
                deleted_flag = result[2]
                if deleted_flag == '0':
    	            if tenant_project == '' or sql_hostname != hostname2 or list_compare(eval(tenant_project), project2):
                        print "you bian hua"
                        sql = 'update nginx set hostname = "%s", tenant_project = "%s", monitor_flag = 0, pic_flag = 0, metric = NULL, modified_time = "%s" where nginx_ip = "%s";' % (hostname2, project2, dt, nginx_ip2)
    	    	        cursor.execute(sql)
    	    	        db.commit()
    	            else:
    	    	        sql = "update nginx set modified_time = '%s' where nginx_ip = '%s';" % (dt, nginx_ip2)
                        cursor.execute(sql)
                        db.commit()
                else:
                    print "deleted data doesn't need to correct! (nginx ip: %s)" % nginx_ip2
    	    else:
    	        # insert info
    	        sql = 'insert into nginx (nginx_ip, hostname, tenant_project, monitor_flag, pic_flag, deleted_flag, created_time, modified_time) value ("%s", "%s", "%s", 0, 0, 0, "%s", "%s")' % (nginx_ip2, hostname2, project2, dt, dt)
    	        cursor.execute(sql)
    	        db.commit()
        # 对本地库的冗余数据不做处理,这一段注释掉.以后肯定用的上
        #sql = "update nginx set deleted_flag = 1 where modified_time < '%s';" % dt
        #cursor.execute(sql)
        #db.commit()
        cursor.close()
        db.close()
    #except Exception, e:
    #    print "Something wrong happenned in getting pod(%s) info!" %service
    #    print e
    #return None


def get_node_info(node_list):
    try:
        db = pymysql.connect(**config)
        cursor = db.cursor()

        for i in node_list.items:
	    # 获取容器云上node信息
            nodeHostname = i.metadata.name
            tenant = []
            for j in i.metadata.labels:
    	        if 'tenant.jucloud' in j: tenant.append(j.split('/')[1].encode('utf-8'))
            for j in i.status.addresses:
    	        if j.type == 'InternalIP': internalIP = j.address

	    # 在本地库中查找云内所有IP，并检查是否有变化，有就更新
    	    dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	    sql = "select tenant_name, hostname, deleted_flag from node where node_ip = '%s';" %internalIP
    	    cursor.execute(sql)
            result = cursor.fetchone()
    	    if result:
    	        # update sql info
		print "update"
	        tenant_name = result[0]
	        hostname = result[1]
                deleted_flag = result[2]
                if deleted_flag == '0':
		    if list_compare(eval(tenant_name), tenant) or hostname != nodeHostname:
			print "you bian hua"
	    	        sql = 'update node set tenant_name = "%s", hostname = "%s", agent_flag = 0, monitor_flag =0, pic_flag = 0, metric = NULL, modified_time = "%s" where node_ip = "%s";' %(str(tenant), nodeHostname, dt, internalIP)
	                cursor.execute(sql)
                        db.commit()
                    else:
                        sql = "update node set modified_time = '%s' where node_ip = '%s';" % (dt, internalIP)
                        cursor.execute(sql)
                        db.commit()
		else:
                    print "deleted data dosen't need to correct! (node IP: %s)" %internalIP
    	    else:
                # insert info
    	        sql = 'insert into node (node_ip, tenant_name, hostname, agent_flag, monitor_flag, pic_flag, deleted_flag, docker_flag, created_time, modified_time) value ("%s", "%s", "%s", 0, 0, 0, 0, 0, "%s", "%s")' % (internalIP, str(tenant), nodeHostname, dt, dt)
    	        cursor.execute(sql)
    	        db.commit()
        # 对本地库的冗余数据不做处理,这一段注释掉.以后肯定用的上
        #sql = "update node set deleted_flag = 1 where modified_time < '%s';" % dt
        #cursor.execute(sql)
        #db.commit()
        cursor.close()
        db.close()
    except Exception, e:
        print "Something wrong in getting nodes' info!"
	print e
    return None


def get_project_info(project_list):
    try:
        db = pymysql.connect(**config)
        cursor = db.cursor()
        tenant = []
        for i in project_list.items:
            tenant.append(i.metadata.name)
        if len(tenant) > 10:
            sql = "truncate project_list;"
            cursor.execute(sql)
            db.commit()
            for i in tenant:
                sql = "insert into project_list (project_name) value ('%s');" % i
                cursor.execute(sql)
                db.commit()
        else:
            print "project list may be wrong!\n%s" % project_list
        cursor.close()
        db.close()
    except Exception, e:
        print "Something wrong in update tenant-project info!"
    return None
        

def update_mycat():
    try:
        db = pymysql.connect(**config)
        cursor = db.cursor()
        # 查找线上库中的mycat
        sql = "select mycat_vip, tenant, project from mycat_group;"
        cursor.execute(sql)
        online_info_1 = cursor.fetchone()
        online_info = []
        while online_info_1:
            # fetchone() is a generation, the last element is NoneType.
            if isinstance(online_info_1, tuple):
                online_info.append(online_info_1)
            online_info_1 = cursor.fetchone()
        for online_vip, online_tenant, online_project in online_info:
            dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "select product_flag, deleted from mycat where vip = '%s'" %online_vip
            cursor.execute(sql)
            local = cursor.fetchone()
            if local:
            # update local mysql info
                local_project = local[0]
                deleted_flag = local[1]
                if deleted_flag == 0:
                    if local_project == online_tenant+'-'+online_project:
                        sql = "update mycat set modified_time = '%s' where vip = '%s';" % (dt, online_vip)
                        cursor.execute(sql)
                        db.commit()
                    else:
                        sql = "update mycat set product_flag = '%s', monitor_status = 0, show_status = 0, monitor_metric = NULL, modified_time= '%s' where vip = '%s';" % (online_tenant+"-"+online_project, online_vip, dt)
                        cursor.execute(sql)
                        db.commit()
                else:
                    print "deleted data dosen't need to correct! (vip: %s; project: %s)" % (online_vip, online_tenant+"-"+online_project)
            else:
            # insert info mycat
                sql = "insert into mycat (vip, product_flag, monitor_status, show_status, deleted, created_time, modified_time) value ('%s', '%s', 0, 0, 0, '%s');" %(online_vip, online_tenant+"-"+online_project, dt, dt)
                cursor.execute(sql)
                db.commit()
        # 对本地库的冗余数据不做处理,这一段注释掉.以后肯定用的上
        #sql = "update mycat set deleted = 1 where modified_time < '%s';" % dt
        #cursor.execute(sql)
        #db.commit()
        cursor.close()
        db.close()
    except Exception, e:
        print "Something wrong happenned in updating mycat info!"
    return None


# 比较两个列表是否相同
def list_compare(a, b):
    FLAG_1 = False
    FLAG_2 = False
    for i in a:
	FLAG_1 = False if i in b else True
    for i in b:
	FLAG_2 = False if i in a else True
    if FLAG_1 or FLAG_2:
	return True
    else:
	return False


#if __name__ == '__main__':
#    get_node_info()
