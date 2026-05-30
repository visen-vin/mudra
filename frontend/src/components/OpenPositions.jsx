import React from 'react'
import { api } from '../lib/api'

export default function OpenPositions({ positions, isLoading, isError, onUpdate }) {
  const handleClosePosition = async (id, currentPrice) => {
    if (!window.confirm('Are you sure you want to close this position?')) return
    try {
      await api.positions.close(id, currentPrice)
      onUpdate()
    } catch (error) {
      alert('Error closing position: ' + (error.response?.data?.detail || error.message))
    }
  }

  if (isLoading) return <div className="p-4">Loading positions...</div>
  if (isError) return <div className="p-4 text-red-500">Error loading positions</div>

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
        <h2 className="text-lg font-bold text-gray-800">Open Positions</h2>
        <span className="bg-blue-100 text-blue-700 text-xs font-bold px-2 py-1 rounded-full">
          {positions?.length || 0}
        </span>
      </div>
      <div className="divide-y divide-gray-100">
        {positions && positions.length > 0 ? (
          positions.map(pos => (
            <div key={pos.id} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-bold text-gray-900">{pos.symbol}</h3>
                  <p className={`text-xs font-bold uppercase ${pos.side === 'long' ? 'text-green-600' : 'text-red-600'}`}>
                    {pos.side}
                  </p>
                </div>
                <button
                  onClick={() => handleClosePosition(pos.id, pos.current_price || pos.entry_price)}
                  className="text-xs bg-red-50 text-red-600 px-3 py-1.5 rounded-lg font-bold hover:bg-red-100 transition-colors border border-red-100"
                >
                  CLOSE
                </button>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">Entry / Current</p>
                  <p className="text-sm font-mono text-gray-700">
                    {pos.entry_price.toLocaleString()} / <span className="font-bold">{(pos.current_price || pos.entry_price).toLocaleString()}</span>
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">Unrealized PnL</p>
                  <p className={`text-sm font-mono font-bold ${(pos.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(pos.pnl || 0) >= 0 ? '+' : ''}{(pos.pnl || 0).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="mt-3 flex gap-4">
                <div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">SL</p>
                  <p className="text-xs font-mono text-red-500 bg-red-50 px-2 py-0.5 rounded border border-red-100">{pos.sl.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">TP</p>
                  <p className="text-xs font-mono text-green-500 bg-green-50 px-2 py-0.5 rounded border border-green-100">{pos.tp.toLocaleString()}</p>
                </div>
                <div className="ml-auto">
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">Qty</p>
                  <p className="text-xs font-mono text-gray-600 bg-gray-100 px-2 py-0.5 rounded">{pos.qty}</p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="p-8 text-center">
            <p className="text-gray-400 text-sm">No open positions</p>
          </div>
        )}
      </div>
    </div>
  )
}
