import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const http = axios.create({ baseURL: '/api', timeout: 90000 })

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('lq_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const detail = err.response?.data?.detail
    const msg = typeof detail === 'string' ? detail : (detail?.[0]?.msg ?? err.message)
    if (err.response?.status === 401) {
      localStorage.removeItem('lq_token')
      localStorage.removeItem('lq_user')
      if (router.currentRoute.value.path !== '/login') router.push('/login')
    }
    ElMessage.error(msg || '请求失败')
    return Promise.reject(err)
  }
)

export default http
