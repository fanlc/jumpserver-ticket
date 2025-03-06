from assets.models import Asset
from django.core.paginator import Paginator

import json
import pymysql
import requests
import copy

from time import sleep

from users.models.user import User
from accounts.models.template import AccountTemplate
from .task_mysql import create_account_template, bind_asset, authorize_user


def paginate(items, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end]


def myapp_dataformat(all_my_application_filename, page, limit):
    # print(all_my_application_filename)
    res = []
    for file_name in all_my_application_filename:
        file_name_path = 'perms/utils/nowapplication/%s' % file_name
        # print(file_name_path)
        try:
            with open(file_name_path, 'r') as file:
                loaded_data = json.load(file)
            
            # print(loaded_data)
            # 判断是mysql文件还是node文件,就是文件的类型
            if loaded_data["platform"] == "MySQL":
                # mysql
                res.append(loaded_data)
                # print(loaded_data)
            else:
                # print(loaded_data)
                assets_id_list = loaded_data['assets']
                assets_ip_list = []
                for assets_id in assets_id_list:
                    asset_mes_obj = Asset.objects.filter(id=assets_id)
                    assets_mes = '{0.name}({0.address})'.format(asset_mes_obj[0])
                    assets_ip_list.append(assets_mes)
                assets_ip_str = ','.join(assets_ip_list)
                loaded_data['assets'] = assets_ip_str
                if len(loaded_data['accounts']) != 1:
                    del loaded_data['accounts'][0]
                accounts_str = ' '.join(loaded_data['accounts'])
                loaded_data['accounts'] = accounts_str
                res.append(loaded_data)
                # print(loaded_data)
        except:
            pass
    # print(res)
    page_1 = paginate(res, int(page), int(limit))
    # print(page_1)

    obj_count = len(res)
    context = {
        "code": 20000,
        "data": {
            'total': obj_count,
            'items': page_1
        }
    }
    return context

def obtain_auth(mes_format_dict):
    admin_token = "4768943dd8ecff2872859e42eeabade6d8aa17dd"    # prod
    # admin_token = "ef5c1e53ece1028b3cbff47f56b5e3357a6b42e0"    # test
    jms_url = 'http://127.0.0.1:8080'
    url = jms_url + '/api/v1/perms/asset-permissions/'

    headers = {
        "Authorization": 'Token ' + admin_token,
        'X-JMS-ORG': '00000000-0000-0000-0000-000000000002'
    }
    response = requests.get(url, headers=headers)
    response_json = json.loads(response.text)

    for auth_dict in response_json:
        if auth_dict['name'] == mes_format_dict['name']:
            # print('已经有授权了')
            asset_perm_id = auth_dict['id']
            url = jms_url + '/api/v1/perms/asset-permissions/' + asset_perm_id + '/'
            response = requests.get(url, headers=headers)
            response_json = json.loads(response.text)
            return response_json
        
    return False


def merge_data(old_data, new_data):
    # print('aaaa', old_data)
    # print('bbbb', new_data)
    for assets_mes in old_data['assets']:
        new_data['assets'].append(assets_mes['id'])
    result = list(set(old_data['accounts'] + new_data['accounts']))
    new_data['accounts'] = result
    new_data['id'] = old_data['id']
    return new_data


def update_auth(new_data_result):
    admin_token = "4768943dd8ecff2872859e42eeabade6d8aa17dd"    # prod
    # admin_token = "ef5c1e53ece1028b3cbff47f56b5e3357a6b42e0"    # test
    jms_url = 'http://127.0.0.1:8080'
    removed_value = new_data_result.pop('id')
    url = jms_url + '/api/v1/perms/asset-permissions/' + removed_value + '/'

    headers = {
        "Authorization": 'Token ' + admin_token,
        'X-JMS-ORG': '00000000-0000-0000-0000-000000000002'
    }
    response = requests.put(url, headers=headers, data=new_data_result)
    # print(json.loads(response.text))


def create_auth(mes_format_dict):
    admin_token = "4768943dd8ecff2872859e42eeabade6d8aa17dd"    # prod
    # admin_token = "ef5c1e53ece1028b3cbff47f56b5e3357a6b42e0"    # test
    jms_url = 'http://127.0.0.1:8080'
    url = jms_url + '/api/v1/perms/asset-permissions/'

    headers = {
        "Authorization": 'Token ' + admin_token,
        'X-JMS-ORG': '00000000-0000-0000-0000-000000000002'
    }
    response = requests.post(url, headers=headers, data=mes_format_dict)
    # print(json.loads(response.text))


def change_status(init_loaded_data, file_name_path):
    init_loaded_data['is_done'] = "true"
    with open(file_name_path, 'w') as file:
        json.dump(init_loaded_data, file)

