from django.http import JsonResponse, HttpResponse
from assets.models import Asset
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from users.models.user import User
from accounts.models.template import AccountTemplate

from perms.utils.mytickets.data_format import myapp_dataformat, myapproval, get_mysql_alldb, judge_readonly

import os,json
from time import sleep

from ..utils.mytickets.data_format import obtain_auth, merge_data, update_auth, create_auth

from ..utils.mytickets.task_mysql import create_account_template, bind_asset, authorize_user


def get_all_node(request):
    get_params = request.GET.dict()
    # {assettype: "node", uname: 'fanlichun', 'page': '1', 'limit': '20', 'ip': '10.8.100.54'}
    # print(get_params)
    if get_params['ip']:
        if get_params['assettype'] == "node":
            assets_object = Asset.objects.filter(Q(platform__name="Linux") | Q(platform__name="Windows") | Q(platform__name="Windows2016"), address=get_params['ip']).order_by('address')
            obj_count = len(assets_object)
        else:
            assets_object = Asset.objects.filter(platform__name="MySQL", address=get_params['ip']).order_by('address')
            obj_count = len(assets_object)
    else:
        if get_params['assettype'] == "node":
            assets_object = Asset.objects.filter(Q(platform__name="Linux") | Q(platform__name="Windows") | Q(platform__name="Windows2016")).order_by('address')
            obj_count = len(assets_object)
        else:
            assets_object = Asset.objects.filter(platform__name="MySQL").order_by('address')
            obj_count = len(assets_object)

    # 创建Paginator对象，每页显示10条数据
    paginator = Paginator(assets_object, int(get_params['limit']))
    page_obj = paginator.get_page(int(get_params['page']))
    assets_all_list = []

    if get_params['assettype'] == "node":
        for assets_mes in page_obj:
            assets_all_q = {}
            assets_all_q['id'] = assets_mes.id
            assets_all_q['name'] = assets_mes.name
            assets_all_q['address'] = assets_mes.address
            assets_all_q['platform'] = assets_mes.platform.name
            assets_all_q['created_by'] = assets_mes.created_by
            assets_all_list.append(assets_all_q)
    else:
        # 如果是mysql 资产的话 需要进行数据的处理
        # 查询这个数据的 所有库，以及这个用户已经拥有权限的库
        for assets_mes in page_obj:
            assets_all_q = {}
            assets_all_q['id'] = assets_mes.id
            assets_all_q['name'] = assets_mes.name
            assets_all_q['address'] = assets_mes.address
            assets_all_q['platform'] = assets_mes.platform.name
            assets_all_q['created_by'] = assets_mes.created_by
            assets_all_q['readonly'] = judge_readonly(assets_mes.get_labels())
            assets_all_q['alldb'] = get_mysql_alldb(assets_mes.address, get_params['uname'])
            assets_all_q['xz'] = []
            assets_all_list.append(assets_all_q)

    # assetsu_queryset = assets_object.values(
    #     "id",
    #     "name",
    #     "address",
    #     "platform",
    #     "created_by",
    #     "is_active"
    # )
    
    # assetsu_queryset_list = list(assetsu_queryset)
    # # print(assetsu_queryset_list)

    # from ...users.models.user import User

    # from users.models import User

    # a = User.objects.get(username='admin')

    # print(a.id)


    context = {
        "code": 20000,
        "data": {
            'total': obj_count,
            'items': assets_all_list,
            'page': int(get_params['page']),
            'limit': int(get_params['limit']),
            "total_page": paginator.num_pages
        }
    }

    return JsonResponse(context, safe=False)


def my_application(request):
    '''
    listQuery: {
        page: 1,
        limit: 10,
        uname: 'fanlichun'
    }
    '''  
    get_params = request.GET.dict()
    is_user = get_params['uname']
    all_my_application_filename = []
    directory = 'perms/utils/nowapplication/'
    entries = os.listdir(directory)
    file_names = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
    if is_user:
        for filename in file_names:
            filename_q = filename.split('-', 1)[0]
            mysql_filename = filename.split('.', 1)[0]
            if filename_q == is_user:
                all_my_application_filename.append(filename)
            elif mysql_filename == f"jump_db_{is_user}_r":
                all_my_application_filename.append(filename)
            else:
                pass
    else:
        all_my_application_filename = file_names

    all_my_application_filename.sort(reverse=True)
    # print(all_my_application_filename)
    res = myapp_dataformat(all_my_application_filename, get_params['page'], get_params['limit'])
    return JsonResponse(res, safe=False)


