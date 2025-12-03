'use client';

import { useState } from 'react';
import { Button } from '@/src/components/ui/Button';
import { Card } from '@/src/components/ui/Card';
import { AnimatedBackground } from '@/src/components/landing/AnimatedBackground';
import { ArrowLeft, Send, Loader2, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { QueryInput } from '@/src/components/query/QueryInput';
import { ResultCard } from '@/src/components/query/ResultCard';
import { ClauseViewer } from '@/src/components/query/ClauseViewer';

export default function QueryPage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    
    // Simulate API call (replace with actual API later)
    setTimeout(() => {
      setResult({
        query: query,
        parsed_query: {
          age: 46,
          gender: 'male',
          procedure: 'knee surgery',
          location: 'Pune',
          policy_duration_months: 3,
          is_emergency: false,
        },
        decision: {
          approved: true,
          amount: 150000,
          reasoning: 'Claim approved based on age eligibility (46 years within 18-50 range), sufficient policy duration (3 months meets minimum requirement for elective surgery), covered procedure (knee surgery at 80% coverage), and Pune is a Tier 1 city with 100% network coverage.',
          relevant_clauses: ['SECTION 2: SURGICAL COVERAGE', 'SECTION 3: GEOGRAPHIC COVERAGE', 'SECTION 4: AGE ELIGIBILITY'],
          confidence: 'high',
          risk_factors: [],
        },
        retrieved_clauses: [
          {
            text: 'Knee surgery, hip replacement, and spinal procedures are covered at 80% of actual hospital bills. Coverage begins after 3 months of active policy for accident-related cases.',
            section: 'SURGICAL COVERAGE AND BENEFITS',
            similarity: 0.92,
          },
          {
            text: 'Treatment in network hospitals in Pune, Mumbai, Bangalore, and Delhi are covered at 100% of scheduled amounts.',
            section: 'GEOGRAPHIC COVERAGE',
            similarity: 0.88,
          },
          {
            text: 'Policyholders aged 18-50 are eligible for all surgical procedures without additional screening.',
            section: 'AGE ELIGIBILITY',
            similarity: 0.85,
          },
        ],
        processing_time_seconds: 2.34,
      });
      setLoading(false);
    }, 2000);
  };

  const handleReset = () => {
    setQuery('');
    setResult(null);
  };

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
        
        <div className="w-20"></div>
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
            disabled={loading}
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
        {!result && !loading && (
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