def myapproval(file_name_str):
    init_loaded_data = ''
    file_name_path = 'perms/utils/nowapplication/%s' % file_name_str

    # filename_q = file_name_str.split('-', 1)[0]
    # mysql_filename = file_name_str.split('.', 1)[0]

    try:
        with open(file_name_path, 'r') as file:
            loaded_data = json.load(file)

        # 这里是判断 审批的是node工单还是mysql工单
        if loaded_data["platform"] == "MySQL":
            # 首先检查用户是否存在 jumpserver数据库，没有的话 就先去登陆一下
            user_obj_ = User.objects.filter(username=loaded_data['uname'])
            if not user_obj_:
                res = {
                    "code": 40000,
                    'type': 'error',
                    'mes': '跳板机没有此用户，请去登陆一下跳板机！'
                }
                return res
            
            '''
            首先：创建一个模版账号。账号固定格式 jump_db_fanlichun_r。
            密码: 手动指定，全部都是: ahZqD!4eVz9HRP^&
            勾选自动推送账号到数据库
            '''

            # 先获取模版账号列表，看是否已经创建过了 模版账号
            # 直接从数据库获取 更快
            # 这个名称是 模版的名称，数据库账号的名称
            account_template_name = loaded_data['name']

            account_template_obj = AccountTemplate.objects.filter(username=account_template_name)

            if account_template_obj:
                # 有这个模版账号 就获取模版id
                account_template_id_uuid = account_template_obj[0].id
                account_template_id = str(account_template_id_uuid)
            else:
                # 没有这个模版的话 那就新建一个 用跳板机的接口去创建
                # 会返回创建的模版账号id
                account_template_id_uuid = create_account_template(account_template_name)
                if account_template_id_uuid:
                    account_template_id = str(account_template_id_uuid)
                else:
                    res = {
                        "code": 40000,
                        'type': 'error',
                        'mes': '创建模版账号出错！'
                    }
                    return res
                
            # 然后给机器 绑定模版账号
            # 循环机器列表 拿到机器id

            assets_ip_list = []
            all_assets_readonly = []
            # 获取ip列表
            for assetsmes in loaded_data['allasset']:
                if assetsmes['readonly']:
                    all_assets_readonly.append(assetsmes['address'])

                assets_ip_list.append(assetsmes['address'])

            '''
            [(UUID('1f86e5e6-d0d9-4cc1-b45d-edcef5ea53db'), '10.8.100.102'),
                (UUID('6a5a1eda-0f18-4cf5-a1ce-dab54c543d2e'), '10.8.100.102'),
                (UUID('71e0519b-70e0-4c57-b14f-6dd018cfa334'), '1.1.1.1'),
                (UUID('d0d97bc9-d296-4f18-b1e9-0c93b1e6c931'), '1.1.1.1'),
                (UUID('e304fef2-e41b-4d48-b13f-96dff7503202'), '10.8.100.102')]
            '''
            assets_id_list = list(Asset.objects.filter(address__in=assets_ip_list).values_list('id', 'address'))

            # 绑定
            template_asset = bind_asset(account_template_id, account_template_name, assets_id_list)

            # 然后去操作数据库
            '''
            1, 查看用户是否创建
            2, 授权表给用户
            '''
            # 授权表给用户
            # 得连接数据库

            # 先整理数据
            '''
            [['mysql1', '2.2.2.2', ['db1', 'db3']],
                ['mysql2', '1.1.1.1', ['db1', 'db2', 'db3']],
                ['mysql3', '10.8.100.54', ['db2', 'db3']]]
            '''
            for uassets in loaded_data['allasset']:
                for ta in template_asset:
                    if uassets["address"] == ta[2]:
                        ta.append(uassets["xz"])

            #### template_asset
            ### [['12669cf1-581d-4865-af78-bb68ba16d985', '26954cde-0cda-4da2-b773-a9819ef81599', '10.8.100.102', ['test1', 'test2']]]

            # 去操作数据库 给用户授权

            # sleep(5)
            # 现在不用等待5秒了，不用等待让jumpserver推送用户了，现在是直接去数据库 新建的用户
            res = authorize_user(account_template_name, template_asset, all_assets_readonly)

            if res:
                context = {
                    "code": 40000,
                    'type': 'error',
                    'mes': '操作数据库 给用户授权失败！'
                }
                return context
            
            assertsid_list = list(Asset.objects.filter(address__in=assets_ip_list).values_list('id', flat=True))
            # 在jumpserver层面给用户授权，创建授权
            init_loaded_data = {
                "assets": assertsid_list,
                "nodes": [],
                "accounts": [
                    "@SPEC",
                    account_template_name
                ],
                "protocols": [
                    "all"
                ],
                "actions": [
                    "connect",
                    "upload",
                    "download",
                    "copy",
                    "paste",
                    "delete",
                    "share"
                ],
                "is_active": "true",
                "users": [
                    loaded_data['nameid']
                ],
                "name": account_template_name,
                "comment": account_template_name
            }

            # 先判断有没有老的授权。获取老的授权
            old_auth_dict = obtain_auth(init_loaded_data)

            if old_auth_dict:
                new_data_result = merge_data(old_auth_dict, init_loaded_data)
                update_auth(new_data_result)
            else:
                create_auth(init_loaded_data)

            # 修改工单文件状态
            change_status(loaded_data, file_name_path)

            res = {
                "code": 20000,
                'type': 'success',
                'mes': '审批通过！权限创建成功!'
            }
            return res

        else:
            init_loaded_data = copy.deepcopy(loaded_data)

            # 先删除一些不用打 参数
            if "platform" in loaded_data:
                del loaded_data['platform']

            old_auth_dict = obtain_auth(loaded_data)
            if old_auth_dict:
                new_data_result = merge_data(old_auth_dict, loaded_data)
                update_auth(new_data_result)
            else:
                create_auth(loaded_data)
            change_status(init_loaded_data, file_name_path)
            res = {
                "code": 20000,
                'type': 'success',
                'mes': '审批通过！权限创建成功!'
            }
            return res
    except Exception as e:
        res = {
            "code": 40000,
            'type': 'error',
            'mes': e
        }
        return res


