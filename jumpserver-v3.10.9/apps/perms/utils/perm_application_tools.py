import json
from .data_serialize import serialize_perm


def mes_format(params, body):
    # print(params, body)

    # 获取信息
    assets_list = []
    is_linux = ''
    is_win = ''
    for assets_mes in body:
        assets_list.append(assets_mes['id'])
        if assets_mes['platform'] == 'Linux':
            is_linux = True
        else:
            is_win = True
    
    if params['adminperm']:
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

        name_fmat = "%s-superuser" % params['uname']
        comment_fmat = "%s-超级用户" % params['pname']
    else:
        accounts_list = [
            "@SPEC",
            "@INPUT",
            "app"
        ]
        name_fmat = "%s-regularusers" % params['uname']
        comment_fmat = "%s-普通用户" % params['pname']

    req_payload_dict = {
        "assets": assets_list,
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
            params['nameid']
        ],
        "comment": comment_fmat
    }

    # print(req_payload_dict)
    return req_payload_dict


def create_authorization(params, body):
    
    mes_format_dict = mes_format(params, body)
    res = serialize_perm(mes_format_dict)

    return res

