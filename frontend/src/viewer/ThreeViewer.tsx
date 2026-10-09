import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Center, useGLTF } from '@react-three/drei';

interface ModelProps {
  url: string;
}

function Model({ url }: ModelProps) {
  const { scene } = useGLTF(url);
  return (
    <primitive
      object={scene}
      scale={1}
      position={[0, 0, 0]}
    />
  );
}

// Fallback procedural visual representation when GLTF is loading
function ProceduralMeshFallback() {
  return (
    <group position={[0, 0.5, 0]}>
      {/* Hull Representation */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[8, 2.5, 1.2]} />
        <meshStandardMaterial color="#F3F4F6" roughness={0.15} metalness={0.05} />
      </mesh>
      {/* Deck */}
      <mesh position={[0, 0.65, 0]}>
        <boxGeometry args={[7.6, 2.3, 0.1]} />
        <meshStandardMaterial color="#92400E" roughness={0.5} metalness={0.0} />
      </mesh>
      {/* Cabin */}
      <mesh position={[-0.5, 1.3, 0]}>
        <boxGeometry args={[3.8, 1.8, 1.2]} />
        <meshStandardMaterial color="#E5E7EB" roughness={0.2} metalness={0.1} />
      </mesh>
      {/* Glass */}
      <mesh position={[-0.4, 1.45, 0]}>
        <boxGeometry args={[4.0, 1.9, 0.4]} />
        <meshStandardMaterial color="#1E293B" roughness={0.05} metalness={0.2} transparent opacity={0.85} />
      </mesh>
      {/* Swim Platform */}
      <mesh position={[-4.5, 0.2, 0]}>
        <boxGeometry args={[1.2, 2.2, 0.15]} />
        <meshStandardMaterial color="#92400E" roughness={0.5} metalness={0.0} />
      </mesh>
    </group>
  );
}

interface ThreeViewerProps {
  modelUrl?: string | null;
  vertexCount?: number;
  polyCount?: number;
}

export const ThreeViewer: React.FC<ThreeViewerProps> = ({
  modelUrl,
  vertexCount = 296,
  polyCount = 148
}) => {
  return (
    <div className="relative w-full h-full bg-[#080C14] rounded-2xl overflow-hidden border border-slate-800/80 shadow-2xl">
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [12, 8, 12], fov: 42 }}
        shadows
        className="w-full h-full cursor-grab active:cursor-grabbing"
      >
        <color attach="background" args={['#080C14']} />
        
        <ambientLight intensity={0.8} />
        <directionalLight
          position={[10, 15, 10]}
          intensity={1.5}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <pointLight position={[-10, 5, -10]} intensity={0.5} />

        <Suspense fallback={<ProceduralMeshFallback />}>
          <Center top>
            {modelUrl ? <Model url={modelUrl} /> : <ProceduralMeshFallback />}
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
          makeDefault
          minDistance={3}
          maxDistance={50}
          maxPolarAngle={Math.PI / 2 + 0.05}
        />
      </Canvas>

      {/* Floating HUD Badges */}
      <div className="absolute top-4 left-4 flex items-center space-x-2">
        <div className="px-3 py-1.5 rounded-lg glass-card flex items-center space-x-2 border border-slate-700/60 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-mono text-slate-300">WebGL 2.0 PBR</span>
        </div>
        <div className="px-3 py-1.5 rounded-lg glass-card text-xs font-mono text-slate-300 border border-slate-700/60">
          <span>Polys: </span>
          <span className="text-blue-400 font-semibold">{polyCount.toLocaleString()}</span>
        </div>
        <div className="px-3 py-1.5 rounded-lg glass-card text-xs font-mono text-slate-300 border border-slate-700/60">
          <span>Verts: </span>
          <span className="text-teal-400 font-semibold">{vertexCount.toLocaleString()}</span>
        </div>
      </div>

      {/* Viewport Control Instructions */}
      <div className="absolute bottom-4 right-4 px-3 py-1.5 rounded-lg glass-card text-[11px] text-slate-400 font-mono border border-slate-800">
        Left Click: Rotate • Right Click: Pan • Scroll: Zoom
      </div>
    </div>
  );
};
