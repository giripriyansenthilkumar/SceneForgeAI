import { GitBranch, Check, ArrowRight } from 'lucide-react';

export interface VersionItem {
  version_number: number;
  prompt_summary: string;
  polygons: number;
  created_at: string;
}

interface VersionHistoryProps {
  versions: VersionItem[];
  activeVersion: number;
  onSelectVersion: (version: number) => void;
}

export const VersionHistory: React.FC<VersionHistoryProps> = ({
  versions,
  activeVersion,
  onSelectVersion
}) => {
  return (
    <div className="glass-panel p-4 rounded-xl space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
          <GitBranch className="w-3.5 h-3.5 text-teal-400" />
          <span>Scene Version Graph</span>
        </div>
        <span className="text-[11px] font-mono text-teal-400 font-semibold">Active: v{activeVersion}</span>
      </div>

      <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
        {versions.map((ver) => {
          const isActive = ver.version_number === activeVersion;
          return (
            <div
              key={ver.version_number}
              onClick={() => onSelectVersion(ver.version_number)}
              className={`p-2.5 rounded-lg border cursor-pointer transition flex items-center justify-between text-xs font-mono ${
                isActive
                  ? 'bg-teal-950/30 border-teal-500/50 text-teal-200'
                  : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <div
                  className={`w-6 h-6 rounded-md flex items-center justify-center font-bold text-xs ${
                    isActive ? 'bg-teal-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  v{ver.version_number}
                </div>
                <div>
                  <div className="text-slate-200 font-medium font-sans truncate max-w-[180px]">
                    {ver.prompt_summary}
                  </div>
                  <div className="text-[10px] text-slate-500 flex items-center space-x-2">
                    <span>{ver.polygons.toLocaleString()} polys</span>
                    <span>•</span>
                    <span>{ver.created_at}</span>
                  </div>
                </div>
              </div>

              {isActive ? (
                <Check className="w-4 h-4 text-teal-400" />
              ) : (
                <ArrowRight className="w-3.5 h-3.5 text-slate-600 hover:text-slate-300" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
