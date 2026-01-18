import React, { useState } from 'react';
import { ShieldCheck, Search, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';

type ResultState = 'default' | 'loading' | 'benign' | 'malicious';

interface ScanResult {
  state: ResultState;
  confidence?: number;
}

const App: React.FC = () => {
  const [url, setUrl] = useState<string>('');
  const [result, setResult] = useState<ScanResult>({ state: 'default' });

  const handleAnalyze = async () => {
    if (!url.trim()) return;

    setResult({ state: 'loading' });

    // Simulate API call with 1.5 second delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Randomly determine if URL is benign or malicious for demo
    const isMalicious = Math.random() > 0.6;
    const confidence = Math.floor(Math.random() * 20) + 80; // 80-100%

    setResult({
      state: isMalicious ? 'malicious' : 'benign',
      confidence
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleAnalyze();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 flex items-center justify-center p-4 font-sans">
      {/* Animated background stars effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-indigo-400 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-violet-400 rounded-full opacity-30 animate-pulse delay-75"></div>
        <div className="absolute bottom-1/4 left-1/3 w-1 h-1 bg-blue-400 rounded-full opacity-25 animate-pulse delay-100"></div>
        <div className="absolute top-2/3 right-1/4 w-2 h-2 bg-purple-400 rounded-full opacity-15 animate-pulse delay-150"></div>
      </div>

      {/* Main Card Container */}
      <div className="relative w-full max-w-3xl">
        {/* Glow effect behind card */}
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 via-violet-500/20 to-purple-500/20 rounded-3xl blur-3xl"></div>
        
        {/* Main frosted glass card */}
        <div className="relative bg-gradient-to-br from-slate-800/40 via-slate-900/60 to-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl shadow-2xl p-8 md:p-12">
          
          {/* Header Section */}
          <div className="text-center mb-10">
            {/* Shield Icon */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full blur-xl opacity-50"></div>
                <ShieldCheck className="relative w-16 h-16 text-indigo-400 drop-shadow-lg" strokeWidth={1.5} />
              </div>
            </div>

            {/* Title Text */}
            <h1 className="text-2xl md:text-3xl font-light text-slate-200 tracking-wide leading-relaxed">
              Analyze URLs for potential security threats using{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 font-medium">
                AI-powered detection
              </span>
            </h1>
          </div>

          {/* Input Section */}
          <div className="flex flex-col sm:flex-row gap-3 mb-10">
            {/* URL Input Field */}
            <div className="relative flex-1">
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-2xl blur"></div>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter URL to analyze (e.g., https://example.com)"
                className="relative w-full px-6 py-4 bg-slate-800/80 border border-slate-600/50 rounded-2xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 transition-all duration-300"
                disabled={result.state === 'loading'}
              />
            </div>

            {/* Analyze Button */}
            <button
              onClick={handleAnalyze}
              disabled={!url.trim() || result.state === 'loading'}
              className="relative px-8 py-4 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed text-white rounded-2xl font-medium shadow-lg hover:shadow-violet-500/50 transition-all duration-300 flex items-center justify-center gap-2 min-w-[140px]"
            >
              {result.state === 'loading' ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Analyzing</span>
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  <span>Analyze</span>
                </>
              )}
            </button>
          </div>

          {/* Result Display Area */}
          <div className="relative min-h-[280px] flex items-center justify-center">
            {/* Default State */}
            {result.state === 'default' && (
              <div className="flex flex-col items-center justify-center text-center space-y-6 animate-fade-in">
                <div className="relative">
                  <div className="absolute inset-0 bg-slate-700/20 rounded-full blur-2xl"></div>
                  <ShieldCheck className="relative w-32 h-32 text-slate-700/40" strokeWidth={1} />
                </div>
                <p className="text-slate-500 text-lg font-light">
                  Enter a URL above to begin threat analysis
                </p>
              </div>
            )}

            {/* Loading State */}
            {result.state === 'loading' && (
              <div className="flex flex-col items-center justify-center text-center space-y-6 animate-fade-in">
                <div className="relative">
                  <div className="absolute inset-0 bg-indigo-500/30 rounded-full blur-2xl animate-pulse"></div>
                  <Loader2 className="relative w-24 h-24 text-indigo-400 animate-spin" strokeWidth={1.5} />
                </div>
                <div className="space-y-2">
                  <p className="text-indigo-300 text-xl font-medium">Scanning in progress...</p>
                  <p className="text-slate-500 text-sm">Analyzing URL for potential threats</p>
                </div>
              </div>
            )}

            {/* Benign Result State */}
            {result.state === 'benign' && (
              <div className="w-full animate-fade-in">
                <div className="relative">
                  <div className="absolute inset-0 bg-emerald-500/10 rounded-2xl blur-xl"></div>
                  <div className="relative bg-gradient-to-br from-emerald-900/40 to-green-900/40 border border-emerald-500/50 rounded-2xl p-8">
                    <div className="flex items-start gap-6">
                      <div className="flex-shrink-0">
                        <div className="relative">
                          <div className="absolute inset-0 bg-emerald-500/30 rounded-full blur-lg"></div>
                          <CheckCircle className="relative w-16 h-16 text-emerald-400" strokeWidth={1.5} />
                        </div>
                      </div>
                      <div className="flex-1 space-y-3">
                        <div className="flex items-center gap-3">
                          <span className="px-4 py-1.5 bg-emerald-500/20 border border-emerald-500/50 rounded-full text-emerald-300 text-sm font-semibold tracking-wide">
                            BENIGN
                          </span>
                          <span className="text-slate-400 text-sm">
                            Confidence: {result.confidence}%
                          </span>
                        </div>
                        <h3 className="text-xl text-emerald-300 font-medium">
                          No Immediate Threat Detected
                        </h3>
                        <p className="text-slate-400 leading-relaxed">
                          The analyzed URL appears to be safe. No malicious patterns, phishing indicators, or known threats were detected during the scan.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Malicious Result State */}
            {result.state === 'malicious' && (
              <div className="w-full animate-fade-in">
                <div className="relative">
                  <div className="absolute inset-0 bg-red-500/10 rounded-2xl blur-xl"></div>
                  <div className="relative bg-gradient-to-br from-red-900/40 to-orange-900/40 border border-red-500/50 rounded-2xl p-8">
                    <div className="flex items-start gap-6">
                      <div className="flex-shrink-0">
                        <div className="relative">
                          <div className="absolute inset-0 bg-red-500/30 rounded-full blur-lg animate-pulse"></div>
                          <AlertTriangle className="relative w-16 h-16 text-red-400" strokeWidth={1.5} />
                        </div>
                      </div>
                      <div className="flex-1 space-y-3">
                        <div className="flex items-center gap-3">
                          <span className="px-4 py-1.5 bg-red-500/20 border border-red-500/50 rounded-full text-red-300 text-sm font-semibold tracking-wide">
                            MALICIOUS
                          </span>
                          <span className="text-slate-400 text-sm">
                            Confidence: {result.confidence}%
                          </span>
                        </div>
                        <h3 className="text-xl text-red-300 font-medium">
                          High Confidence Threat Detected
                        </h3>
                        <p className="text-slate-400 leading-relaxed">
                          ⚠️ This URL has been flagged as potentially malicious. Indicators suggest possible <span className="text-red-400 font-medium">Phishing</span> or <span className="text-red-400 font-medium">Malware</span> activity. Avoid accessing this site.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer Note */}
          <div className="mt-8 text-center">
            <p className="text-slate-600 text-sm">
              Powered by AI-Based Threat Analysis using NIDS (CIC-IDS-2018)
            </p>
          </div>
        </div>
      </div>

      {/* Inline animation styles */}
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
        .delay-75 {
          animation-delay: 75ms;
        }
        .delay-100 {
          animation-delay: 100ms;
        }
        .delay-150 {
          animation-delay: 150ms;
        }
      `}</style>
    </div>
  );
};

export default App;
