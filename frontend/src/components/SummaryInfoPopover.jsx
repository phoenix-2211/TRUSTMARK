import React, { useState } from 'react';

export default function SummaryInfoPopover({ summary, guidance }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative inline-block text-left">
      <button
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full bg-[#f8fafc] text-[#475569] border border-[#cbd5e1] hover:bg-[#f1f5f9] transition-colors"
        title="View AI-Generated Summary"
      >
        <span>✨</span>
        <span>AI Summary</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-[#e2e8f0] p-4 z-50 animate-in fade-in zoom-in-95 duration-150">
          <div className="flex items-center justify-between border-b border-[#f1f5f9] pb-2 mb-2">
            <span className="text-xs font-bold text-[#0f172a] flex items-center gap-1">
              ✨ AI-Generated Summary <span className="text-[10px] font-normal text-[#64748b]">(Advisory Layer)</span>
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsOpen(false);
              }}
              className="text-[#94a3b8] hover:text-[#475569] text-xs font-bold"
            >
              ✕
            </button>
          </div>

          <div className="space-y-2 text-xs">
            {summary && (
              <div>
                <span className="font-semibold text-[#334155] block mb-0.5">Summary</span>
                <p className="text-[#475569] bg-[#f8fafc] p-2 rounded border border-[#f1f5f9]">
                  {summary}
                </p>
              </div>
            )}

            {guidance && (
              <div>
                <span className="font-semibold text-[#334155] block mb-0.5">Merchant Guidance</span>
                <p className="text-[#475569] bg-[#f8fafc] p-2 rounded border border-[#f1f5f9] leading-relaxed">
                  {guidance}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
