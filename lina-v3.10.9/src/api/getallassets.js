import request from '@/utils/request'

export function getAllAssets(query) {
  return request({
    url: '/api/v1/perms/users/mytickets/getassets',
    method: 'get',
    params: query
  })
}
