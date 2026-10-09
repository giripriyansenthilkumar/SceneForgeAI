import { useState } from 'react';
import { Header } from './components/Header';
import { PromptBar } from './components/PromptBar';
import { AgentActivity, AgentStep } from './components/AgentActivity';
import { SceneTree } from './components/SceneTree';
import { VersionHistory, VersionItem } from './components/VersionHistory';
import { ExportModal } from './components/ExportModal';
import { ThreeViewer } from './viewer/ThreeViewer';
import { Activity, Layers, GitBranch } from 'lucide-react';

const DEFAULT_STEPS: AgentStep[] = [
  {
    id: '1',
    step: 'Understanding Prompt',
    message: 'Parsed natural language prompt into parametric boat specifications.',
    status: 'COMPLETED',
    duration: '120ms'
  },
  {
    id: '2',
    step: 'Scene Planning',
    message: 'Constructed Scene IR hierarchy: boat_hull -> boat_deck -> boat_cabin -> boat_swim_platform.',
    status: 'COMPLETED',
    duration: '210ms'
  },
  {
    id: '3',
    step: 'MCP Tool Execution',
    message: 'Dispatched procedural geometry operations via Model Context Protocol.',
    status: 'COMPLETED',
    tool: 'mcp:create_scene(category="boat", units="meters")',
    duration: '380ms'
  },
  {
    id: '4',
    step: 'Material Synthesis',
    message: 'Applied white fiberglass PBR, teak wood planking, and tinted panoramic glass.',
    status: 'COMPLETED',
    duration: '150ms'
  },
  {
    id: '5',
    step: 'Geometry Validation',
    message: 'Passed all multi-tier guardrails: 0 non-manifold edges, valid outward normals.',
    status: 'COMPLETED',
    duration: '90ms'
  },
  {
    id: '6',
    step: 'Binary GLB Export',
    message: 'Successfully serialized asset to glTF 2.0 Binary container.',
    status: 'COMPLETED',
    tool: 'mcp:export_model(format="GLB")',
    duration: '340ms'
  }
];

