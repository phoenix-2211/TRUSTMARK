import React from 'react';

export default function VerdictBadge({ verdict, size = 'md' }) {
  let badgeStyle = 'bg-[#f1f5f9] text-[#475569] border-[#cbd5e1]';
  let icon = 'ℹ️';

  if (!verdict) {
    return <span className="text-xs text-[#94a3b8]">N/A</span>;
  }

  const upper = verdict.toUpperCase();

  if (upper.includes('READY')) {
    badgeStyle = 'bg-[#f0fdf4] text-[#166534] border-[#bbf7d0] font-semibold';
    icon = '✓';
  } else if (upper.includes('NEEDS REVIEW')) {
    badgeStyle = 'bg-[#fffbeb] text-[#92400e] border-[#fef3c7] font-semibold';
    icon = '⚠️';
  } else if (upper.includes('DO NOT SUBMIT')) {
    badgeStyle = 'bg-[#fef2f2] text-[#991b1b] border-[#fecaca] font-semibold';
    icon = '✕';
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-3 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border ${sizeClasses} ${badgeStyle}`}>
      <span>{icon}</span>
      <span>{verdict}</span>
    </span>
  );
}
