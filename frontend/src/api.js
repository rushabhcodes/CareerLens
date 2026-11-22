import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/',
  timeout: 90000,
})
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('careerlens-token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config.url.includes('auth/login')) {
      window.dispatchEvent(new Event('careerlens-session-expired'))
    }
    return Promise.reject(error)
  },
)

export function errorMessage(error) {
  const payload = error.response?.data?.error
  if (!payload)
    return error.code === 'ECONNABORTED'
      ? 'This request took too long. Please try again.'
      : 'Could not reach CareerLens. Check that the backend is running.'
  const fields = payload.fields || {}
  const messages = Object.entries(fields)
    .filter(([key]) => key !== 'detail')
    .map(
      ([key, value]) =>
        `${key.replaceAll('_', ' ')}: ${Array.isArray(value) ? value.join(' ') : typeof value === 'object' ? JSON.stringify(value) : value}`,
    )
  return messages.length ? messages.join(' · ') : payload.message
}

export async function allRecords(path) {
  const output = []
  let page = 1
  while (true) {
    const { data } = await api.get(path, { params: { page } })
    if (Array.isArray(data)) return data
    output.push(...data.results)
    if (!data.next) return output
    page += 1
  }
}

export async function downloadFile(path, name) {
  const response = await api.get(path, { responseType: 'blob' })
  const url = URL.createObjectURL(response.data)
  const link = document.createElement('a')
  link.href = url
  link.download = name
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
