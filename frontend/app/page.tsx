'use client';

import { Button } from '@/src/components/ui/Button';
import { AnimatedBackground } from '@/src/components/landing/AnimatedBackground';
import { HeroVisual } from '@/src/components/landing/HeroVisual';
import { Features } from '@/src/components/landing/Features';
import { ArrowRight, Sparkles, Menu } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useState } from 'react';

export default function Home() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <main className="min-h-screen bg-linear-dark relative overflow-hidden">
      <AnimatedBackground />
      
      {/* Navigation */}
      <nav className="relative z-10 flex justify-between items-center px-4 sm:px-8 py-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-2"
        >
          <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-linear-to-br from-cyber-cyan to-cyber-blue flex items-center justify-center">
            <Sparkles className="w-4 h-4 sm:w-6 sm:h-6 text-white" />
          </div>
          <span className="text-xl sm:text-2xl font-bold text-white">EPiCE</span>
        </motion.div>
        
        {/* Desktop Nav */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="hidden sm:block"
        >
          <Link href="/query">
            <Button variant="outline" size="sm">
              Try Demo
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </motion.div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="sm:hidden text-white p-2"
        >
          <Menu className="w-6 h-6" />
        </button>
      </nav>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="sm:hidden absolute top-20 right-4 z-20 bg-cyber-gray/95 backdrop-blur-lg rounded-xl p-4 border border-cyber-cyan/30"
        >
          <Link href="/query" onClick={() => setMobileMenuOpen(false)}>
            <Button variant="outline" size="sm" className="w-full">
              Try Demo
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </motion.div>
      )}
      
      {/* Hero Section */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-8 py-12 sm:py-20">
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left: Text Content */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-6 sm:space-y-8 order-2 lg:order-1"
          >
            <div className="inline-block px-3 sm:px-4 py-1.5 sm:py-2 rounded-full bg-cyber-cyan/10 border border-cyber-cyan/30 text-cyber-cyan text-xs sm:text-sm font-semibold mb-4">
              Next-Gen Insurance Processing
            </div>
            
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white leading-tight">
              Explainable
              <br />
              <span className="bg-linear-to-r from-cyber-cyan via-cyber-blue to-purple-500 bg-clip-text text-transparent">
                Policy Analysis
              </span>
            </h1>
            
            <p className="text-base sm:text-lg lg:text-xl text-gray-400 leading-relaxed">
              Transform insurance claim processing with AI-powered document analysis. 
              Get instant, explainable decisions backed by policy clauses.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <Link href="/query" className="w-full sm:w-auto">
                <Button size="lg" className="w-full">
                  Start Analysis
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              
              <Link href="/upload" className="w-full sm:w-auto">
                <Button variant="outline" size="lg" className="w-full">
                  Upload Policy
                </Button>
              </Link>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 sm:gap-6 pt-6 sm:pt-8 border-t border-white/10">
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-cyber-cyan">80%+</div>
                <div className="text-xs sm:text-sm text-gray-500">Accuracy</div>
              </div>
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-cyber-blue">&lt;3s</div>
                <div className="text-xs sm:text-sm text-gray-500">Processing</div>
              </div>
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-cyber-teal">100%</div>
                <div className="text-xs sm:text-sm text-gray-500">Explainable</div>
              </div>
            </div>
          </motion.div>
          
          {/* Right: Hero Visual */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="order-1 lg:order-2"
          >
            <HeroVisual />
          </motion.div>
        </div>
        
        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 sm:mt-24 lg:mt-32"
        >
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-3 sm:mb-4">
              Powered by Advanced AI
            </h2>
            <p className="text-gray-400 text-base sm:text-lg">
              Cutting-edge technology for intelligent document analysis
            </p>
          </div>
          
          <Features />
        </motion.div>
      </div>
      
      {/* Footer */}
      <footer className="relative z-10 text-center py-6 sm:py-8 text-gray-500 text-xs sm:text-sm border-t border-white/10 mt-12 sm:mt-20">
        <p>© 2025 EPiCE - Explainable Policy & Contract Evaluator</p>
        <p>This project is done by Ayaan Shaikh so do mention if cloning the project</p>
      </footer>
    </main>
  );
}