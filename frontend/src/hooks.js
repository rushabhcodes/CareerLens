import { useEffect, useState } from 'react'
import { api, allRecords, errorMessage } from './api'

export function useCollection(path) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [version, setVersion] = useState(0)
  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')
    allRecords(path)
      .then((rows) => {
        if (active) setData({ results: rows, count: rows.length })
      })
      .catch((err) => {
        if (active) setError(errorMessage(err))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [path, version])
  return { data, loading, error, reload: () => setVersion((v) => v + 1) }
}

export function useData(path) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [version, setVersion] = useState(0)
  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')
    api
      .get(path)
      .then((response) => {
        if (active) setData(response.data)
      })
      .catch((err) => {
        if (active) setError(errorMessage(err))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [path, version])
  return { data, loading, error, reload: () => setVersion((v) => v + 1) }
}
