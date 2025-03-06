import request from '@/utils/request'

export function permApp(query, data) {
  return request({
    url: '/api/v1/perms/users/mytickets/apply/',
    method: 'post',
    params: query,
    data: data
  })
}

export function permAppDb(query, data) {
  return request({
    url: '/api/v1/perms/users/mytickets/applydb/',
    method: 'post',
    params: query,
    data: data
  })
}

export function permMd(query, data) {
  return request({
    url: '/api/v1/perms/users/mytickets/applymd/',
    method: 'post',
    params: query,
    data: data
  })
}