# 获取这个数据库的所有库，并且根据登陆用户获取是否已经有这个数据库的权限了
def get_mysql_alldb(nodeip, uname):
    '''
    res = [
            {"value": 'ceshi1',"label": 'ceshi1', "disabled": True},
            {"value": 'ceshi2',"label": 'ceshi2'},
        ]
    '''
    res = []

    # 拼接授权的数据库用户名称
    # 这样去数据库查询用户是否 存在 才能查出来
    overall_name = 'jump_db_{}_r'.format(uname)

    # 连接到MySQL服务器
    # prod
    db_user = "jumpserver_r"
    db_pwd = "subSEWW7xErBBLmZ"

    # dev
    # db_user = "root"
    # db_pwd = "QAZwsx123!"
    try:
        connection = pymysql.connect(
                                    host=nodeip,
                                    user=db_user,
                                    password=db_pwd,
                                    db="mysql",
                                    charset='utf8mb4'
                                )
    except:
        res = [{"value": '连接数据库失败',"label": '连接数据库失败'}]


    # 获取数据库
    try:
        # 创建cursor对象
        with connection.cursor() as cursor:
            # 执行查询所有数据库的SQL命令
            cursor.execute("SHOW DATABASES")
            # 获取所有数据库的名称
            databases = cursor.fetchall()
    
            # 筛选出非系统数据库
            system_databases = ['information_schema', 'mysql', 'performance_schema', 'sys']
            # 得到数据库里面的所有数据库名称列表
            filtered_databases = [db[0] for db in databases if db[0] not in system_databases]

            # 查询这个用户是否在数据库有账号
            selectsql = "SELECT 1 FROM mysql.user WHERE user = %s LIMIT 1"
            cursor.execute(selectsql, (overall_name,))

            # 获取结果
            result = cursor.fetchone()

            authorized_db_list = []
            # 检查结果
            if result:
                # 如果用户在数据库里面 就获取已经授权的数据库
                # print(f"用户 {uname} 存在于MySQL中。")
                # 获取已经的授权
                authsql = "SELECT DISTINCT `Db` FROM `db` JOIN `user` ON `db`.`Host` = `user`.`Host` AND `db`.`User` = `user`.`User` WHERE `user`.`User` = %s"
                cursor.execute(authsql, (overall_name,))

                # 已经授权的库的 元祖
                authorized_dbs = cursor.fetchall()

                # 整理成列表
                authorized_db_list = [db[0] for db in authorized_dbs]

        #############################################################
        # 不在这里创建数据库用户，这里只做查询
        #     else:
        #         # print(f"用户 {uname} 不存在于MySQL中。")
        #         # 如果用户不在数据库里面 那就新建一个用户
        #         # 新建用户
        #         createsql = "CREATE USER '%s'@'10.4.8.144' IDENTIFIED BY '44WJznAV5hJuN5qk';"
        #         cursor.execute(createsql, (uname,))

        #         # 刷新权限使新用户设置生效
        #         flushsql = "FLUSH PRIVILEGES;"
        #         cursor.execute(flushsql)


        # # 提交事务
        # # 一般只需要创建 删除 更新 需要提交事物，查询不需要
        # connection.commit()


    except:
        res = [{"value": '获取数据库失败',"label": '获取数据库失败'}]

    finally:
        # 关闭连接
        connection.close()


    # 数据都获取到了 整理一下最终的数据
    # filtered_databases, authorized_db_list
    if authorized_db_list:
        for db in filtered_databases:
            if db in authorized_db_list:
                res.append({
                    "value": db,
                    "label": db,
                    "disabled": True
                })
            else:
                res.append({
                    "value": db,
                    "label": db
                })
    else:
        for db in filtered_databases:
            res.append({
                "value": db,
                "label": db
            })


    # 最终返回的数据
    return res


def judge_readonly(all_lables_qs):
    '''
    all_lables_qs = <QuerySet [<Label: mysql:prod>, <Label: mysql:readonly>]>
    获取mysql资产的标签
    并且从标签判断这个mysql资产是否为只读数据库
    '''
    if all_lables_qs:
        for lable_mes in all_lables_qs:
            if lable_mes.name == "mysql" and lable_mes.value == "readonly":
                return True


    return False

