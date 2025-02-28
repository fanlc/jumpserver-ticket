'''
这个是对接工单系统
工单发起接口请求
创建数据库授权 相关的数据处理
'''

import requests
import json
import pymysql

from time import sleep
from accounts.models.account import Account

# from .data_format import obtain_auth, merge_data, update_auth, create_auth

def create_account_template(account_template_name):
    '''
    创建模版账号
    密码: 手动指定，全部都是: ahZqD!4eVz9HRP^&
    '''
    admin_token = "4768943dd8ecff2872859e42eeabade6d8aa17dd"    # prod
    # admin_token = "ef5c1e53ece1028b3cbff47f56b5e3357a6b42e0"    # test

    jms_url = 'http://127.0.0.1:8080'
    url = jms_url + '/api/v1/accounts/account-templates/'

    headers = {
        "Authorization": 'Token ' + admin_token,
        'X-JMS-ORG': '00000000-0000-0000-0000-000000000002'
    }


    # 先组合参数
    # account_template = {
    #     "privileged": "false",
    #     "secret_type": "password",
    #     "secret_strategy": "random",
    #     "password_rules": {
    #         "length": 16,
    #         "lowercase": "true",
    #         "uppercase": "true",
    #         "digit": "true",
    #         "symbol": "true",
    #         "exclude_symbols": ""
    #     },
    #     "auto_push": "true",
    #     "push_params": {},
    #     "name": account_template_name,
    #     "username": account_template_name,
    #     "comment": account_template_name,
    #     "is_active": "true",
    #     "secret": ""
    # }

    account_template = {
        "name": account_template_name,
        "username": account_template_name,
        "secret_type": "password",
        "secret": "ahZqD!4eVz9HRP^&",
        "comment": account_template_name,
        "secret_strategy": "specific",
        "push_params": {},
        "privileged": "false",
        "is_active": "true",
        "auto_push": "false"
    }

    try:
        response = requests.post(url, headers=headers, data=account_template)

        response_json = json.loads(response.text)

        account_template_id = response_json["id"]

        return account_template_id
    except:
        return ""


def bind_asset(account_template_id, account_template_name, assets_id_list):
    '''
    把模版账号绑定给机器
    [
        {
            "template": "e1e13876-ed59-46d9-b9ef-03cd721f0613",
            "name": "jump_db_fanlichun_r",
            "username": "jump_db_fanlichun_r",
            "secret_type": "password",
            "privileged": false,
            "asset": "c477c0fe-c95d-4e50-bd1b-1472f79189cb"
        }
    ]
    '''
    admin_token = "4768943dd8ecff2872859e42eeabade6d8aa17dd"    # prod
    # admin_token = "ef5c1e53ece1028b3cbff47f56b5e3357a6b42e0"    # test

    jms_url = 'http://127.0.0.1:8080'
    url = jms_url + '/api/v1/accounts/accounts/'

    headers = {
        "Authorization": 'Token ' + admin_token,
        'X-JMS-ORG': '00000000-0000-0000-0000-000000000002',
        'Content-Type': 'application/json'
    }

    # 先组合参数
    bing_mes = []
    template_asset = []

    for assetsid, assetsip in assets_id_list:
        bing_mes.append({
            "template": account_template_id,
            "name": account_template_name,
            "username": account_template_name,
            "secret_type": "password",
            "privileged": "false",
            "is_active": "true",
            "asset": str(assetsid)
        })

        template_asset.append([
            account_template_id,
            str(assetsid),
            assetsip
        ])


    json_data = json.dumps(bing_mes)

    response = requests.post(url, headers=headers, data=json_data)

    # 获取绑定后的id
    # if response.status_code == 201:
    #     response_json = json.loads(response.text)

    #     account_id = response_json[0]["id"]

    #     # 激活账号 /api/v1/accounts/accounts/40119099-4b19-4ea6-9904-0a31753f23e2/
    #     url = jms_url + '/api/v1/accounts/accounts/' + account_id + '/'

    #     # 组合数据
    #     active_data = {
    #         "is_active": "true",
    #         "name": account_template_name
    #     }

    #     requests.patch(url, headers=headers, data=json.dumps(active_data))

    return template_asset


