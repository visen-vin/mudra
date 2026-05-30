import React from 'react'

export default function HistoryTable({ history, isLoading, isError }) {
  const [filter, setFilter] = React.useState({ market: 'all', side: 'all' })

  if (isLoading) return <div className="p-4">Loading history...</div>
  if (isError) return <div className="p-4 text-red-500">Error loading history</div>

  const filteredHistory = history?.filter(trade => {
    const marketMatch = filter.market === 'all' || trade.market === filter.market
    const sideMatch = filter.side === 'all' || trade.side === filter.side
    return marketMatch && sideMatch
  })

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-gray-50/50">
        <h2 className="text-lg font-bold text-gray-800">Trade History</h2>
        <div className="flex gap-2">
          <select 
            value={filter.market} 
            onChange={(e) => setFilter(f => ({ ...f, market: e.target.value }))}
            className="text-xs border rounded-lg px-2 py-1 bg-white outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Markets</option>
            <option value="crypto">Crypto</option>
            <option value="indian_equity">Equity</option>
          </select>
          <select 
            value={filter.side} 
            onChange={(e) => setFilter(f => ({ ...f, side: e.target.value }))}
            className="text-xs border rounded-lg px-2 py-1 bg-white outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Sides</option>
            <option value="long">Long</option>
            <option value="short">Short</option>
          </select>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-50 text-[10px] uppercase font-bold text-gray-500 tracking-wider">
            <tr>
              <th className="px-6 py-3">Symbol</th>
              <th className="px-6 py-3">Side</th>
              <th className="px-6 py-3">Entry/Exit</th>
              <th className="px-6 py-3">PnL</th>
              <th className="px-6 py-3">Reason</th>
              <th className="px-6 py-3">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredHistory && filteredHistory.length > 0 ? (
              filteredHistory.map(trade => (
                <tr key={trade.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <span className="font-bold text-gray-900">{trade.symbol}</span>
                  </td>
                  <td className="px-6 py-4 text-xs font-bold">
                    <span className={trade.side === 'long' ? 'text-green-600' : 'text-red-600'}>
                      {trade.side.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-mono text-gray-700">
                      {trade.entry_price.toLocaleString()} → {trade.exit_price?.toLocaleString()}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-sm font-mono font-bold ${(trade.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {(trade.pnl || 0) >= 0 ? '+' : ''}{(trade.pnl || 0).toLocaleString()}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-gray-500">
                    <span className="px-2 py-0.5 bg-gray-100 rounded text-[10px] font-bold uppercase tracking-tight">
                      {trade.exit_reason || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-gray-400">
                    {new Date(trade.opened_at).toLocaleDateString()}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-gray-400 text-sm italic">
                  No trade history yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
