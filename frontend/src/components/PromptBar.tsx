import React, { useState } from 'react';
import { Sparkles, Wand2, RefreshCw, Edit3 } from 'lucide-react';

interface PromptBarProps {
  onGenerate: (prompt: string, category: string) => void;
  onEdit: (instruction: string) => void;
  isGenerating: boolean;
  hasActiveScene: boolean;
}

export const PromptBar: React.FC<PromptBarProps> = ({
  onGenerate,
  onEdit,
  isGenerating,
  hasActiveScene
}) => {
  const [prompt, setPrompt] = useState('Create a realistic small luxury yacht with two decks, glass windows, teak flooring, and swimming platform.');
  const [category, setCategory] = useState('boat');
  const [mode, setMode] = useState<'generate' | 'edit'>('generate');

  const suggestions = [
    { label: '✨ Luxury Yacht', prompt: 'Create a realistic small luxury yacht with two decks, glass windows, teak flooring, and swimming platform.', cat: 'boat', mode: 'generate' },
    { label: '📐 Make 20% Longer', prompt: 'Make the yacht 20% longer and add twin stern engines.', cat: 'boat', mode: 'edit' },
    { label: '🏊 Add Swim Platform', prompt: 'Add a spacious stern swimming platform with teak planking.', cat: 'boat', mode: 'edit' },
    { label: '🪵 Teak Decking', prompt: 'Change the deck material to teak wood.', cat: 'boat', mode: 'edit' }
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isGenerating) return;

    if (mode === 'edit' && hasActiveScene) {
      onEdit(prompt);
    } else {
      onGenerate(prompt, category);
    }
  };

  return (
    <div className="glass-panel p-5 rounded-2xl shadow-xl space-y-3">
      {/* Mode toggle & title */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-2">
          {hasActiveScene ? (
            <div className="flex bg-slate-900 p-0.5 rounded-lg border border-slate-800">
              <button
                type="button"
                onClick={() => setMode('generate')}
                className={`px-2.5 py-1 rounded-md text-xs font-medium transition ${
                  mode === 'generate' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Generate New
              </button>
              <button
                type="button"
                onClick={() => setMode('edit')}
                className={`px-2.5 py-1 rounded-md text-xs font-medium flex items-center space-x-1 transition ${
                  mode === 'edit' ? 'bg-teal-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Edit3 className="w-3 h-3" />
                <span>Modify Scene</span>
              </button>
            </div>
          ) : (
            <span className="font-semibold text-slate-300 flex items-center space-x-1.5">
              <Wand2 className="w-3.5 h-3.5 text-blue-400" />
              <span>Natural-Language 3D Synthesis</span>
            </span>
          )}
        </div>

        {mode === 'generate' && (
          <div className="flex items-center space-x-2">
            <span>Category:</span>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-200 rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="boat">Boat & Yacht</option>
              <option value="furniture">Furniture</option>
              <option value="vehicle">Vehicle</option>
              <option value="building">Architecture</option>
              <option value="mechanical">Mechanical</option>
            </select>
          </div>
        )}
      </div>

      {/* Prompt Form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <textarea
          rows={2}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={
            mode === 'edit'
              ? 'Enter modification (e.g. "Make it 20% longer and add a swimming platform")...'
              : 'Describe your 3D model requirements, dimensions, or materials...'
          }
          className="flex-1 bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition resize-none font-sans"
        />
        <button
          type="submit"
          disabled={isGenerating || !prompt.trim()}
          className={`px-5 rounded-xl text-white font-medium text-sm flex items-center justify-center space-x-2 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg ${
            mode === 'edit'
              ? 'bg-gradient-to-r from-teal-600 to-emerald-500 hover:from-teal-500 hover:to-emerald-400 shadow-teal-600/20'
              : 'bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-500 hover:to-teal-400 shadow-blue-600/20'
          }`}
        >
          {isGenerating ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : mode === 'edit' ? (
            <>
              <Edit3 className="w-4 h-4" />
              <span>Modify</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Generate</span>
            </>
          )}
        </button>
      </form>

      {/* Quick Suggestions Chips */}
      <div className="flex flex-wrap gap-1.5 pt-1">
        <span className="text-[11px] text-slate-500 self-center mr-1">Suggestions:</span>
        {suggestions.map((item, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setPrompt(item.prompt);
              setCategory(item.cat);
              if (item.mode === 'edit' && hasActiveScene) {
                setMode('edit');
              } else {
                setMode('generate');
              }
            }}
            className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border border-slate-700/50 transition font-mono"
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
};
