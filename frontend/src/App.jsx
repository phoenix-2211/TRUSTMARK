import React, { useState } from 'react';
import VerificationQueueScreen from './components/VerificationQueueScreen';
import DisputeDetailScreen from './components/DisputeDetailScreen';
import EvidenceLibraryScreen from './components/EvidenceLibraryScreen';
import BenchmarkReportScreen from './components/BenchmarkReportScreen';
import TrustmarkLogo from './components/TrustmarkLogo';

export default function App() {
  const [activeNav, setActiveNav] = useState('queue');
  const [selectedDisputeId, setSelectedDisputeId] = useState(null);
  const [showSystemScopeModal, setShowSystemScopeModal] = useState(false);

  const handleSelectDispute = (id) => {
    setSelectedDisputeId(id);
    setActiveNav('detail');
  };

  const handleBackToQueue = () => {
    setSelectedDisputeId(null);
    setActiveNav('queue');
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-[#0f172a] font-sans flex flex-col lg:flex-row">
      <aside className="w-full lg:w-64 bg-white border-b lg:border-b-0 lg:border-r border-[#e2e8f0] flex flex-col justify-between shrink-0 z-20">
        <div>
          <div className="p-4 border-b border-[#e2e8f0]">
            <TrustmarkLogo onGoHome={() => setActiveNav('queue')} />
          </div>

          <nav className="p-3 space-y-1">
            <button
              onClick={() => setActiveNav('queue')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-xs font-semibold transition-all ${
                activeNav === 'queue'
                  ? 'bg-[#eef2ff] text-[#002cb3] border-l-4 border-l-[#b45309] shadow-2xs font-bold'
                  : 'text-[#475569] hover:text-[#0f172a] hover:bg-[#f1f5f9]'
              }`}
            >
              <span className="text-sm">📊</span>
              <span>Verification Queue</span>
            </button>

            <button
              onClick={() => setActiveNav('evidence')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-xs font-semibold transition-all ${
                activeNav === 'evidence'
                  ? 'bg-[#eef2ff] text-[#002cb3] border-l-4 border-l-[#b45309] shadow-2xs font-bold'
                  : 'text-[#475569] hover:text-[#0f172a] hover:bg-[#f1f5f9]'
              }`}
            >
              <span className="text-sm">📁</span>
              <span>Evidence Repository</span>
            </button>

            <button
              onClick={() => setActiveNav('benchmark')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-xs font-semibold transition-all ${
                activeNav === 'benchmark'
                  ? 'bg-[#eef2ff] text-[#002cb3] border-l-4 border-l-[#b45309] shadow-2xs font-bold'
                  : 'text-[#475569] hover:text-[#0f172a] hover:bg-[#f1f5f9]'
              }`}
            >
              <span className="text-sm">📈</span>
              <span>Benchmark Report</span>
            </button>
          </nav>
        </div>

        <div className="p-4 border-t border-[#e2e8f0] bg-[#f8fafc]">
          <button
            onClick={() => setShowSystemScopeModal(true)}
            className="w-full flex items-center justify-between p-2 rounded text-[11px] text-[#64748b] hover:text-[#0f172a] hover:bg-[#e2e8f0] transition-colors"
          >
            <span className="flex items-center gap-1.5 font-medium">
              <span>🔒</span>
              <span>System Scope</span>
            </span>
            <span>ⓘ</span>
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0 overflow-auto">
        {activeNav === 'queue' && (
          <VerificationQueueScreen onSelectDispute={handleSelectDispute} />
        )}
        {activeNav === 'detail' && (
          <DisputeDetailScreen
            disputeId={selectedDisputeId}
            onBack={handleBackToQueue}
          />
        )}
        {activeNav === 'evidence' && (
          <EvidenceLibraryScreen onSelectDispute={handleSelectDispute} />
        )}
        {activeNav === 'benchmark' && (
          <BenchmarkReportScreen />
        )}
      </main>

      {showSystemScopeModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl border border-[#e2e8f0] max-w-lg w-full p-6 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-[#f1f5f9] pb-3 mb-4">
              <h3 className="font-bold text-sm text-[#0f172a] flex items-center gap-2">
                <span>🔒</span>
                <span>System Scope & Architectural Boundaries</span>
              </h3>
              <button
                onClick={() => setShowSystemScopeModal(false)}
                className="text-[#94a3b8] hover:text-[#475569] font-bold text-sm"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs text-[#475569] leading-relaxed">
              <p>
                <strong>Trustmark Scope:</strong> Pre-submission chargeback evidence verification platform for Razorpay merchants.
              </p>
              <p>
                <strong>Out of Scope:</strong> Financial settlement, card network representment filing, or direct issuer communications.
              </p>
              <p>
                <strong>AI Transparency:</strong> The verification engine operates deterministically over structured evidence data. The OpenRouter LLM layer is purely advisory.
              </p>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowSystemScopeModal(false)}
                className="px-4 py-2 bg-[#0f172a] text-white rounded text-xs font-semibold hover:bg-[#1e293b]"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
