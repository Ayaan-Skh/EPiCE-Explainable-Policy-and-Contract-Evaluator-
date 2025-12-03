'use client';

import { Card } from '@/src/components/ui/Card';
import { CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

interface ResultCardProps {
    result: any;
}

export function ResultCard({ result }: ResultCardProps) {
    const { decision, parsed_query, processing_time_seconds } = result;
    const isApproved = decision.approved;

    return (
        <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            <Card
                glass
                className={`p-6 sm:p-8 border-2 ${isApproved
                        ? 'border-emerald-500/50 bg-emerald-500/5'
                        : 'border-rose-500/50 bg-rose-500/5'
                    }`}
            >
                {/* Status Header */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
                    <div className="flex items-center gap-3">
                        {isApproved ? (
                            <CheckCircle className="w-10 h-10 sm:w-12 sm:h-12 text-emerald-500" />
                        ) : (
                            <XCircle className="w-10 h-10 sm:w-12 sm:h-12 text-rose-500" />
                        )}
                        <div>
                            <h2 className="text-2xl sm:text-3xl font-bold text-white">
                                {isApproved ? 'Claim Approved' : 'Claim Rejected'}
                            </h2>
                            <p className="text-sm sm:text-base text-gray-400">
                                Confidence: <span className="text-cyber-cyan capitalize">{decision.confidence}</span>
                            </p>
                        </div>
                    </div>

                    {decision.amount && (
                        <div className="text-left sm:text-right">
                            <p className="text-sm text-gray-500">Approved Amount</p>
                            <p className="text-2xl sm:text-3xl font-bold text-cyber-cyan">
                                ₹{decision.amount.toLocaleString()}
                            </p>
                        </div>
                    )}
                </div>

                {/* Parsed Query Info */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6 p-4 bg-cyber-navy/30 rounded-xl">
                    <div>
                        <p className="text-xs text-gray-500">Age</p>
                        <p className="text-base sm:text-lg font-semibold text-white">{parsed_query.age || 'N/A'}</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Gender</p>
                        <p className="text-base sm:text-lg font-semibold text-white capitalize">{parsed_query.gender || 'N/A'}</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Procedure</p>
                        <p className="text-base sm:text-lg font-semibold text-white capitalize">{parsed_query.procedure || 'N/A'}</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Location</p>
                        <p className="text-base sm:text-lg font-semibold text-white">{parsed_query.location || 'N/A'}</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Policy Duration</p>
                        <p className="text-base sm:text-lg font-semibold text-white">{parsed_query.policy_duration_months || 'N/A'} months</p>
                    </div>
                </div>

                {/* Reasoning */}
                <div className="mb-6">
                    <h3 className="text-lg sm:text-xl font-semibold text-white mb-3 flex items-center gap-2">
                        <span className="w-1 h-6 bg-linear-to-b from-cyber-cyan to-cyber-blue rounded-full"></span>
                        Decision Reasoning
                    </h3>
                    <p className="text-sm sm:text-base text-gray-300 leading-relaxed">
                        {decision.reasoning}
                    </p>
                </div>

                {/* Relevant Clauses */}
                <div className="mb-6">
                    <h3 className="text-lg sm:text-xl font-semibold text-white mb-3">
                        Referenced Policy Sections
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {decision.relevant_clauses.map((clause: string, index: number) => (
                            <span
                                key={index}
                                className="px-3 py-1.5 bg-cyber-cyan/10 border border-cyber-cyan/30 rounded-lg text-xs sm:text-sm text-cyber-cyan font-medium"
                            >
                                {clause}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Risk Factors */}
                {decision.risk_factors && decision.risk_factors.length > 0 && (
                    <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl">
                        <div className="flex items-start gap-2">
                            <AlertTriangle className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
                            <div>
                                <h4 className="text-base font-semibold text-yellow-500 mb-2">Risk Factors</h4>
                                <ul className="space-y-1">
                                    {decision.risk_factors.map((risk: string, index: number) => (
                                        <li key={index} className="text-sm text-gray-300">• {risk}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                )}

                {/* Processing Time */}
                <div className="mt-6 pt-6 border-t border-white/10 flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        <span>Processed in {processing_time_seconds}s</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        <span>AI Analysis Complete</span>
                    </div>
                </div>
            </Card>
        </motion.div>
    );
}