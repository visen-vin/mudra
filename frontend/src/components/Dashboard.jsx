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
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xl">M</span>
              </div>
              <h1 className="text-xl font-black tracking-tight text-gray-800">MUDRA</h1>
            </div>
            
            <div className="flex items-center gap-4">
              <button 
                onClick={toggleMode}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all border ${
                  settings?.mode === 'live' 
                    ? 'bg-red-50 text-red-600 border-red-100 hover:bg-red-100' 
                    : 'bg-green-50 text-green-600 border-green-100 hover:bg-green-100'
                }`}
              >
                {settings?.mode?.toUpperCase() || 'PAPER'} MODE
              </button>
              <button onClick={handleRefresh} className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        {/* Prices Bar */}
        <div className="bg-gray-900 py-1.5 overflow-x-auto no-scrollbar whitespace-nowrap px-4 border-t border-gray-800">
          <div className="max-w-7xl mx-auto flex gap-6 text-[11px] font-mono">
            {symbols.map(s => (
              <div key={s} className="flex gap-2 items-center">
                <span className="text-gray-500 font-bold">{s}</span>
                <span className="text-blue-400 font-bold">
                  {prices?.[s]?.toLocaleString() || '---'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        {hasError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700 shadow-sm animate-in fade-in slide-in-from-top-4 duration-300">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-bold">API Connection Error</p>
              <p className="text-xs opacity-80">Unable to fetch latest data. Please check if the backend service is running.</p>
            </div>
            <button 
              onClick={handleRefresh}
              className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 text-xs font-bold rounded-lg transition-colors"
            >
              RETRY
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-8 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
               {/* Left column on tablet/desktop: Form */}
               <div className="space-y-6">
                 <ManualTradeForm onOrderPlaced={handleOrderPlaced} currentMode={settings?.mode} />
               </div>

               {/* Right column on tablet/desktop: Positions */}
               <div className="space-y-6">
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

          {/* Sidebar Area (e.g. for Stats or Settings) */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Portfolio Summary</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-xl border border-blue-100">
                  <span className="text-sm font-bold text-blue-700">Account Balance</span>
                  <span className="text-lg font-mono font-black text-blue-900">₹1,000,000</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
                    <p className="text-[10px] font-bold text-gray-500 uppercase">Daily PnL</p>
                    <p className="text-sm font-mono font-bold text-green-600">+₹12,450</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
                    <p className="text-[10px] font-bold text-gray-500 uppercase">Win Rate</p>
                    <p className="text-sm font-mono font-bold text-gray-700">64%</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl shadow-lg p-6 text-white overflow-hidden relative">
              <div className="relative z-10">
                <h3 className="font-bold mb-2">Need Help?</h3>
                <p className="text-sm text-gray-300 mb-4">Check the strategy guide for better trade execution.</p>
                <button className="bg-white text-gray-900 text-xs font-bold px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors">
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
