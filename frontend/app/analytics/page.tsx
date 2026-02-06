'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/src/components/ui/Button';
import { Card } from '@/src/components/ui/Card';
import { AnimatedBackground } from '@/src/components/landing/AnimatedBackground';
import { ArrowLeft, BarChart3, TrendingUp, Clock, Zap } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { apiClient, AnalyticsResponse } from '@/src/lib/api';

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .getAnalytics()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-gradient-dark relative overflow-hidden">
      <AnimatedBackground />
      <nav className="relative z-10 flex justify-between items-center px-4 sm:px-8 py-6">
        <Link href="/">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
        </Link>
        <span className="text-xl font-bold text-white">Analytics</span>
      </nav>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2 flex items-center justify-center gap-2">
            <BarChart3 className="w-8 h-8 text-cyber-cyan" />
            Analytics Dashboard
          </h1>
          <p className="text-gray-400">Query stats and performance</p>
        </motion.div>

        {error && (
          <Card className="p-4 bg-rose-500/10 border-rose-500/30 text-rose-500 mb-6">
            {error}
          </Card>
        )}

        {loading && (
          <Card glass className="p-12 text-center">
            <p className="text-white">Loading analytics...</p>
          </Card>
        )}

        {data && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid sm:grid-cols-2 gap-4 sm:gap-6"
          >
            <Card glass className="p-6 border border-cyber-cyan/20">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-8 h-8 text-cyber-cyan" />
                <h2 className="text-lg font-semibold text-white">Total Queries</h2>
              </div>
              <p className="text-3xl font-bold text-cyber-cyan">{data.total_queries}</p>
            </Card>

            <Card glass className="p-6 border border-cyber-cyan/20">
              <div className="flex items-center gap-3 mb-4">
                <BarChart3 className="w-8 h-8 text-cyber-blue" />
                <h2 className="text-lg font-semibold text-white">Approval Rate</h2>
              </div>
              <p className="text-3xl font-bold text-cyber-blue">{data.approval_rate}%</p>
              <p className="text-sm text-gray-400 mt-1">
                {data.approved_count} approved / {data.rejected_count} rejected
              </p>
            </Card>

            <Card glass className="p-6 border border-cyber-cyan/20">
              <div className="flex items-center gap-3 mb-4">
                <Clock className="w-8 h-8 text-cyber-teal" />
                <h2 className="text-lg font-semibold text-white">Avg Processing Time</h2>
              </div>
              <p className="text-3xl font-bold text-cyber-teal">
                {data.avg_processing_time_seconds.toFixed(2)}s
              </p>
            </Card>

            <Card glass className="p-6 border border-cyber-cyan/20">
              <div className="flex items-center gap-3 mb-4">
                <Zap className="w-8 h-8 text-amber-400" />
                <h2 className="text-lg font-semibold text-white">Cache</h2>
              </div>
              <p className="text-3xl font-bold text-amber-400">{data.cache_hits} hits</p>
              <p className="text-sm text-gray-400 mt-1">Cache size: {data.cache_size}</p>
            </Card>
          </motion.div>
        )}

        {data && data.total_queries === 0 && !loading && (
          <Card glass className="p-8 text-center">
            <p className="text-gray-400">No queries yet. Run some queries to see analytics.</p>
            <Link href="/query" className="mt-4 inline-block">
              <Button>Go to Query</Button>
            </Link>
          </Card>
        )}
      </div>
    </main>
  );
}
