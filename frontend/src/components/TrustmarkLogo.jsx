import React, { useEffect, useState } from 'react';

export default function TrustmarkLogo({ compact = false, onGoHome }) {
  const [shouldAnimate, setShouldAnimate] = useState(false);

  useEffect(() => {
    const hasAnimated = sessionStorage.getItem('trustmark_has_animated');
    if (!hasAnimated) {
      setShouldAnimate(true);
      sessionStorage.setItem('trustmark_has_animated', 'true');
    }
  }, []);

  return (
    <div
      onClick={onGoHome}
      className="group cursor-pointer flex items-center gap-3 select-none"
      title="Click to return to Trustmark Verification Queue"
    >
      <div
        className={`w-9 h-9 rounded-lg bg-white border border-[#e2e8f0] p-1 flex items-center justify-center shrink-0 shadow-2xs relative ${
          shouldAnimate ? 'animate-seal-once' : ''
        }`}
      >
        <img
          src="/Logo.png"
          alt="Trustmark Logo"
          className="w-full h-full object-contain"
        />
      </div>

      {!compact && (
        <div className="min-w-0">
          <div className="relative inline-block">
            <span className="font-brand font-bold text-sm text-[#0f172a] tracking-widest uppercase block">
              TRUSTMARK
            </span>
            <span className="absolute left-0 bottom-0 w-full h-[2px] bg-[#b45309] transition-transform duration-200 ease-out origin-left scale-x-0 group-hover:scale-x-100"></span>
          </div>

          <span className="text-[10px] font-medium text-[#64748b] tracking-tight block mt-0.5 whitespace-nowrap">
            Trustmark — certified before you submit.
          </span>
        </div>
      )}
    </div>
  );
}
