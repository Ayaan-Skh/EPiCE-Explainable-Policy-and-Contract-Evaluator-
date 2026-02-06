'use client';

import { useState } from 'react';
import { Button } from '@/src/components/ui/Button';
import { Card } from '@/src/components/ui/Card';
import { AnimatedBackground } from '@/src/components/landing/AnimatedBackground';
import { ArrowLeft, Send, Loader2, CheckCircle, XCircle } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { apiClient, BatchQueryResponse } from '@/src/lib/api';

export default function BatchPage() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BatchQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    const queries = text
      .split('\n')
      .map((q) => q.trim())
      .filter((q) => q.length >= 5);
    if (queries.length === 0) {
      setError('Enter at least one query (min 5 chars per line).');
      return;
    }
    if (queries.length > 50) {
      setError('Maximum 50 queries per batch.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await apiClient.batchQuery(queries, 3);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Batch query failed');
    } finally {
      setLoading(false);
    }
  };

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
        <span className="text-xl font-bold text-white">Batch Query</span>
      </nav>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">Batch Query Processing</h1>
          <p className="text-gray-400">One query per line (5–50 queries)</p>
        </motion.div>

        {error && (
          <Card className="p-4 bg-rose-500/10 border-rose-500/30 text-rose-500 mb-6">{error}</Card>
        )}

        <Card glass className="p-6 mb-6">
          <label className="block text-sm font-medium text-gray-400 mb-2">Queries</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="46 year old male, knee surgery in Pune, 3 months policy&#10;35F hip replacement Mumbai 8 month policy"
            className="w-full h-40 px-4 py-3 rounded-lg bg-cyber-navy/50 border border-cyber-cyan/20 text-white placeholder-gray-500 focus:border-cyber-cyan/50 focus:outline-none resize-y"
            disabled={loading}
          />
          <div className="mt-4 flex justify-end">
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Run Batch
                </>
              )}
            </Button>
          </div>
        </Card>

        {result && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <Card glass className="p-6 border border-cyber-cyan/20">
              <h3 className="text-lg font-semibold text-white mb-4">Summary</h3>
              <p className="text-cyber-cyan">
                Processed {result.total} queries in {result.total_time_seconds.toFixed(2)}s (avg{' '}
                {result.avg_time_seconds.toFixed(2)}s each)
              </p>
            </Card>
            <div className="space-y-2">
              {result.results.map((r: Record<string, unknown>, i: number) => {
                const approved = (r.decision as { approved?: boolean })?.approved;
                const query = (r.query as string) || '';
                return (
                  <Card key={i} className="p-4 flex items-center justify-between gap-4">
                    <span className="text-gray-300 truncate flex-1">{query}</span>
                    {approved !== undefined ? (
                      approved ? (
                        <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />
                      ) : (
                        <XCircle className="w-5 h-5 text-rose-500 shrink-0" />
                      )
                    ) : (
                      <span className="text-rose-500 text-sm">Error</span>
                    )}
                  </Card>
                );
              })}
            </div>
          </motion.div>
        )}
      </div>
    </main>
  );
}
