'use client';

import { Card } from '@/src/components/ui/Card';
import { FileText, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';

interface Clause {
  text: string;
  section: string;
  similarity: number;
}

interface ClauseViewerProps {
  clauses: Clause[];
}

export function ClauseViewer({ clauses }: ClauseViewerProps) {
  return (
    <div>
      <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4 sm:mb-6 flex items-center gap-3">
        <FileText className="w-6 h-6 sm:w-8 sm:h-8 text-cyber-cyan" />
        Retrieved Policy Clauses
      </h2>
      
      <div className="space-y-4">
        {clauses.map((clause, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card glass className="p-4 sm:p-6 hover:border-cyber-cyan/50 transition-all">
              <div className="flex flex-col sm:flex-row justify-between items-start gap-3 mb-3">
                <h3 className="text-base sm:text-lg font-semibold text-cyber-cyan">
                  {clause.section}
                </h3>
                <div className="flex items-center gap-2 px-3 py-1 bg-cyber-cyan/10 rounded-lg">
                  <TrendingUp className="w-4 h-4 text-cyber-cyan" />
                  <span className="text-sm font-semibold text-cyber-cyan">
                    {(clause.similarity * 100).toFixed(0)}% Match
                  </span>
                </div>
              </div>
              <p className="text-sm sm:text-base text-gray-300 leading-relaxed">
                {clause.text}
              </p>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}