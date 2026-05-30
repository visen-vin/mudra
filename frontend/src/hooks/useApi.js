import useSWR from 'swr'
import axios from 'axios'

const fetcher = (url) => axios.get(url).then(res => res.data)

export function usePositions() {
  const { data, error, mutate } = useSWR('/api/positions', fetcher, {
    refreshInterval: 5000 // Poll every 5s
  })
  return {
    positions: data,
    isLoading: !error && !data,
    isError: error,
    mutate
  }
}

export function useHistory(limit = 50, offset = 0) {
  const { data, error, mutate } = useSWR(`/api/history?limit=${limit}&offset=${offset}`, fetcher)
  return {
    history: data,
    isLoading: !error && !data,
    isError: error,
    mutate
  }
}

export function useSettings() {
  const { data, error, mutate } = useSWR('/api/settings', fetcher)
  return {
    settings: data,
    isLoading: !error && !data,
    isError: error,
    mutate
  }
}

export function usePrices(symbols = []) {
  const query = symbols.length > 0 ? `?symbols=${symbols.join(',')}` : ''
  const { data, error, mutate } = useSWR(`/api/prices${query}`, fetcher, {
    refreshInterval: 2000 // Poll every 2s for prices
  })
  return {
    prices: data,
    isLoading: !error && !data,
    isError: error,
    mutate
  }
}
