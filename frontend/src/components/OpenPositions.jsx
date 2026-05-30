import React, { useState } from 'react'
import { api } from '../lib/api'

export default function OpenPositions({ positions, isLoading, isError, onUpdate }) {
  const [expandedId, setExpandedId] = useState(null)

  const handleClosePosition = async (id, currentPrice) => {
    if (!window.confirm('Are you sure you want to close this position?')) return
    try {
      await api.positions.close(id, currentPrice)
      onUpdate()
    } catch (error) {
      alert('Error closing position: ' + (error.response?.data?.detail || error.message))
    }
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 bg-gray-50/50">
          <h2 className="text-base sm:text-lg font-bold text-gray-800">Open Positions</h2>
        </div>
        <div className="space-y-3 p-4 sm:p-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="skeleton h-24 rounded-lg"></div>
          ))}
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 bg-gray-50/50">
          <h2 className="text-base sm:text-lg font-bold text-gray-800">Open Positions</h2>
        </div>
        <div className="p-4 sm:p-6 text-center">
          <p className="text-red-500 text-sm">Error loading positions</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden fade-in">
      <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
        <h2 className="text-base sm:text-lg font-bold text-gray-800">Open Positions</h2>
        <span className="bg-blue-100 text-blue-700 text-xs font-bold px-2.5 py-1 rounded-full">
          {positions?.length || 0}
        </span>
      </div>

      {positions && positions.length > 0 ? (
        <div className="space-y-0 sm:space-y-3 p-3 sm:p-6 divide-y sm:divide-y-0">
          {positions.map((pos, idx) => (
            <div key={pos.id} className="fade-in">
              <div
                className="p-4 hover:bg-gray-50 transition-colors cursor-pointer rounded-lg sm:rounded-xl border border-transparent sm:border-gray-100 mb-0 sm:mb-3"
                onClick={() => setExpandedId(expandedId === pos.id ? null : pos.id)}
              >
                {/* Primary Info - Always visible */}
                <div className="flex justify-between items-start gap-3 mb-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-base sm:text-lg text-gray-900">{pos.symbol}</h3>
                    <p
                      className={`text-xs font-bold uppercase mt-1 ${
                        pos.side === 'long' ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {pos.side}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleClosePosition(pos.id, pos.current_price || pos.entry_price)
                    }}
                    className="tap-target text-xs bg-red-50 text-red-600 px-3 py-2 rounded-lg font-bold hover:bg-red-100 transition-colors border border-red-100 flex-shrink-0 active:scale-95"
                  >
                    CLOSE
                  </button>
                </div>

                {/* Entry and PnL - Key metrics */}
                <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-3">
                  <div className="bg-gray-50 rounded-lg p-2.5 sm:p-3">
                    <p className="text-[9px] sm:text-[10px] text-gray-500 uppercase font-bold tracking-wide mb-0.5">
                      Entry Price
                    </p>
                    <p className="text-sm sm:text-base font-mono font-bold text-gray-900">
                      {pos.entry_price.toLocaleString()}
                    </p>
                  </div>
                  <div
                    className={`rounded-lg p-2.5 sm:p-3 ${
                      (pos.pnl || 0) >= 0
                        ? 'bg-green-50'
                        : 'bg-red-50'
                    }`}
                  >
                    <p className="text-[9px] sm:text-[10px] text-gray-500 uppercase font-bold tracking-wide mb-0.5">
                      Unrealized PnL
                    </p>
                    <p
                      className={`text-sm sm:text-base font-mono font-bold ${
                        (pos.pnl || 0) >= 0 ? 'text-green-700' : 'text-red-700'
                      }`}
                    >
                      {(pos.pnl || 0) >= 0 ? '+' : ''}{(pos.pnl || 0).toLocaleString()}
                    </p>
                  </div>
                </div>

                {/* Current Price */}
                <div className="bg-blue-50 rounded-lg p-2.5 sm:p-3">
                  <p className="text-[9px] sm:text-[10px] text-gray-500 uppercase font-bold tracking-wide mb-0.5">
                    Current Price
                  </p>
                  <p className="text-sm sm:text-base font-mono font-bold text-blue-700">
                    {(pos.current_price || pos.entry_price).toLocaleString()}
                  </p>
                </div>

                {/* Expandable Details - SL, TP, Qty */}
                <div
                  className={`overflow-hidden transition-all duration-200 ${
                    expandedId === pos.id ? 'mt-3 pt-3 border-t border-gray-200' : ''
                  }`}
                >
                  {expandedId === pos.id && (
                    <div className="grid grid-cols-3 gap-2.5 slide-in-bottom">
                      <div className="bg-red-50 rounded-lg p-2.5 sm:p-3">
                        <p className="text-[9px] sm:text-[10px] text-gray-500 uppercase font-bold tracking-wide mb-0.5">
                          Stop Loss
                        </p>
                        <p className="text-xs sm:text-sm font-mono text-red-700 font-bold">
                          {pos.sl.toLocaleString()}
                        </p>
                      </div>
                      <div className="bg-green-50 rounded-lg p-2.5 sm:p-3">
                        <p className="text-[9px] sm:text-[10px] text-gray-500 uppercase font-bold tracking-wide mb-0.5">
                          Take Profit
                        </p>
                        <p className="text-xs sm:text-sm font-mono text-green-700 font-bold">
                          {pos.tp.toLocaleString()}
                        </p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-2.5 sm:p-3">
                        <p className="text-[9px] sm:text-[10px] text-gray-500 uppercase font-bold tracking-wide mb-0.5">
                          Quantity
                        </p>
                        <p className="text-xs sm:text-sm font-mono text-gray-700 font-bold">
                          {pos.qty}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-12 w-12 mx-auto text-gray-300 mb-3"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
            />
          </svg>
          <p className="text-gray-400 text-sm">No open positions</p>
          <p className="text-gray-300 text-xs mt-1">Your positions will appear here</p>
        </div>
      )}
    </div>
  )
}
