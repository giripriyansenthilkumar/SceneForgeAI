import React from 'react';
import { CheckCircle2, Terminal, Cpu, Activity } from 'lucide-react';

export interface AgentStep {
  id: string;
  step: string;
  message: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'ERROR';
  tool?: string;
  duration?: string;
}

interface AgentActivityProps {
  steps: AgentStep[];
  currentProgress: number;
  isGenerating: boolean;
  sceneSpecification?: any;
}

export const AgentActivity: React.FC<AgentActivityProps> = ({
  steps,
  currentProgress,
  isGenerating,
  sceneSpecification
}) => {
  return (
    <div className="glass-panel p-5 rounded-2xl flex flex-col h-full space-y-4">
      {/* Title & Progress Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-blue-400" />
          <h2 className="text-sm font-semibold text-slate-200">AI Agent & MCP Trace</h2>
        </div>
        <div className="flex items-center space-x-2">
          {isGenerating ? (
            <span className="flex items-center space-x-1.5 text-xs text-blue-400 font-mono">
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping"></span>
              <span>Autonomous Run Active</span>
            </span>
          ) : (
            <span className="text-xs text-emerald-400 font-mono flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Model Validated</span>
            </span>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-slate-400 font-mono">
          <span>Pipeline Progress</span>
          <span>{currentProgress}%</span>
        </div>
        <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-blue-500 via-teal-400 to-emerald-400 transition-all duration-300"
            style={{ width: `${currentProgress}%` }}
          />
        </div>
      </div>

      {/* Steps List */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 font-mono text-xs">
        {steps.map((st) => (
          <div
            key={st.id}
            className={`p-3 rounded-xl transition border ${
              st.status === 'RUNNING'
                ? 'bg-blue-950/30 border-blue-500/40 text-blue-200 shadow-lg shadow-blue-500/5'
                : st.status === 'COMPLETED'
                ? 'bg-slate-900/60 border-slate-800 text-slate-300'
                : 'bg-slate-950/30 border-slate-900 text-slate-500'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center space-x-2 font-semibold">
                {st.status === 'COMPLETED' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />}
                {st.status === 'RUNNING' && <Activity className="w-3.5 h-3.5 text-blue-400 animate-spin flex-shrink-0" />}
                {st.status === 'PENDING' && <div className="w-3.5 h-3.5 rounded-full border border-slate-700 flex-shrink-0" />}
                <span className="text-slate-100">{st.step}</span>
              </div>
              {st.duration && <span className="text-[10px] text-slate-500">{st.duration}</span>}
            </div>

            <p className="text-[11px] text-slate-400 pl-5.5 leading-relaxed font-sans">{st.message}</p>

            {st.tool && (
              <div className="mt-2 ml-5 px-2.5 py-1 rounded-md bg-slate-950 border border-slate-800 text-[11px] text-teal-400 flex items-center space-x-1.5">
                <Terminal className="w-3 h-3 text-teal-400" />
                <span className="truncate">{st.tool}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Intermediate Representation Preview */}
      {sceneSpecification && (
        <div className="pt-2 border-t border-slate-800/80">
          <div className="text-[11px] text-slate-400 mb-1.5 flex items-center justify-between">
            <span>Scene Intermediate Representation (IR):</span>
            <span className="text-teal-400">{sceneSpecification.objects?.length || 0} Components</span>
          </div>
          <div className="max-h-28 overflow-y-auto bg-slate-950/90 border border-slate-800/80 rounded-lg p-2.5 text-[10px] font-mono text-slate-300">
            <pre>{JSON.stringify(sceneSpecification.metadata, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};