def my_myapproval(request):
    if request.method == 'POST':
        json_b = request.body
        file_name_str = json_b.decode('utf-8')

        # print(file_name_str)
        res = myapproval(file_name_str)
        return JsonResponse(res, safe=False)
    else:
        context = {
            "code": 20000,
            "data": {
                'total': 'obj_count',
                'items': 'assets_all_list'
            }
        }
        return JsonResponse(context, safe=False)
    

@csrf_exempt   #不再做检测！其他没加装饰器的函数还是会检测
def create_auth_nodes(request):
    '''
    工单系统 创建nodes权限
    body = {
        "pname": "张三",         # 中文名称
        "uname": "zhangsan",    # 名称拼音
        "adminperm": false,    # 是否为管理员权限，true为管理员权限，false为普通用户权限
        "assets": [             # 机器ip列表
            "1.1.1.1",
            "2.2.2.2",
            "3.3.3.3",
            "4.4.4.4",
        ],
    }
    '''
    if request.method == 'POST':
        json_b = request.body
        json_str = json_b.decode('utf-8')
        json_obj = json.loads(json_str)

        if "pname" not in json_obj or not json_obj['pname']:
            context = {
                "code": 40000,
                "mes": "参数错误，用户名错误！"
            }
            return JsonResponse(context, safe=False)

        if "uname" in json_obj:
            if json_obj['uname']:
                user_obj_ = User.objects.filter(username=json_obj['uname'])
                if user_obj_:
                    user_obj = user_obj_[0]
                    user_id = user_obj.id
                else:
                    context = {
                        "code": 40000,
                        "mes": "跳板机没有此用户，请去登陆一下跳板机！"
                    }
                    return JsonResponse(context, safe=False)
            else:
                context = {
                    "code": 40000,
                    "mes": "参数错误，用户名错误！"
                }
                return JsonResponse(context, safe=False)
        else:
            context = {
                "code": 40000,
                "mes": "参数错误，用户名错误！"
            }
            return JsonResponse(context, safe=False)


        # 获取所有的服务器信息
        # 判断申请的权限是 linux的 还是windows的
        is_linux = ''
        is_win = ''
        if "assets" in json_obj:
            if json_obj['assets']:
                # 获取所有的服务器id列表
                assets_ip_list = json_obj['assets']
                assets_all_obj = Asset.objects.filter(address__in=assets_ip_list)
                assets_id_list = list(assets_all_obj.values_list('id', flat=True))

                for assets_mes in assets_all_obj:
                    if assets_mes.platform.name == "Linux":
                        is_linux = True
                    else:
                        is_win = True
            else:
                context = {
                    "code": 40000,
                    "mes": "参数错误，请传入申请的机器列表！"
                }
                return JsonResponse(context, safe=False)
        else:
            context = {
                "code": 40000,
                "mes": "参数错误，请传入申请的机器列表！"
            }
            return JsonResponse(context, safe=False)


        # 设置权限账号数据
        if "adminperm" in json_obj:
            value = json_obj['adminperm']
            if value is None or value == '' or value == [] or value == () or value == set() or value == {}:
                context = {
                    "code": 40000,
                    "mes": "参数错误，请传入申请的权限！"
                }
                return JsonResponse(context, safe=False)
            else:
                # 如果要是true 那就是管理员权限
                if value:
                    # 超级用户
                    if is_linux and is_win:
                        accounts_list = [
                            "@SPEC",
                            "root",
                            "administrator"
                        ]
                    elif is_linux and not is_win:
                        accounts_list = [
                            "@SPEC",
                            "root"
                        ]
                    else:
                        accounts_list = [
                            "@SPEC",
                            "administrator"
                        ]

                    name_fmat = "%s-superuser" % user_obj.username
                    comment_fmat = "%s-超级用户" % user_obj.name
                else:
                    # 普通用户
                    accounts_list = [
                        "@SPEC",
                        "app"
                    ]
                    name_fmat = "%s-regularusers" % user_obj.username
                    comment_fmat = "%s-普通用户" % user_obj.name
        else:
            context = {
                "code": 40000,
                "mes": "参数错误，请传入申请的权限！"
            }
            return JsonResponse(context, safe=False)



        '''
        组合数据，这个数据用于创建用户授权
        '''
        init_loaded_data = {
            "assets": assets_id_list,
            "nodes": [],
            "accounts": accounts_list,
            "protocols": ["all"],
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
            "name": name_fmat,
            "users": [
                user_id
            ],
            "comment": comment_fmat
        }

        # 先判断有没有老的授权。获取老的授权
        old_auth_dict = obtain_auth(init_loaded_data)

        if old_auth_dict:
            new_data_result = merge_data(old_auth_dict, init_loaded_data)
            update_auth(new_data_result)
        else:
            create_auth(init_loaded_data)


        context = {
            "code": 20000,
            "mes": "权限创建成功!"
        }
        return JsonResponse(context, safe=False)


