import request from '@/utils/request'

export function myAllApplication(query) {
  return request({
    url: '/api/v1/perms/users/mytickets/myapplication/',
    method: 'get',
    params: query
  })
}

export function approvalApi(data) {
  return request({
    url: '/api/v1/perms/users/mytickets/myapproval/',
    method: 'post',
    data: data
  })
}
