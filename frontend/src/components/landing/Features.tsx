'use client';

import { Brain, Zap, Shield, TrendingUp } from 'lucide-react';
import { Card } from '@/src/components/ui/Card';
import { motion } from 'framer-motion';

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Analysis',
    description: 'Advanced LLM technology analyzes policies with human-level understanding',
    color: 'from-cyber-cyan to-cyber-blue',
  },
  {
    icon: Zap,
    title: 'Instant Decisions',
    description: 'Get claim approvals in seconds, not hours. Sub-3 second processing time',
    color: 'from-cyber-blue to-purple-500',
  },
  {
    icon: Shield,
    title: 'Explainable AI',
    description: 'Every decision backed by specific policy clauses and transparent reasoning',
    color: 'from-cyber-teal to-emerald-500',
  },
  {
    icon: TrendingUp,
    title: '80%+ Accuracy',
    description: 'Industry-leading accuracy in entity extraction and decision making',
    color: 'from-purple-500 to-pink-500',
  },
];

export function Features() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {features.map((feature, index) => (
        <motion.div
          key={feature.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <Card glass glow className="h-full hover:scale-105 cursor-pointer group">
            <div className={`w-12 h-12 rounded-xl bg-linear-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:animate-glow`}>
              <feature.icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
            <p className="text-gray-400 text-sm">{feature.description}</p>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}