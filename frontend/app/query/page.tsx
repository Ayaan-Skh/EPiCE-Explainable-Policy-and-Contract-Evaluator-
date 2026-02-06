'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/src/components/ui/Button';
import { Card } from '@/src/components/ui/Card';
import { AnimatedBackground } from '@/src/components/landing/AnimatedBackground';
import { ArrowLeft, Send, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { QueryInput } from '@/src/components/query/QueryInput';
import { ResultCard } from '@/src/components/query/ResultCard';
import { ClauseViewer } from '@/src/components/query/ClauseViewer';
import { apiClient, QueryResponse } from '@/src/lib/api';

export default function QueryPage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [systemReady, setSystemReady] = useState(false);
  const [checkingStatus, setCheckingStatus] = useState(true);

  // Check system status on mount
  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const status = await apiClient.getStatus();
      setSystemReady(status.is_setup);
      setCheckingStatus(false);
    } catch (err) {
      console.error('Failed to check status:', err);
      setError('Failed to connect to backend. Make sure the API server is running on port 8000.');
      setCheckingStatus(false);
    }
  };

  const handleSubmit = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.processQuery({
        query: query,
        top_k: 3
      });
      
      setResult(response);
    } catch (err: any) {
      console.error('Query error:', err);
      setError(err.message || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setQuery('');
    setResult(null);
    setError(null);
  };

  if (checkingStatus) {
    return (
      <main className="min-h-screen bg-gradient-dark relative overflow-hidden flex items-center justify-center">
        <AnimatedBackground />
        <Card glass className="p-8 text-center">
          <Loader2 className="w-12 h-12 text-cyber-cyan animate-spin mx-auto mb-4" />
          <p className="text-white">Checking system status...</p>
        </Card>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-dark relative overflow-hidden">
      <AnimatedBackground />
      
      {/* Navigation */}
      <nav className="relative z-10 flex justify-between items-center px-4 sm:px-8 py-6">
        <Link href="/">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
        </Link>
        
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-linear-to-br from-cyber-cyan to-cyber-blue flex items-center justify-center">
            <Sparkles className="w-4 h-4 sm:w-6 sm:h-6 text-white" />
          </div>
          <span className="text-xl sm:text-2xl font-bold text-white">EPiCE</span>
        </div>
        
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${systemReady ? 'bg-emerald-500' : 'bg-rose-500'} animate-pulse`}></div>
          <span className="text-xs text-gray-400 hidden sm:block">
            {systemReady ? 'Ready' : 'Not Setup'}
          </span>
        </div>
      </nav>
      
      {/* Main Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-8 py-8 sm:py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8 sm:mb-12"
        >
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-3 sm:mb-4">
            Insurance Claim Analyzer
          </h1>
          <p className="text-base sm:text-lg text-gray-400">
            Enter your claim details to get instant AI-powered analysis
          </p>
        </motion.div>
        
        {/* System Not Ready Warning */}
        {!systemReady && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <Card className="p-4 bg-yellow-500/10 border-yellow-500/30">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-yellow-500 font-semibold mb-1">System Not Setup</p>
                  <p className="text-sm text-gray-300">
                    Please upload a policy document first or run the setup command.
                  </p>
                  <Link href="/upload">
                    <Button variant="outline" size="sm" className="mt-3">
                      Upload Document
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
        
        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <Card className="p-4 bg-rose-500/10 border-rose-500/30">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-rose-500 font-semibold mb-1">Error</p>
                  <p className="text-sm text-gray-300">{error}</p>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
        
        {/* Query Input */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <QueryInput
            value={query}
            onChange={setQuery}
            onSubmit={handleSubmit}
            loading={loading}
            disabled={loading || !systemReady}
          />
        </motion.div>
        
        {/* Loading State */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-8 sm:mt-12"
          >
            <Card glass className="text-center py-12 sm:py-16">
              <Loader2 className="w-12 h-12 sm:w-16 sm:h-16 text-cyber-cyan animate-spin mx-auto mb-4" />
              <p className="text-lg sm:text-xl text-white font-semibold">Analyzing your claim...</p>
              <p className="text-sm sm:text-base text-gray-400 mt-2">This usually takes 2-3 seconds</p>
            </Card>
          </motion.div>
        )}
        
        {/* Results */}
        {result && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 sm:mt-12 space-y-6 sm:space-y-8"
          >
            {/* Decision Card */}
            <ResultCard result={result} />
            
            {/* Clause Viewer */}
            <ClauseViewer clauses={result.retrieved_clauses} />
            
            {/* Reset Button */}
            <div className="text-center">
              <Button onClick={handleReset} variant="outline">
                Analyze Another Claim
              </Button>
            </div>
          </motion.div>
        )}
        
        {/* Example Queries */}
        {!result && !loading && systemReady && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-8 sm:mt-12"
          >
            <h3 className="text-lg sm:text-xl font-semibold text-white mb-4 text-center">
              Try these examples:
            </h3>
            <div className="grid sm:grid-cols-2 gap-3 sm:gap-4 max-w-4xl mx-auto">
              {[
                '46 year old male, knee surgery in Pune, 3 month policy',
                '35F hip replacement Mumbai 8 month policy',
                '28M emergency cardiac surgery Delhi 1 month',
                '42F cataract surgery Chennai 12 month policy',
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(example)}
                  className="text-left p-3 sm:p-4 rounded-xl bg-cyber-gray/50 border border-cyber-cyan/20 hover:border-cyber-cyan/50 hover:bg-cyber-gray/70 transition-all text-sm sm:text-base text-gray-300 hover:text-white"
                >
                  {example}
                </button>
              ))}
            </div>
          </motion.div>
          
        )}
        
      </div>
      
    </main>
  );
}
