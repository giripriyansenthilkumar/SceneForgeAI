import React, { Suspense, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Center, useGLTF } from '@react-three/drei';
import { Camera, RotateCw, Layers } from 'lucide-react';
import * as THREE from 'three';

interface ModelProps {
  url: string;
  wireframe: boolean;
}

function Model({ url, wireframe }: ModelProps) {
  const { scene } = useGLTF(url);

  // Apply wireframe override if toggled
  scene.traverse((child) => {
    if ((child as THREE.Mesh).isMesh) {
      const mesh = child as THREE.Mesh;
      if (Array.isArray(mesh.material)) {
        mesh.material.forEach((mat: any) => {
          mat.wireframe = wireframe;
        });
      } else if (mesh.material) {
        (mesh.material as any).wireframe = wireframe;
      }
    }
  });

  return (
    <primitive
      object={scene}
      scale={1}
      position={[0, 0, 0]}
    />
  );
}

// Parametric fallback assembly
function ProceduralMeshFallback({ wireframe }: { wireframe: boolean }) {
  return (
    <group position={[0, 0.5, 0]}>
      {/* Hull */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[8, 2.5, 1.2]} />
        <meshStandardMaterial color="#F3F4F6" roughness={0.15} metalness={0.05} wireframe={wireframe} />
      </mesh>
      {/* Deck */}
      <mesh position={[0, 0.65, 0]}>
        <boxGeometry args={[7.6, 2.3, 0.1]} />
        <meshStandardMaterial color="#92400E" roughness={0.5} metalness={0.0} wireframe={wireframe} />
      </mesh>
      {/* Cabin */}
      <mesh position={[-0.5, 1.3, 0]}>
        <boxGeometry args={[3.8, 1.8, 1.2]} />
        <meshStandardMaterial color="#E5E7EB" roughness={0.2} metalness={0.1} wireframe={wireframe} />
      </mesh>
      {/* Glass */}
      <mesh position={[-0.4, 1.45, 0]}>
        <boxGeometry args={[4.0, 1.9, 0.4]} />
        <meshStandardMaterial color="#1E293B" roughness={0.05} metalness={0.2} transparent opacity={0.85} wireframe={wireframe} />
      </mesh>
      {/* Swim Platform */}
      <mesh position={[-4.5, 0.2, 0]}>
        <boxGeometry args={[1.2, 2.2, 0.15]} />
        <meshStandardMaterial color="#92400E" roughness={0.5} metalness={0.0} wireframe={wireframe} />
      </mesh>
    </group>
  );
}

interface ThreeViewerProps {
  modelUrl?: string | null;
  vertexCount?: number;
  polyCount?: number;
  selectedComponentId?: string | null;
}

