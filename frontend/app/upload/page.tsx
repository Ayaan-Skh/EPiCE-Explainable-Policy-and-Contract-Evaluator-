'use client';

import { useState } from 'react';
import { Button } from '@/src/components/ui/Button';
import { Card } from '@/src/components/ui/Card';
import { AnimatedBackground } from '@/src/components/landing/AnimatedBackground';
import { ArrowLeft, Upload, FileText, CheckCircle, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploaded(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    
    // Simulate upload (replace with actual API)
    setTimeout(() => {
      setUploading(false);
      setUploaded(true);
    }, 2000);
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
          <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gradient-to-br from-cyber-cyan to-cyber-blue flex items-center justify-center">
            <Sparkles className="w-4 h-4 sm:w-6 sm:h-6 text-white" />
          </div>
          <span className="text-xl sm:text-2xl font-bold text-white">EPiCE</span>
        </div>
        
        <div className="w-20"></div>
      </nav>
      
      {/* Main Content */}
      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-8 py-8 sm:py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8 sm:mb-12"
        >
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-3 sm:mb-4">
            Upload Policy Document
          </h1>
          <p className="text-base sm:text-lg text-gray-400">
            Upload your insurance policy document to enable AI analysis
          </p>
        </motion.div>
        
        {/* Upload Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card glass glow className="p-6 sm:p-8">
            {!uploaded ? (
              <div className="space-y-6">
                {/* File Input */}
                <div
                  className="border-2 border-dashed border-cyber-cyan/30 rounded-2xl p-8 sm:p-12 text-center hover:border-cyber-cyan/50 transition-all cursor-pointer bg-cyber-navy/20"
                  onClick={() => document.getElementById('file-input')?.click()}
                >
                  <Upload className="w-12 h-12 sm:w-16 sm:h-16 text-cyber-cyan mx-auto mb-4" />
                  <p className="text-lg sm:text-xl font-semibold text-white mb-2">
                    {file ? file.name : 'Click to upload or drag and drop'}
                  </p>
                  <p className="text-sm sm:text-base text-gray-500">
                    PDF, DOCX or TXT (Max 10MB)
                  </p>
                  <input
                    id="file-input"
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>
                
                {/* Upload Button */}
                {file && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <Button
                      onClick={handleUpload}
                      disabled={uploading}
                      size="lg"
                      className="w-full"
                    >
                      {uploading ? 'Uploading...' : 'Upload Document'}
                      <Upload className="w-5 h-5" />
                    </Button>
                  </motion.div>
                )}
              </div>
            ) : (
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-center py-8"
              >
                <CheckCircle className="w-16 h-16 sm:w-20 sm:h-20 text-emerald-500 mx-auto mb-4" />
                <h3 className="text-2xl sm:text-3xl font-bold text-white mb-2">
                  Upload Successful!
                </h3>
                <p className="text-base sm:text-lg text-gray-400 mb-6">
                  Your policy document has been processed and is ready for analysis
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link href="/query">
                    <Button size="lg" className="w-full sm:w-auto">
                      Start Analyzing Claims
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => {
                      setFile(null);
                      setUploaded(false);
                    }}
                    className="w-full sm:w-auto"
                  >
                    Upload Another
                  </Button>
                </div>
              </motion.div>
            )}
          </Card>
        </motion.div>
        
        {/* Info Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid sm:grid-cols-3 gap-4 mt-8 sm:mt-12"
        >
          <Card glass className="p-4 sm:p-6 text-center">
            <FileText className="w-8 h-8 text-cyber-cyan mx-auto mb-3" />
            <h4 className="font-semibold text-white mb-2 text-sm sm:text-base">Secure Processing</h4>
            <p className="text-xs sm:text-sm text-gray-400">Your documents are encrypted and never stored</p>
          </Card>
          <Card glass className="p-4 sm:p-6 text-center">
            <FileText className="w-8 h-8 text-cyber-blue mx-auto mb-3" />
            <h4 className="font-semibold text-white mb-2 text-sm sm:text-base">Fast Analysis</h4>
            <p className="text-xs sm:text-sm text-gray-400">AI processes documents in seconds</p>
          </Card>
          <Card glass className="p-4 sm:p-6 text-center">
            <FileText className="w-8 h-8 text-cyber-teal mx-auto mb-3" />
            <h4 className="font-semibold text-white mb-2 text-sm sm:text-base">100% Accuracy</h4>
            <p className="text-xs sm:text-sm text-gray-400">Clause extraction with perfect precision</p>
          </Card>
        </motion.div>
      </div>
    </main>
  );
}