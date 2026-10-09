import { Box, Layers, Palette } from 'lucide-react';

interface SceneObjectData {
  id: string;
  type: string;
  material_id?: string;
  parameters?: Record<string, any>;
}

interface SceneTreeProps {
  objects: SceneObjectData[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

export const SceneTree: React.FC<SceneTreeProps> = ({
  objects,
  selectedId,
  onSelect
}) => {
  if (!objects || objects.length === 0) {
    return (
      <div className="glass-panel p-4 rounded-xl text-xs text-slate-500 font-mono">
        No components in active scene.
      </div>
    );
  }

  return (
    <div className="glass-panel p-4 rounded-xl space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
          <Layers className="w-3.5 h-3.5 text-blue-400" />
          <span>Scene Hierarchy & Components</span>
        </div>
        <span className="text-[11px] font-mono text-slate-500">{objects.length} Objects</span>
      </div>

      <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
        {objects.map((obj) => {
          const isSelected = selectedId === obj.id;
          return (
            <button
              key={obj.id}
              onClick={() => onSelect(isSelected ? null : obj.id)}
              className={`w-full text-left p-2 rounded-lg transition flex items-center justify-between text-xs font-mono border ${
                isSelected
                  ? 'bg-blue-600/20 border-blue-500 text-blue-200'
                  : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center space-x-2 truncate">
                <Box className={`w-3.5 h-3.5 flex-shrink-0 ${isSelected ? 'text-blue-400' : 'text-slate-500'}`} />
                <span className="font-medium text-slate-200 truncate">{obj.id}</span>
                <span className="text-[10px] text-slate-500 uppercase px-1.5 py-0.2 rounded bg-slate-800">
                  {obj.type.replace('boat_', '')}
                </span>
              </div>

              {obj.material_id && (
                <div className="flex items-center space-x-1 text-[10px] text-teal-400/90 pl-2">
                  <Palette className="w-2.5 h-2.5" />
                  <span className="truncate max-w-[80px]">{obj.material_id.replace('mat_', '')}</span>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
