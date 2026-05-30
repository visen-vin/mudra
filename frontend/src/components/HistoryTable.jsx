import React from 'react'

export default function HistoryTable({ history, isLoading, isError }) {
  const [filter, setFilter] = React.useState({ market: 'all', side: 'all' })

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 bg-gray-50/50">
          <h2 className="text-base sm:text-lg font-bold text-gray-800">Trade History</h2>
        </div>
        <div className="space-y-3 p-4 sm:p-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="skeleton h-20 rounded-lg"></div>
          ))}
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 bg-gray-50/50">
          <h2 className="text-base sm:text-lg font-bold text-gray-800">Trade History</h2>
        </div>
        <div className="p-4 sm:p-6 text-center">
          <p className="text-red-500 text-sm">Error loading trade history</p>
        </div>
      </div>
    )
  }

  const filteredHistory = history?.filter(trade => {
    const marketMatch = filter.market === 'all' || trade.market === filter.market
    const sideMatch = filter.side === 'all' || trade.side === filter.side
    return marketMatch && sideMatch
  })

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden fade-in">
      <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4 bg-gray-50/50">
        <h2 className="text-base sm:text-lg font-bold text-gray-800">Trade History</h2>
        <div className="flex gap-2 w-full sm:w-auto">
          <select
            value={filter.market}
            onChange={(e) => setFilter(f => ({ ...f, market: e.target.value }))}
            className="flex-1 sm:flex-none text-xs border border-gray-200 rounded-lg px-3 py-2 bg-white outline-none focus:ring-2 focus:ring-blue-500 transition-all tap-target"
          >
            <option value="all">All Markets</option>
            <option value="crypto">Crypto</option>
            <option value="indian_equity">Equity</option>
          </select>
          <select
            value={filter.side}
            onChange={(e) => setFilter(f => ({ ...f, side: e.target.value }))}
            className="flex-1 sm:flex-none text-xs border border-gray-200 rounded-lg px-3 py-2 bg-white outline-none focus:ring-2 focus:ring-blue-500 transition-all tap-target"
          >
            <option value="all">All Sides</option>
            <option value="long">Long</option>
            <option value="short">Short</option>
          </select>
        </div>
      </div>

      {/* Desktop Table - Hidden on mobile */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-50 text-[10px] uppercase font-bold text-gray-500 tracking-wider">
            <tr>
              <th className="px-4 sm:px-6 py-3">Symbol</th>
              <th className="px-4 sm:px-6 py-3">Side</th>
              <th className="px-4 sm:px-6 py-3">Entry/Exit</th>
              <th className="px-4 sm:px-6 py-3">PnL</th>
              <th className="px-4 sm:px-6 py-3">Reason</th>
              <th className="px-4 sm:px-6 py-3">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredHistory && filteredHistory.length > 0 ? (
              filteredHistory.map(trade => (
                <tr key={trade.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 sm:px-6 py-4">
                    <span className="font-bold text-gray-900">{trade.symbol}</span>
                  </td>
                  <td className="px-4 sm:px-6 py-4 text-xs font-bold">
                    <span className={trade.side === 'long' ? 'text-green-600' : 'text-red-600'}>
                      {trade.side.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 sm:px-6 py-4">
                    <div className="text-sm font-mono text-gray-700">
                      {trade.entry_price.toLocaleString()} → {trade.exit_price?.toLocaleString()}
                    </div>
                  </td>
                  <td className="px-4 sm:px-6 py-4">
                    <span className={`text-sm font-mono font-bold ${(trade.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {(trade.pnl || 0) >= 0 ? '+' : ''}{(trade.pnl || 0).toLocaleString()}
                    </span>
                  </td>
                  <td className="px-4 sm:px-6 py-4 text-xs text-gray-500">
                    <span className="px-2 py-0.5 bg-gray-100 rounded text-[10px] font-bold uppercase tracking-tight">
                      {trade.exit_reason || 'N/A'}
                    </span>
                  </td>
                  <td className="px-4 sm:px-6 py-4 text-xs text-gray-400">
                    {new Date(trade.opened_at).toLocaleDateString()}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="px-4 sm:px-6 py-12 text-center text-gray-400 text-sm">
                  No trade history yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile Card Layout - Shown on mobile */}
      <div className="block md:hidden">
        {filteredHistory && filteredHistory.length > 0 ? (
          <div className="space-y-0">
            {filteredHistory.map((trade, idx) => (
              <div key={trade.id} className={`p-4 fade-in ${idx < filteredHistory.length - 1 ? 'border-b border-gray-100' : ''}`}>
                <div className="flex justify-between items-start gap-3 mb-3">
                  <div>
                    <h3 className="font-bold text-base text-gray-900">{trade.symbol}</h3>
                    <p className={`text-xs font-bold uppercase mt-1 ${trade.side === 'long' ? 'text-green-600' : 'text-red-600'}`}>
                      {trade.side}
                    </p>
                  </div>
                  <span
                    className={`text-sm font-mono font-bold ${
                      (trade.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {(trade.pnl || 0) >= 0 ? '+' : ''}{(trade.pnl || 0).toLocaleString()}
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs bg-gray-50 rounded-lg p-2.5">
                    <span className="text-gray-500 font-bold uppercase">Entry</span>
                    <span className="font-mono font-bold text-gray-900">{trade.entry_price.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs bg-gray-50 rounded-lg p-2.5">
                    <span className="text-gray-500 font-bold uppercase">Exit</span>
                    <span className="font-mono font-bold text-gray-900">{trade.exit_price?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs bg-gray-50 rounded-lg p-2.5">
                    <span className="text-gray-500 font-bold uppercase">Reason</span>
                    <span className="font-bold text-gray-700 uppercase">{trade.exit_reason || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs bg-gray-50 rounded-lg p-2.5">
                    <span className="text-gray-500 font-bold uppercase">Date</span>
                    <span className="text-gray-600">{new Date(trade.opened_at).toLocaleDateString()}</span>
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-gray-400 text-sm">No trade history</p>
            <p className="text-gray-300 text-xs mt-1">Closed trades will appear here</p>
          </div>
        )}
      </div>
    </div>
  )
}
