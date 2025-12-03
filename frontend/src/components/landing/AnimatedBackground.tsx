'use client';

export function AnimatedBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Gradient Orbs */}
      <div className="absolute top-20 left-20 w-96 h-96 bg-cyber-cyan/20 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyber-blue/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-cyber-teal/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }} />
      
      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.05)_1px,transparent_1px)] bg-size-[100px_100px]" />
      
      {/* Scan Line Effect */}
      <div className="absolute inset-0 bg-linear-to-b from-transparent via-cyber-cyan/5 to-transparent h-full animate-pulse" />
    </div>
  );
}