def authorize_user(account_template_name, template_asset, all_assets_readonly):
    '''
    1, 查看用户是否创建
    2, 授权表给用户
    template_asset: 是一个大列表
    小列表：下标
    0: account_template_id
    1: assetsid
    2: assetsip
    3: selectdb 这个是一个列表
    template_asset = [[
        "1aeb2ffd-ca91-4dbc-9e5c-8f37d32d1f75",
        "c477c0fe-c95d-4e50-bd1b-1472f79189cb",
        "10.4.9.139",
        ["alert_manage"]
    ]]
    '''

    res = []

    # 连接数据库
    for mes_list in template_asset:
        if mes_list[2] in all_assets_readonly:
            # 如果ip在只读列表 那么就跳出本次循环
            continue
        try:
            # prod
            db_user = "jumpserver_r"
            db_pwd = "subSEWW7xErBBLmZ"

            # dev
            # db_user = "root"
            # db_pwd = "QAZwsx123!"

            connection = pymysql.connect(
                                        host=mes_list[2],
                                        user=db_user,
                                        password=db_pwd,
                                        db="mysql",
                                        charset='utf8mb4'
                                    )
        except:
            # res = [{"value": '连接数据库失败',"label": '连接数据库失败'}]
            return "error"

        # 获取数据库
        try:
            # 创建cursor对象
            with connection.cursor() as cursor:

                # 先查看用户是否已经创建
                checkuser_sql = "SELECT 1 FROM mysql.user WHERE User = %s"
                
                # 执行
                cursor.execute(checkuser_sql, (account_template_name,))
                # 获取查询结果
                # (1)
                user_info = cursor.fetchone()

                # 判断用户是否存在
                if not user_info:
                    # # 用户不存在 推送用户
                    # # 获取推送账号id
                    # push_account_id_list = []
                    # account_obj = Account.objects.get(asset_id=mes_list[1], source_id=mes_list[0])
                    # push_account_id_list.append(str(account_obj.id))


                    # # 推送账号
                    # admin_token = "4768943dd8ecff2872859e42eeabade6d8aa17dd"    # prod
                    # # admin_token = "ef5c1e53ece1028b3cbff47f56b5e3357a6b42e0"    # test

                    # jms_url = 'http://127.0.0.1:8080'
                    # url = jms_url + '/api/v1/accounts/accounts/tasks/'

                    # headers = {
                    #     "Authorization": 'Token ' + admin_token,
                    #     'X-JMS-ORG': '00000000-0000-0000-0000-000000000002',
                    #     'Content-Type': 'application/json'
                    # }

                    # # 组合数据
                    # '''
                    # {
                    #     "action": "push",
                    #     "accounts": [
                    #         "3c899fcc-359e-4ac6-9717-22b11f158f95"
                    #     ]
                    # }
                    # '''

                    # push_data = {
                    #     "action": "push",
                    #     "accounts": push_account_id_list
                    # }

                    # # 推送账号
                    # json_data = json.dumps(push_data)

                    # response = requests.post(url, headers=headers, data=json_data)

                    # # 推送后 需要等待推送成功，静默5秒
                    # sleep(5)

                    '''
                    不让jumpseerveer 推送mysql用户了
                    直接连接数据 创建用户
                    '''

                    # 创建新用户的SQL语句
                    create_user_sql = f"""
                    CREATE USER '{account_template_name}'@'%' IDENTIFIED BY 'ahZqD!4eVz9HRP^&';
                    """

                    # 执行创建用户的SQL语句
                    cursor.execute(create_user_sql)

                    flushsql = "FLUSH PRIVILEGES;"
                    cursor.execute(flushsql)


                # 如果用户创建成功的话 那就授权用户 库权限
                # mes_list[3] 这里面是用户选择的库
                for dbname in mes_list[3]:

                    # # 循环3次 给用户授权 每次循环1秒
                    # for i in range(3):
                    #     sleep(1)
                    #     grant_sql = f"GRANT SELECT ON {dbname}.* TO '{account_template_name}'@'%';"

                    #     cursor.execute(grant_sql)

                    #     flushsql = "FLUSH PRIVILEGES;"
                    #     cursor.execute(flushsql)

                    # 这里不用循环了，之前循环 是因为jumpserver推送用户 需要时间，所以就在这 循环等待用户推送创建
                    # 现在上面是直接创建用户，所以不用循环了
                    # 保险起见，我们还是等待1秒
                    sleep(1)
                    grant_sql = f"GRANT SELECT ON {dbname}.* TO '{account_template_name}'@'%';"
                    cursor.execute(grant_sql)

                    flushsql = "FLUSH PRIVILEGES;"
                    cursor.execute(flushsql)


        except Exception as e:
            print(e)
            return "error"

        finally:
        # 关闭连接
            connection.close()

