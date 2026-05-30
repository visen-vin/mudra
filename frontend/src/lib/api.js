import axios from 'axios'

const API_BASE = '/api'

export const api = {
  positions: {
    list: () => axios.get(`${API_BASE}/positions`),
    close: (id, exitPrice) => axios.post(`${API_BASE}/close-position/${id}?exit_price=${exitPrice}`),
  },
  orders: {
    place: (order) => axios.post(`${API_BASE}/place-order`, order),
  },
  history: {
    list: (limit = 50, offset = 0) => axios.get(`${API_BASE}/history?limit=${limit}&offset=${offset}`),
  },
  prices: {
    get: (symbols) => axios.get(`${API_BASE}/prices?symbols=${symbols.join(',')}`),
  },
  settings: {
    get: () => axios.get(`${API_BASE}/settings`),
    update: (mode) => axios.post(`${API_BASE}/settings?mode=${mode}`),
  }
}
