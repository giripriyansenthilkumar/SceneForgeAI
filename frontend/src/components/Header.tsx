import React from 'react';
import { Box, Download, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  onExport: (format: string) => void;
  isGenerating: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onExport, isGenerating }) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-[#0B0F19]/90 backdrop-blur-md px-6 flex items-center justify-between z-20">
      {/* Brand */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-teal-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <Box className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-bold text-lg text-white tracking-tight">SceneForge AI</h1>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              v1.0 Agent + MCP
            </span>
          </div>
          <p className="text-xs text-slate-400">Autonomous 3D Procedural Studio</p>
        </div>
      </div>

      {/* Badges & Actions */}
      <div className="flex items-center space-x-3">
        <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg glass-card text-xs text-slate-300 border border-slate-800">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Multi-Layer Guardrails Active</span>
        </div>

        <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => onExport('GLB')}
            disabled={isGenerating}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>GLB</span>
          </button>
          <button
            onClick={() => onExport('OBJ')}
            disabled={isGenerating}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg hover:bg-slate-800 text-slate-300 text-xs font-medium transition disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>OBJ</span>
          </button>
          <button
            onClick={() => onExport('STL')}
            disabled={isGenerating}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg hover:bg-slate-800 text-slate-300 text-xs font-medium transition disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>STL</span>
          </button>
        </div>
      </div>
    </header>
  );
};
