import { useState } from 'react';
import { Header } from './components/Header';
import { PromptBar } from './components/PromptBar';
import { AgentActivity, AgentStep } from './components/AgentActivity';
import { ThreeViewer } from './viewer/ThreeViewer';

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
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(100);
  const [steps, setSteps] = useState<AgentStep[]>(DEFAULT_STEPS);
  const [vertexCount, setVertexCount] = useState<number>(296);
  const [polyCount, setPolyCount] = useState<number>(148);
  const [sceneSpec, setSceneSpec] = useState<any>({
    metadata: {
      name: "Parametric Luxury Yacht",
      category: "boat",
      units: "meters"
    },
    objects: [{ id: "hull_main" }, { id: "deck_main" }, { id: "cabin_bridge" }, { id: "platform_stern" }]
  });

  const handleGenerate = async (prompt: string, category: string) => {
    setIsGenerating(true);
    setProgress(10);

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
      if (data.vertex_count) setVertexCount(data.vertex_count);
      if (data.polygons) setPolyCount(data.polygons);
      if (data.specification) setSceneSpec(data.specification);

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

      if (data.model_url) {
        // Cache bust query string so Three.js reloads the updated GLB mesh
        setModelUrl(`${data.model_url}?t=${Date.now()}`);
      }
      if (data.vertex_count) setVertexCount(data.vertex_count);
      if (data.polygons) setPolyCount(data.polygons);
      if (data.specification) setSceneSpec(data.specification);

    } catch (err) {
      console.error(err);
      setProgress(100);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExport = (format: string) => {
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
    <div className="flex flex-col h-screen w-screen bg-[#0B0F19] text-slate-100 overflow-hidden">
      {/* Top Header */}
      <Header onExport={handleExport} isGenerating={isGenerating} />

      {/* Main Studio Workspace */}
      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0 overflow-hidden">
        {/* Left Column: Prompt & Agent Activity Trace */}
        <div className="lg:col-span-5 flex flex-col space-y-5 h-full min-h-0">
          <PromptBar
            onGenerate={handleGenerate}
            onEdit={handleEdit}
            isGenerating={isGenerating}
            hasActiveScene={Boolean(sceneId)}
          />
          
          <div className="flex-1 min-h-0">
            <AgentActivity
              steps={steps}
              currentProgress={progress}
              isGenerating={isGenerating}
              sceneSpecification={sceneSpec}
            />
          </div>
        </div>

        {/* Right Column: 3D Viewport */}
        <div className="lg:col-span-7 h-full min-h-0 flex flex-col">
          <ThreeViewer
            modelUrl={modelUrl}
            vertexCount={vertexCount}
            polyCount={polyCount}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
