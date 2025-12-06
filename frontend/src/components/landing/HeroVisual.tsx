'use client';

import { motion } from 'framer-motion';
import { FileText, Brain, Zap, Shield } from 'lucide-react';

export function HeroVisual() {
  return (
    <div className="relative w-full h-[500px] flex items-center justify-center">
      {/* Central Glowing Circle */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8 }}
        className="absolute w-64 h-64 rounded-full bg-linear-to-br from-cyber-cyan to-cyber-blue opacity-20 blur-3xl"
      />
      
      {/* Orbiting Icons */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="relative w-80 h-80"
      >
        {/* Icon 1 - Top */}
        <motion.div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-16 h-16 rounded-2xl bg-linear-to-br from-cyber-cyan to-cyber-blue flex items-center justify-center shadow-lg shadow-cyber-cyan/50"
          whileHover={{ scale: 1.2, rotate: 360 }}
        >
          <FileText className="w-8 h-8 text-white" />
        </motion.div>
        
        {/* Icon 2 - Right */}
        <motion.div
          className="absolute top-1/2 right-0 -translate-y-1/2 w-16 h-16 rounded-2xl bg-linear-to-br from-cyber-blue to-purple-500 flex items-center justify-center shadow-lg shadow-cyber-blue/50"
          whileHover={{ scale: 1.2, rotate: 360 }}
        >
          <Brain className="w-8 h-8 text-white" />
        </motion.div>
        
        {/* Icon 3 - Bottom */}
        <motion.div
          className="absolute bottom-0 left-1/2 -translate-x-1/2 w-16 h-16 rounded-2xl bg-linear-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/50"
          whileHover={{ scale: 1.2, rotate: 360 }}
        >
          <Zap className="w-8 h-8 text-white" />
        </motion.div>
        
        {/* Icon 4 - Left */}
        <motion.div
          className="absolute top-1/2 left-0 -translate-y-1/2 w-16 h-16 rounded-2xl bg-linear-to-br from-cyber-teal to-emerald-500 flex items-center justify-center shadow-lg shadow-cyber-teal/50"
          whileHover={{ scale: 1.2, rotate: 360 }}
        >
          <Shield className="w-8 h-8 text-white" />
        </motion.div>
      </motion.div>
      
      {/* Center Logo/Icon */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
        className="absolute w-24 h-24 rounded-3xl bg-linear-to-br from-cyber-cyan via-cyber-blue to-purple-500 flex items-center justify-center shadow-2xl shadow-cyber-cyan/50"
      >
        <div className="text-4xl font-bold text-white">AI</div>
      </motion.div>
      
      {/* Connecting Lines */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <motion.circle
          cx="50%"
          cy="50%"
          r="160"
          fill="none"
          stroke="url(#gradient)"
          strokeWidth="2"
          strokeDasharray="10 5"
          initial={{ strokeDashoffset: 0 }}
          animate={{ strokeDashoffset: 1000 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        />
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.5" />
            <stop offset="50%" stopColor="#3B82F6" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.5" />
          </linearGradient>
        </defs>
      </svg>
      
      {/* Floating Particles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 rounded-full bg-cyber-cyan"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`, 
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}
    </div>
  );
}