@csrf_exempt   #不再做检测！其他没加装饰器的函数还是会检测
def create_auth_mysqls(request):
    '''
    工单系统 创建mysqls权限
    body = {
        "pname": "张三",         # 中文名称
        "uname": "zhangsan",    # 名称拼音
        "assets": [             # 数据库列表 
            {
                "address": "1.1.1.1",
                "selectdb": [
                    "db1",
                    "db2",
                    "db3"
                ]
            },
            {
                "address": "2.2.2.2",
                "selectdb": [
                    "db1",
                    "db3"
                ]
            },
            {
                "address": "10.8.100.54",
                "selectdb": [
                    "db2",
                    "db3"
                ]
            }
        ],
    }
    '''

    if request.method == 'POST':
        json_b = request.body
        json_str = json_b.decode('utf-8')
        json_obj = json.loads(json_str)

        if "pname" not in json_obj or not json_obj['pname']:
            context = {
                "code": 40000,
                "mes": "参数错误，用户名错误！"
            }
            return JsonResponse(context, safe=False)

        if "uname" in json_obj:
            if json_obj['uname']:
                user_obj_ = User.objects.filter(username=json_obj['uname'])
                if user_obj_:
                    user_obj = user_obj_[0]
                    user_id = user_obj.id
                else:
                    context = {
                        "code": 40000,
                        "mes": "跳板机没有此用户，请去登陆一下跳板机！"
                    }
                    return JsonResponse(context, safe=False)
            else:
                context = {
                    "code": 40000,
                    "mes": "参数错误，用户名错误！"
                }
                return JsonResponse(context, safe=False)
        else:
            context = {
                "code": 40000,
                "mes": "参数错误，用户名错误！"
            }
            return JsonResponse(context, safe=False)
        

        '''
        首先：创建一个模版账号。账号固定格式 jump_db_fanlichun_r。
        密码：自动生成
        勾选自动推送账号到数据库
        '''

        # 先获取模版账号列表，看是否已经创建过了 模版账号
        # 直接从数据库获取 更快
        # 这个名称是 模版的名称，数据库账号的名称
        account_template_name = 'jump_db_{}_r'.format(user_obj.username)

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
                context = {
                    "code": 40000,
                    "mes": "创建模版账号出错！"
                }
                return JsonResponse(context, safe=False)


        # 然后给机器 绑定模版账号
        # 循环机器列表 拿到机器id
        assets_ip_list = []
        all_assets_readonly = []
        for assetsmes in json_obj['assets']:
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

        # if not template_asset:
        #     context = {
        #         "code": 40000,
        #         "mes": "绑定账号失败！"
        #     }
        #     return JsonResponse(context, safe=False)
        # 绑定完成

        # 然后去操作数据库
        '''
        1, 查看用户是否创建
        2, 授权表给用户
        '''
        # 授权表给用户
        # 得连接数据库

        # 先整理数据
        '''
        [['dadas', '2.2.2.2', ['db1', 'db3']],
            ['dadas', '1.1.1.1', ['db1', 'db2', 'db3']],
            ['dadas', '10.8.100.54', ['db2', 'db3']]]
        '''
        for uassets in json_obj['assets']:
            for ta in template_asset:
                if uassets["address"] == ta[2]:
                    ta.append(uassets["selectdb"])

        #### template_asset
        ### [['12669cf1-581d-4865-af78-bb68ba16d985', '26954cde-0cda-4da2-b773-a9819ef81599', '10.8.100.102', ['test1', 'test2']]]

        # 去操作数据库 给用户授权
        # 先静默2秒 等待用户自动推送
        sleep(5)
        res = authorize_user(account_template_name, template_asset, all_assets_readonly)

        if res:
            context = {
                "code": 40000,
                "mes": "操作数据库 给用户授权失败！"
            }
            return JsonResponse(context, safe=False)


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
                user_id
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


        context = {
            "code": 20000,
            "mes": "权限创建成功!"
        }
        return JsonResponse(context, safe=False)

