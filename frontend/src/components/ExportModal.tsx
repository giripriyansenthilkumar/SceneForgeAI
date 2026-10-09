import React, { useState } from 'react';
import { Download, X, FileBox, Check } from 'lucide-react';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmExport: (format: string, compress: boolean) => void;
  polyCount: number;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  onConfirmExport,
  polyCount
}) => {
  const [selectedFormat, setSelectedFormat] = useState<'GLB' | 'OBJ' | 'STL'>('GLB');
  const [dracoCompression, setDracoCompression] = useState<boolean>(true);

  if (!isOpen) return null;

  const formats = [
    {
      id: 'GLB',
      title: 'glTF 2.0 Binary (.glb)',
      desc: 'Standard for Web, Three.js, Babylon.js, AR/VR with embedded PBR textures.',
      badge: 'Recommended'
    },
    {
      id: 'OBJ',
      title: 'Wavefront OBJ (.obj)',
      desc: 'Broad compatibility for Blender, Maya, 3ds Max, and game engines.',
      badge: 'Universal'
    },
    {
      id: 'STL',
      title: 'Stereolithography (.stl)',
      desc: 'Solid surface mesh optimized for 3D printing and CAD analysis.',
      badge: '3D Printing'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-md bg-[#0F172A] border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-blue-600/20 text-blue-400">
              <FileBox className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-base">Export 3D Model</h3>
              <p className="text-xs text-slate-400 font-mono">{polyCount.toLocaleString()} Triangles • Validated Manifold</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Format Selection Cards */}
        <div className="space-y-2.5">
          <label className="text-xs text-slate-400 font-medium">Select Output Format:</label>
          {formats.map((fmt) => {
            const isSelected = selectedFormat === fmt.id;
            return (
              <div
                key={fmt.id}
                onClick={() => setSelectedFormat(fmt.id as any)}
                className={`p-3.5 rounded-xl border cursor-pointer transition flex items-start justify-between ${
                  isSelected
                    ? 'bg-blue-600/10 border-blue-500 shadow-lg shadow-blue-500/10'
                    : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-sm text-slate-100">{fmt.title}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono ${
                      fmt.badge === 'Recommended' ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {fmt.badge}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{fmt.desc}</p>
                </div>
                {isSelected && (
                  <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center text-slate-950 flex-shrink-0 mt-0.5">
                    <Check className="w-3 h-3 stroke-[3]" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Options */}
        {selectedFormat === 'GLB' && (
          <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer pt-1">
            <input
              type="checkbox"
              checked={dracoCompression}
              onChange={(e) => setDracoCompression(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-blue-600 focus:ring-0"
            />
            <span>Enable Draco Mesh Compression (reduced bandwidth)</span>
          </label>
        )}

        {/* Action Buttons */}
        <div className="flex items-center space-x-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-2.5 rounded-xl border border-slate-800 text-xs font-medium text-slate-300 hover:bg-slate-900 transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => {
              onConfirmExport(selectedFormat, dracoCompression);
              onClose();
            }}
            className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-500 hover:to-teal-400 text-white text-xs font-semibold flex items-center justify-center space-x-2 shadow-lg shadow-blue-500/20 transition"
          >
            <Download className="w-4 h-4" />
            <span>Download {selectedFormat}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