export const ThreeViewer: React.FC<ThreeViewerProps> = ({
  modelUrl,
  vertexCount = 296,
  polyCount = 148,
  selectedComponentId
}) => {
  const controlsRef = useRef<any>(null);

  const [wireframe, setWireframe] = useState<boolean>(false);
  const [autoRotate, setAutoRotate] = useState<boolean>(false);
  const lightingTheme: 'marine' = 'marine';

  const setCameraPreset = (position: [number, number, number]) => {
    if (controlsRef.current) {
      controlsRef.current.object.position.set(...position);
      controlsRef.current.target.set(0, 0.5, 0);
      controlsRef.current.update();
    }
  };

  const captureSnapshot = () => {
    const canvas = document.querySelector('canvas');
    if (canvas) {
      const dataUrl = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = 'sceneforge_snapshot.png';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="relative w-full h-full bg-[#080C14] rounded-2xl overflow-hidden border border-slate-800/80 shadow-2xl flex flex-col">
      {/* Top Viewport Toolbar */}
      <div className="absolute top-4 left-4 right-4 z-10 flex items-center justify-between pointer-events-none">
        {/* Left: Mesh HUD Stats */}
        <div className="flex items-center space-x-2 pointer-events-auto">
          <div className="px-3 py-1.5 rounded-lg glass-card flex items-center space-x-2 border border-slate-700/60 text-xs shadow-lg">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-mono text-slate-300">PBR Live</span>
          </div>
          <div className="px-3 py-1.5 rounded-lg glass-card text-xs font-mono text-slate-300 border border-slate-700/60 shadow-lg">
            <span>Polys: </span>
            <span className="text-blue-400 font-semibold">{polyCount.toLocaleString()}</span>
          </div>
          <div className="px-3 py-1.5 rounded-lg glass-card text-xs font-mono text-slate-300 border border-slate-700/60 shadow-lg">
            <span>Verts: </span>
            <span className="text-teal-400 font-semibold">{vertexCount.toLocaleString()}</span>
          </div>
          {selectedComponentId && (
            <div className="px-3 py-1.5 rounded-lg glass-card text-xs font-mono text-amber-400 border border-amber-500/40 shadow-lg">
              <span>Inspect: </span>
              <span className="font-semibold">{selectedComponentId}</span>
            </div>
          )}
        </div>

        {/* Right: Camera & Render Controls */}
        <div className="flex items-center space-x-1.5 bg-slate-900/90 backdrop-blur-md p-1.5 rounded-xl border border-slate-800 pointer-events-auto shadow-xl">
          {/* Camera Presets */}
          <button
            onClick={() => setCameraPreset([12, 8, 12])}
            title="Isometric Quarter View"
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition text-xs font-mono"
          >
            ISO
          </button>
          <button
            onClick={() => setCameraPreset([0, 1.5, 15])}
            title="Front View"
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition text-xs font-mono"
          >
            FRT
          </button>
          <button
            onClick={() => setCameraPreset([15, 1.5, 0])}
            title="Side Profile View"
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition text-xs font-mono"
          >
            SIDE
          </button>
          <button
            onClick={() => setCameraPreset([0, 18, 0])}
            title="Top Plan View"
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition text-xs font-mono"
          >
            TOP
          </button>

          <div className="w-px h-4 bg-slate-800 mx-1"></div>

          {/* Wireframe Toggle */}
          <button
            onClick={() => setWireframe(!wireframe)}
            title="Toggle Wireframe Mesh"
            className={`p-1.5 rounded-lg transition ${
              wireframe ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Layers className="w-4 h-4" />
          </button>

          {/* Auto Rotate Toggle */}
          <button
            onClick={() => setAutoRotate(!autoRotate)}
            title="Toggle Auto Orbit"
            className={`p-1.5 rounded-lg transition ${
              autoRotate ? 'bg-teal-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <RotateCw className={`w-4 h-4 ${autoRotate ? 'animate-spin' : ''}`} />
          </button>

          {/* Snapshot Capture */}
          <button
            onClick={captureSnapshot}
            title="Capture Viewport Screenshot"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <Camera className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 3D WebGL Canvas */}
      <div className="flex-1 w-full h-full">
        <Canvas
          camera={{ position: [12, 8, 12], fov: 42 }}
          shadows
          gl={{ preserveDrawingBuffer: true, antialias: true }}
          className="w-full h-full cursor-grab active:cursor-grabbing"
        >
          <color
            attach="background"
            args={[
              lightingTheme === 'marine' ? '#070D18' : lightingTheme === 'cyber' ? '#090514' : '#0B0F19'
            ]}
          />

          <ambientLight intensity={lightingTheme === 'marine' ? 0.9 : 0.7} />
          <directionalLight
            position={[10, 16, 10]}
            intensity={lightingTheme === 'marine' ? 1.8 : 1.4}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <pointLight position={[-12, 6, -10]} intensity={0.6} color="#60A5FA" />
          <pointLight position={[12, -4, 10]} intensity={0.4} color="#14B8A6" />

          <Suspense fallback={<ProceduralMeshFallback wireframe={wireframe} />}>
            <Center top>
              {modelUrl ? (
                <Model url={modelUrl} wireframe={wireframe} />
              ) : (
                <ProceduralMeshFallback wireframe={wireframe} />
              )}
            </Center>
          </Suspense>

          <Grid
            renderOrder={-1}
            position={[0, -0.01, 0]}
            infiniteGrid
            cellSize={1}
            cellThickness={0.6}
            cellColor="#1E293B"
            sectionSize={5}
            sectionThickness={1.2}
            sectionColor="#3B82F6"
            fadeDistance={45}
          />

          <OrbitControls
            ref={controlsRef}
            makeDefault
            autoRotate={autoRotate}
            autoRotateSpeed={1.5}
            minDistance={3}
            maxDistance={50}
            maxPolarAngle={Math.PI / 2 + 0.05}
          />
        </Canvas>
      </div>

      {/* Viewport Bottom HUD Helper */}
      <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between pointer-events-none text-[11px] font-mono text-slate-400">
        <div className="px-3 py-1.5 rounded-lg glass-card border border-slate-800/80 pointer-events-auto">
          Dimensions: <span className="text-slate-200">12.0m</span> L × <span className="text-slate-200">3.8m</span> B × <span className="text-slate-200">3.4m</span> H
        </div>

        <div className="px-3 py-1.5 rounded-lg glass-card border border-slate-800/80 pointer-events-auto">
          Left Drag: Rotate • Right Drag: Pan • Scroll: Zoom
        </div>
      </div>
    </div>
  );
};
