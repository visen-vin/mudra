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
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden fade-in">
      <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 bg-gray-50/50">
        <h2 className="text-base sm:text-lg font-bold text-gray-800">New Trade</h2>
      </div>
      <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4 sm:space-y-5">
        <div className="grid grid-cols-2 gap-3 sm:gap-4">
          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Market</label>
            <select
              name="market"
              value={formData.market}
              onChange={handleInputChange}
              className="input-field text-sm"
            >
              <option value="crypto">Crypto</option>
              <option value="indian_equity">Equity</option>
            </select>
          </div>
          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Symbol</label>
            <input
              type="text"
              name="symbol"
              value={formData.symbol}
              onChange={handleInputChange}
              className="input-field text-sm"
              placeholder="BTCUSDT"
              required
            />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Side</label>
            <div className="flex gap-2 bg-gray-100 p-1.5 rounded-lg">
              <button
                type="button"
                onClick={() => setFormData(p => ({...p, side: 'long'}))}
                className={`flex-1 tap-target py-2.5 text-xs sm:text-sm font-bold rounded-md transition-all active:scale-95 ${
                  formData.side === 'long'
                    ? 'bg-green-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                LONG
              </button>
              <button
                type="button"
                onClick={() => setFormData(p => ({...p, side: 'short'}))}
                className={`flex-1 tap-target py-2.5 text-xs sm:text-sm font-bold rounded-md transition-all active:scale-95 ${
                  formData.side === 'short'
                    ? 'bg-red-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                SHORT
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:gap-4">
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Quantity</label>
            <input
              type="number"
              step="any"
              name="qty"
              value={formData.qty}
              onChange={handleInputChange}
              className="input-field text-sm"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Entry Price</label>
            <input
              type="number"
              step="any"
              name="entry_price"
              value={formData.entry_price}
              onChange={handleInputChange}
              className="input-field text-sm"
              required
            />
          </div>
        </div>

        <div className="space-y-4 sm:space-y-5 pt-2">
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-xs font-bold text-gray-500 uppercase">Stop Loss</label>
              <div className="flex gap-1.5 sm:gap-2">
                {[1, 2, 5].map(p => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPercentSL(p)}
                    className="tap-target text-[10px] sm:text-xs bg-gray-100 hover:bg-gray-200 px-2 sm:px-2.5 py-1 rounded text-gray-600 transition-colors active:scale-95"
                  >
                    {p}%
                  </button>
                ))}
              </div>
            </div>
            <input
              type="number"
              step="any"
              name="sl"
              value={formData.sl}
              onChange={handleInputChange}
              className="input-field text-sm"
              required
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-xs font-bold text-gray-500 uppercase">Take Profit</label>
              <div className="flex gap-1.5 sm:gap-2">
                {[2, 5, 10].map(p => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPercentTP(p)}
                    className="tap-target text-[10px] sm:text-xs bg-gray-100 hover:bg-gray-200 px-2 sm:px-2.5 py-1 rounded text-gray-600 transition-colors active:scale-95"
                  >
                    {p}%
                  </button>
                ))}
              </div>
            </div>
            <input
              type="number"
              step="any"
              name="tp"
              value={formData.tp}
              onChange={handleInputChange}
              className="input-field text-sm"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`w-full tap-target py-3 sm:py-3.5 rounded-xl font-bold text-sm sm:text-base shadow-lg transition-all active:scale-95 ${
            loading
              ? 'bg-gray-400 cursor-not-allowed text-white'
              : formData.side === 'long'
                ? 'bg-green-600 hover:bg-green-700 text-white shadow-green-200'
                : 'bg-red-600 hover:bg-red-700 text-white shadow-red-200'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="h-4 w-4 spin-loader" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              EXECUTING...
            </span>
          ) : (
            `EXECUTE ${formData.side.toUpperCase()}`
          )}
        </button>
      </form>
    </div>
  )
}
