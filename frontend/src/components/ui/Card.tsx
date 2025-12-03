import React from 'react';
import { cn } from '@/src/lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
  glass?: boolean;
}

export function Card({ children, className, glow = false, glass = false }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-2xl p-6 transition-all duration-300',
        glass && 'bg-white/10 backdrop-blur-md border border-white/20',
        !glass && 'bg-cyber-gray/50 border border-cyber-cyan/20',
        glow && 'hover:shadow-2xl hover:shadow-cyber-cyan/30',
        className
      )}
    >
      {children}
    </div>
  );
}