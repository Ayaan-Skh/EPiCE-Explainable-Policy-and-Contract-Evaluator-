'use client';

import { Send } from 'lucide-react';
import { Button } from '@/src/components/ui/Button';
import { Card } from '@/src/components/ui/Card';

interface QueryInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading?: boolean;
  disabled?: boolean;
}

export function QueryInput({ value, onChange, onSubmit, loading, disabled }: QueryInputProps) {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <Card glass glow className="p-4 sm:p-6">
      <div className="space-y-4">
        <label className="block text-sm sm:text-base font-semibold text-white mb-2">
          Enter Claim Details
        </label>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Example: 46 year old male, knee surgery in Pune, 3 month policy"
          className="w-full h-24 sm:h-32 px-4 py-3 bg-cyber-navy/50 border border-cyber-cyan/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyber-cyan focus:ring-2 focus:ring-cyber-cyan/50 transition-all resize-none text-sm sm:text-base"
          disabled={disabled}
        />
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-0">
          <p className="text-xs sm:text-sm text-gray-500">
            Include: age, procedure, location, policy duration
          </p>
          <Button
            onClick={onSubmit}
            disabled={!value.trim() || disabled}
            size="md"
            className="w-full sm:w-auto"
          >
            {loading ? 'Analyzing...' : 'Analyze Claim'}
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
}