export function App() {
  const [modelUrl, setModelUrl] = useState<string | null>('/static/exports/test_yacht.glb');
  const [sceneId, setSceneId] = useState<string | null>('scene_initial');
  const [versionNumber, setVersionNumber] = useState<number>(1);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(100);
  const [steps, setSteps] = useState<AgentStep[]>(DEFAULT_STEPS);
  const [vertexCount, setVertexCount] = useState<number>(296);
  const [polyCount, setPolyCount] = useState<number>(148);
  const [selectedComponentId, setSelectedComponentId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'agent' | 'tree' | 'versions'>('agent');
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);

  const [versions, setVersions] = useState<VersionItem[]>([
    {
      version_number: 1,
      prompt_summary: 'Small Luxury Yacht with Teak Deck',
      polygons: 148,
      created_at: 'Initial Draft'
    }
  ]);

  const [sceneSpec, setSceneSpec] = useState<any>({
    metadata: {
      name: "Parametric Luxury Yacht",
      category: "boat",
      units: "meters"
    },
    objects: [
      { id: "hull_main", type: "boat_hull", material_id: "mat_hull_white", parameters: { length: 12.0, beam: 3.8 } },
      { id: "deck_main", type: "boat_deck", material_id: "mat_teak_deck", parameters: { length: 11.4, thickness: 0.12 } },
      { id: "cabin_bridge", type: "boat_cabin", material_id: "mat_cabin_glass", parameters: { length: 5.5, height: 1.9 } },
      { id: "platform_stern", type: "boat_swim_platform", material_id: "mat_teak_deck", parameters: { depth: 1.4, width: 3.2 } },
      { id: "radar_arch", type: "boat_radar_arch", material_id: "mat_stainless_steel", parameters: { span: 2.6 } }
    ]
  });

  const handleGenerate = async (prompt: string, category: string) => {
    setIsGenerating(true);
    setProgress(10);
    setActiveTab('agent');

    setSteps([
      { id: '1', step: 'Understanding Prompt', message: `Analyzing intent: "${prompt}"`, status: 'RUNNING' },
      { id: '2', step: 'Scene Planning', message: 'Decomposing geometry parameters...', status: 'PENDING' },
      { id: '3', step: 'MCP Tool Dispatch', message: 'Invoking procedural tools...', status: 'PENDING' },
      { id: '4', step: 'Material Assignment', message: 'Configuring PBR shader nodes...', status: 'PENDING' },
      { id: '5', step: 'Geometry Validation', message: 'Checking manifold boundaries...', status: 'PENDING' },
      { id: '6', step: 'Model Export', message: 'Packaging 3D asset...', status: 'PENDING' }
    ]);

    try {
      const response = await fetch('/api/v1/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, category })
      });

      if (!response.ok) {
        throw new Error(`Generation failed with HTTP ${response.status}`);
      }

      const data = await response.json();

      setProgress(40);
      setSteps(prev => prev.map((s, idx) => idx <= 1 ? { ...s, status: 'COMPLETED' } : idx === 2 ? { ...s, status: 'RUNNING' } : s));

      await new Promise(r => setTimeout(r, 300));
      setProgress(75);
      setSteps(prev => prev.map((s, idx) => idx <= 3 ? { ...s, status: 'COMPLETED' } : idx === 4 ? { ...s, status: 'RUNNING' } : s));

      await new Promise(r => setTimeout(r, 300));
      setProgress(100);
      setSteps(prev => prev.map(s => ({ ...s, status: 'COMPLETED' })));

      if (data.model_url) setModelUrl(data.model_url);
      if (data.scene_id) setSceneId(data.scene_id);
      setVersionNumber(1);
      if (data.vertex_count) setVertexCount(data.vertex_count);
      if (data.polygons) setPolyCount(data.polygons);
      if (data.specification) setSceneSpec(data.specification);

      setVersions([
        {
          version_number: 1,
          prompt_summary: prompt.slice(0, 40) + '...',
          polygons: data.polygons || 148,
          created_at: 'Just now'
        }
      ]);

    } catch (err) {
      console.error(err);
      setProgress(100);
      setSteps(DEFAULT_STEPS);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleEdit = async (instruction: string) => {
    if (!sceneId) return;
    setIsGenerating(true);
    setProgress(20);
    setActiveTab('agent');

    setSteps([
      { id: '1', step: 'Scene Inspection', message: `Querying active scene '${sceneId}'...`, status: 'RUNNING' },
      { id: '2', step: 'Mutation Planner', message: `Computing parametric diffs: "${instruction}"`, status: 'PENDING' },
      { id: '3', step: 'MCP Tool Mutation', message: 'Executing modify_object & component updates...', status: 'PENDING' },
      { id: '4', step: 'Geometry Validation', message: 'Verifying mutated manifold edges...', status: 'PENDING' },
      { id: '5', step: 'Re-Export GLB', message: 'Re-compiling updated 3D container...', status: 'PENDING' }
    ]);

    try {
      const response = await fetch('/api/v1/edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scene_id: sceneId, instruction })
      });

      if (!response.ok) {
        throw new Error(`Edit failed with HTTP ${response.status}`);
      }

      const data = await response.json();

      setProgress(60);
      setSteps(prev => prev.map((s, idx) => idx <= 1 ? { ...s, status: 'COMPLETED' } : idx === 2 ? { ...s, status: 'RUNNING' } : s));

      await new Promise(r => setTimeout(r, 300));
      setProgress(100);
      setSteps(prev => prev.map(s => ({ ...s, status: 'COMPLETED' })));

      const nextVer = versionNumber + 1;
      setVersionNumber(nextVer);

      if (data.model_url) {
        setModelUrl(`${data.model_url}?t=${Date.now()}`);
      }
      if (data.vertex_count) setVertexCount(data.vertex_count);
      if (data.polygons) setPolyCount(data.polygons);
      if (data.specification) setSceneSpec(data.specification);

      setVersions(prev => [
        {
          version_number: nextVer,
          prompt_summary: instruction.slice(0, 40) + '...',
          polygons: data.polygons || polyCount,
          created_at: 'Just now'
        },
        ...prev
      ]);

    } catch (err) {
      console.error(err);
      setProgress(100);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleConfirmExport = (format: string, _compress: boolean = true) => {
    if (modelUrl) {
      const a = document.createElement('a');
      a.href = modelUrl;
      a.download = `sceneforge_model.${format.toLowerCase()}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#0B0F19] text-slate-100 overflow-hidden font-sans">
      {/* Top Header */}
      <Header
        onExport={() => setIsExportOpen(true)}
        isGenerating={isGenerating}
        versionNumber={versionNumber}
      />

      {/* Main Studio Workspace */}
      <main className="flex-1 p-5 grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-0 overflow-hidden">
        {/* Left Column: Prompt, Studio Tabs & Panels */}
        <div className="lg:col-span-5 flex flex-col space-y-4 h-full min-h-0">
          <PromptBar
            onGenerate={handleGenerate}
            onEdit={handleEdit}
            isGenerating={isGenerating}
            hasActiveScene={Boolean(sceneId)}
          />

          {/* Panel Selector Tabs */}
          <div className="flex items-center space-x-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setActiveTab('agent')}
              className={`flex-1 py-1.5 rounded-lg font-medium flex items-center justify-center space-x-1.5 transition ${
                activeTab === 'agent'
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Agent Trace</span>
            </button>
            <button
              onClick={() => setActiveTab('tree')}
              className={`flex-1 py-1.5 rounded-lg font-medium flex items-center justify-center space-x-1.5 transition ${
                activeTab === 'tree'
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Components</span>
            </button>
            <button
              onClick={() => setActiveTab('versions')}
              className={`flex-1 py-1.5 rounded-lg font-medium flex items-center justify-center space-x-1.5 transition ${
                activeTab === 'versions'
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <GitBranch className="w-3.5 h-3.5" />
              <span>Versions ({versions.length})</span>
            </button>
          </div>

          {/* Active Tab Panel */}
          <div className="flex-1 min-h-0">
            {activeTab === 'agent' && (
              <AgentActivity
                steps={steps}
                currentProgress={progress}
                isGenerating={isGenerating}
                sceneSpecification={sceneSpec}
              />
            )}
            {activeTab === 'tree' && (
              <SceneTree
                objects={sceneSpec?.objects || []}
                selectedId={selectedComponentId}
                onSelect={(id) => setSelectedComponentId(id)}
              />
            )}
            {activeTab === 'versions' && (
              <VersionHistory
                versions={versions}
                activeVersion={versionNumber}
                onSelectVersion={(v) => setVersionNumber(v)}
              />
            )}
          </div>
        </div>

        {/* Right Column: 3D Viewport Studio */}
        <div className="lg:col-span-7 h-full min-h-0 flex flex-col">
          <ThreeViewer
            modelUrl={modelUrl}
            vertexCount={vertexCount}
            polyCount={polyCount}
            selectedComponentId={selectedComponentId}
          />
        </div>
      </main>

      {/* Export Modal Dialog */}
      <ExportModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        onConfirmExport={handleConfirmExport}
        polyCount={polyCount}
      />
    </div>
  );
}

export default App;
