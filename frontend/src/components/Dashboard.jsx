import React, { useState, useMemo } from 'react'
import { usePositions, useHistory, useSettings, usePrices } from '../hooks/useApi'
import { api } from '../lib/api'
import OpenPositions from './OpenPositions'
import ManualTradeForm from './ManualTradeForm'
import HistoryTable from './HistoryTable'

export default function Dashboard() {
  const { positions, isLoading: posLoading, isError: posError, mutate: mutatePositions } = usePositions()
  const { history, isLoading: histLoading, isError: histError, mutate: mutateHistory } = useHistory()
  const { settings, isError: settingsError, mutate: mutateSettings } = useSettings()
  
  // Extract symbols from open positions to fetch prices
  const symbols = useMemo(() => {
    const s = new Set(['BTCUSDT', 'ETHUSDT']) // Default watchlist
    if (positions) {
      positions.forEach(p => s.add(p.symbol))
    }
    return Array.from(s)
  }, [positions])

  const { prices, isError: pricesError } = usePrices(symbols)

  const hasError = posError || histError || settingsError || pricesError

  const handleOrderPlaced = () => {
    mutatePositions()
  }

  const handleRefresh = () => {
    mutatePositions()
    mutateHistory()
    mutateSettings()
  }

  const toggleMode = async () => {
    const newMode = settings?.mode === 'paper' ? 'live' : 'paper'
    if (newMode === 'live' && !window.confirm('WARNING: Live mode enabled. Real orders will be executed. Continue?')) return
    try {
      await api.settings.update(newMode)
      mutateSettings()
    } catch (error) {
      alert('Error updating settings: ' + error.message)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans pb-12">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            <div className="flex items-center gap-2 min-w-0 flex-shrink-0">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-white font-black text-lg sm:text-xl">M</span>
              </div>
              <h1 className="text-base sm:text-xl font-black tracking-tight text-gray-800 hidden xs:block">MUDRA</h1>
            </div>

            <div className="flex items-center gap-2 sm:gap-4">
              <button
                onClick={toggleMode}
                className={`tap-target px-2 sm:px-3 py-1.5 rounded-full text-[10px] sm:text-xs font-bold transition-all border ${
                  settings?.mode === 'live'
                    ? 'bg-red-50 text-red-600 border-red-100 hover:bg-red-100'
                    : 'bg-green-50 text-green-600 border-green-100 hover:bg-green-100'
                }`}
              >
                <span className="hidden sm:inline">{settings?.mode?.toUpperCase() || 'PAPER'} MODE</span>
                <span className="sm:hidden">{settings?.mode?.charAt(0).toUpperCase() || 'P'}</span>
              </button>
              <button
                onClick={handleRefresh}
                className="tap-target p-2 text-gray-400 hover:text-gray-600 transition-colors active:scale-95"
                aria-label="Refresh data"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Prices Bar - Mobile scrollable */}
        <div className="bg-gray-900 py-2 overflow-x-auto no-scrollbar whitespace-nowrap px-3 sm:px-4 border-t border-gray-800">
          <div className="flex gap-4 sm:gap-6 text-[10px] sm:text-[11px] font-mono">
            {symbols.map(s => (
              <div key={s} className="flex gap-2 items-center flex-shrink-0">
                <span className="text-gray-500 font-bold">{s}</span>
                <span className="text-blue-400 font-bold">
                  {prices?.[s]?.toLocaleString() || '---'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 mt-4 sm:mt-6">
        {hasError && (
          <div className="mb-4 sm:mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex flex-col sm:flex-row items-start sm:items-center gap-3 text-red-700 shadow-sm fade-in">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-500 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold">API Connection Error</p>
              <p className="text-xs opacity-80">Unable to fetch latest data. Please check if the backend service is running.</p>
            </div>
            <button
              onClick={handleRefresh}
              className="tap-target px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 text-xs font-bold rounded-lg transition-colors active:scale-95 flex-shrink-0"
            >
              RETRY
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-8 space-y-4 sm:space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 items-start">
              {/* Left column on tablet/desktop: Form */}
              <div className="space-y-4 sm:space-y-6">
                <ManualTradeForm onOrderPlaced={handleOrderPlaced} currentMode={settings?.mode} />
              </div>

              {/* Right column on tablet/desktop: Positions */}
              <div className="space-y-4 sm:space-y-6">
                <OpenPositions
                  positions={positions}
                  isLoading={posLoading}
                  onUpdate={handleRefresh}
                />
              </div>
            </div>

            {/* Bottom area: History */}
            <HistoryTable history={history} isLoading={histLoading} />
          </div>

          {/* Sidebar Area - Responsive */}
          <div className="lg:col-span-4 space-y-4 sm:space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 fade-in">
              <h2 className="text-base sm:text-lg font-bold text-gray-800 mb-4">Portfolio Summary</h2>
              <div className="space-y-3 sm:space-y-4">
                <div className="flex justify-between items-center p-3 sm:p-4 bg-blue-50 rounded-xl border border-blue-100">
                  <span className="text-xs sm:text-sm font-bold text-blue-700">Account Balance</span>
                  <span className="text-base sm:text-lg font-mono font-black text-blue-900">₹1,000,000</span>
                </div>
                <div className="grid grid-cols-2 gap-3 sm:gap-4">
                  <div className="p-3 sm:p-4 bg-gray-50 rounded-xl border border-gray-100">
                    <p className="text-[9px] sm:text-[10px] font-bold text-gray-500 uppercase">Daily PnL</p>
                    <p className="text-xs sm:text-sm font-mono font-bold text-green-600 mt-1">+₹12,450</p>
                  </div>
                  <div className="p-3 sm:p-4 bg-gray-50 rounded-xl border border-gray-100">
                    <p className="text-[9px] sm:text-[10px] font-bold text-gray-500 uppercase">Win Rate</p>
                    <p className="text-xs sm:text-sm font-mono font-bold text-gray-700 mt-1">64%</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl shadow-lg p-4 sm:p-6 text-white overflow-hidden relative fade-in">
              <div className="relative z-10">
                <h3 className="font-bold text-base sm:text-lg mb-2">Need Help?</h3>
                <p className="text-xs sm:text-sm text-gray-300 mb-3 sm:mb-4">Check the strategy guide for better trade execution.</p>
                <button className="tap-target bg-white text-gray-900 text-xs font-bold px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors active:scale-95">
                  READ GUIDE
                </button>
              </div>
              <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-blue-600 rounded-full opacity-20 blur-xl"></div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
