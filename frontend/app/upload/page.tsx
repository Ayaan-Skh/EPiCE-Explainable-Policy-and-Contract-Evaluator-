'use client';

import { useState } from 'react';
import { Button } from '@/src/components/ui/Button';
import { Card } from '@/src/components/ui/Card';
import { AnimatedBackground } from '@/src/components/landing/AnimatedBackground';
import { ArrowLeft, Upload, FileText, CheckCircle, Sparkles, X, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain'];
    const allowedExtensions = ['.pdf', '.docx', '.doc', '.txt'];

    const fileExt = '.' + selectedFile.name.split('.').pop()?.toLowerCase();

    if (!allowedTypes.includes(selectedFile.type) && !allowedExtensions.includes(fileExt)) {
      setError('Invalid file type. Please upload PDF, DOCX, or TXT files only.');
      return;
    }

    // Validate file size (10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File too large. Maximum size is 10MB.');
      return;
    }

    setFile(selectedFile);
    setUploaded(false);
    setError(null);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/upload-file`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      setUploadResult(result);
      setUploading(false);
      setUploaded(true);
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.message || 'Failed to upload file');
      setUploading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setUploaded(false);
    setUploadResult(null);
    setError(null);
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
          <p className="text-sm text-gray-500 mt-2">
            Supports PDF, DOCX, DOC, and TXT files (max 10MB)
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
                {/* Error Display */}
                {error && (
                  <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                    <div>
                      <p className="text-rose-500 font-semibold">Upload Error</p>
                      <p className="text-sm text-gray-300 mt-1">{error}</p>
                    </div>
                  </div>
                )}

                {/* File Input - Drag & Drop */}
                <div
                  className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all cursor-pointer
                    ${dragActive
                      ? 'border-cyber-cyan bg-cyber-cyan/10'
                      : 'border-cyber-cyan/30 hover:border-cyber-cyan/50 bg-cyber-navy/20'
                    }`}
                  onClick={() => !file && document.getElementById('file-input')?.click()}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  {file ? (
                    <div className="space-y-4">
                      <FileText className="w-16 h-16 text-cyber-cyan mx-auto" />
                      <div>
                        <p className="text-lg font-semibold text-white">{file.name}</p>
                        <p className="text-sm text-gray-400 mt-1">
                          {(file.size / 1024).toFixed(2)} KB
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {file.type || 'Unknown type'}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile();
                        }}
                      >
                        <X className="w-4 h-4" />
                        Remove
                      </Button>
                    </div>
                  ) : (
                    <>
                      <Upload className="w-12 h-12 sm:w-16 sm:h-16 text-cyber-cyan mx-auto mb-4" />
                      <p className="text-lg sm:text-xl font-semibold text-white mb-2">
                        {dragActive ? 'Drop file here' : 'Click to upload or drag and drop'}
                      </p>
                      <p className="text-sm sm:text-base text-gray-500">
                        PDF, DOCX, DOC, or TXT (Max 10MB)
                      </p>
                    </>
                  )}
                  <input
                    id="file-input"
                    type="file"
                    accept=".pdf,.docx,.doc,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword,text/plain"
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
                      {uploading ? 'Processing...' : 'Upload & Process Document'}
                      <Upload className="w-5 h-5" />
                    </Button>
                    {uploading && (
                      <p className="text-sm text-gray-400 text-center mt-3">
                        Extracting text, creating embeddings, and storing in vector database...
                      </p>
                    )}
                  </motion.div>
                )}
              </div>
            ) : (
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-center py-8"
              >
                <CheckCircle className="w-16 h-16 sm:w-20 sm:h-20 text-emerald-500 mx-auto mb-4"

                />
                <h3 className="text-2xl sm:text-3xl font-bold text-white mb-2">
                  Upload Successful!
                </h3>
                <p className="text-base sm:text-lg text-gray-400 mb-6">
                  Your policy document has been processed and is ready for analysis
                </p>
                {/* Upload Stats */}
                {uploadResult && (
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6 p-4 bg-cyber-navy/30 rounded-xl">
                    <div>
                      <p className="text-xs text-gray-500">File Size</p>
                      <p className="text-lg font-semibold text-cyber-cyan">{uploadResult.file_size_kb} KB</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Chunks</p>
                      <p className="text-lg font-semibold text-cyber-cyan">{uploadResult.total_chunks}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Sections</p>
                      <p className="text-lg font-semibold text-cyber-cyan">{uploadResult.statistics?.unique_sections || 0}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Process Time</p>
                      <p className="text-lg font-semibold text-cyber-cyan">{uploadResult.setup_time_seconds?.toFixed(1)}s</p>
                    </div>
                  </div>
                )}

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link href="/query">
                    <Button size="lg" className="w-full sm:w-auto">
                      Start Analyzing Claims
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={removeFile}
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
            <h4 className="font-semibold text-white mb-2 text-sm sm:text-base">Multi-Format Support</h4>
            <p className="text-xs sm:text-sm text-gray-400">PDF, DOCX, DOC, and TXT files supported</p>
          </Card>
          <Card glass className="p-4 sm:p-6 text-center">
            <FileText className="w-8 h-8 text-cyber-blue mx-auto mb-3" />
            <h4 className="font-semibold text-white mb-2 text-sm sm:text-base">Intelligent Parsing</h4>
            <p className="text-xs sm:text-sm text-gray-400">Extracts text from complex layouts and tables</p>
          </Card>
          <Card glass className="p-4 sm:p-6 text-center">
            <FileText className="w-8 h-8 text-cyber-teal mx-auto mb-3" />
            <h4 className="font-semibold text-white mb-2 text-sm sm:text-base">Secure Processing</h4>
            <p className="text-xs sm:text-sm text-gray-400">Files processed securely and never permanently stored</p>
          </Card>
        </motion.div>
      </div>
    </main>
  );
}