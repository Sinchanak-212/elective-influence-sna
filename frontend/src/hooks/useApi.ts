import { useState, useEffect, useCallback, useRef } from 'react'
import { isApiError } from '../lib/api'

type Status = 'idle' | 'loading' | 'success' | 'error' | 'unavailable'

interface ApiState<T> {
  data: T | null
  status: Status
  error: string | null
  refetch: () => void
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = []
): ApiState<T> {
  const [data, setData] = useState<T | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState<string | null>(null)
  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  const run = useCallback(async () => {
    setStatus('loading')
    setError(null)
    try {
      const result = await fetcherRef.current()
      setData(result)
      setStatus('success')
    } catch (err) {
      if (isApiError(err)) {
        if (err.status === 503) {
          setStatus('unavailable')
        } else {
          setStatus('error')
          setError(err.message)
        }
      } else {
        setStatus('error')
        setError(err instanceof Error ? err.message : 'Unknown error')
      }
    }
  }, deps) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    run()
  }, [run])

  return { data, status, error, refetch: run }
}
