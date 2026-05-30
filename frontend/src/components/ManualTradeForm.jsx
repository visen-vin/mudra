import React, { useState } from 'react'
import { api } from '../lib/api'

export default function ManualTradeForm({ onOrderPlaced, currentMode }) {
  const [formData, setFormData] = useState({
    symbol: 'BTCUSDT',
    market: 'crypto',
    side: 'long',
    qty: 0.01,
    entry_price: 0,
    sl: 0,
    tp: 0
  })
  const [loading, setLoading] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: ['qty', 'entry_price', 'sl', 'tp'].includes(name) ? parseFloat(value) : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.orders.place({ ...formData, mode: currentMode })
      onOrderPlaced()
      // Reset form or some fields if needed
    } catch (error) {
      alert('Error placing order: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const setPercentSL = (percent) => {
    const entry = formData.entry_price || 0
    if (entry === 0) return
    const sl = formData.side === 'long' 
      ? entry * (1 - percent / 100) 
      : entry * (1 + percent / 100)
    setFormData(prev => ({ ...prev, sl: parseFloat(sl.toFixed(2)) }))
  }

  const setPercentTP = (percent) => {
    const entry = formData.entry_price || 0
    if (entry === 0) return
    const tp = formData.side === 'long' 
      ? entry * (1 + percent / 100) 
      : entry * (1 - percent / 100)
    setFormData(prev => ({ ...prev, tp: parseFloat(tp.toFixed(2)) }))
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
        <h2 className="text-lg font-bold text-gray-800">New Trade</h2>
      </div>
      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Market</label>
            <select
              name="market"
              value={formData.market}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            >
              <option value="crypto">Crypto</option>
              <option value="indian_equity">Equity</option>
            </select>
          </div>
          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Symbol</label>
            <input
              type="text"
              name="symbol"
              value={formData.symbol}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              placeholder="BTCUSDT"
              required
            />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Side</label>
            <div className="flex bg-gray-100 p-1 rounded-lg">
              <button
                type="button"
                onClick={() => setFormData(p => ({...p, side: 'long'}))}
                className={`flex-1 py-1.5 text-xs font-bold rounded-md transition-all ${formData.side === 'long' ? 'bg-green-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
              >
                LONG
              </button>
              <button
                type="button"
                onClick={() => setFormData(p => ({...p, side: 'short'}))}
                className={`flex-1 py-1.5 text-xs font-bold rounded-md transition-all ${formData.side === 'short' ? 'bg-red-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
              >
                SHORT
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Quantity</label>
            <input
              type="number"
              step="any"
              name="qty"
              value={formData.qty}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Entry Price</label>
            <input
              type="number"
              step="any"
              name="entry_price"
              value={formData.entry_price}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <div className="space-y-4 pt-2">
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-xs font-bold text-gray-500 uppercase">Stop Loss</label>
              <div className="flex gap-1">
                {[1, 2, 5].map(p => (
                  <button key={p} type="button" onClick={() => setPercentSL(p)} className="text-[10px] bg-gray-100 hover:bg-gray-200 px-1.5 py-0.5 rounded text-gray-600">{p}%</button>
                ))}
              </div>
            </div>
            <input
              type="number"
              step="any"
              name="sl"
              value={formData.sl}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-red-500 border-red-50"
              required
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-xs font-bold text-gray-500 uppercase">Take Profit</label>
              <div className="flex gap-1">
                {[2, 5, 10].map(p => (
                  <button key={p} type="button" onClick={() => setPercentTP(p)} className="text-[10px] bg-gray-100 hover:bg-gray-200 px-1.5 py-0.5 rounded text-gray-600">{p}%</button>
                ))}
              </div>
            </div>
            <input
              type="number"
              step="any"
              name="tp"
              value={formData.tp}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-green-500 border-green-50"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 rounded-xl font-bold text-sm shadow-lg transition-all ${
            loading 
              ? 'bg-gray-400 cursor-not-allowed' 
              : formData.side === 'long' 
                ? 'bg-green-600 hover:bg-green-700 text-white shadow-green-200' 
                : 'bg-red-600 hover:bg-red-700 text-white shadow-red-200'
          }`}
        >
          {loading ? 'EXECUTING...' : `EXECUTE ${formData.side.toUpperCase()}`}
        </button>
      </form>
    </div>
  )
}
