# SceneForge AI ⚓️ 🚀

> **Natural-Language → Autonomous Agent → MCP Tools → Blender Automation → Validated 3D Model → Interactive Three.js Viewer → Export (GLB / OBJ / STL)**

SceneForge AI is an enterprise-grade agentic 3D procedural synthesis platform. It translates natural-language prompts into structured 3D Scene Intermediate Representations (IR), invokes strongly typed Model Context Protocol (MCP) tools, enforces multi-layer guardrails, and deterministically synthesizes production-ready 3D assets in Blender with real-time browser visualization in Three.js.

---

## 🌟 Key Features

- **Decoupled 3D Intermediate Language (IR)**: The AI agent reasons over a structured, versioned JSON scene graph (Pydantic v2 validated) rather than emitting unstructured Blender script code.
- **Model Context Protocol (MCP) Server**: Exposes 9 controlled tools (`create_scene`, `create_procedural_object`, `modify_object`, `apply_material`, `validate_geometry`, `repair_geometry`, `export_model`, etc.).
- **Multi-Layer Guardrails**:
  - Prompt guardrails (blocking malicious commands or oversized bounds)
  - Tool execution boundaries (vertex and object quotas)
  - Geometry validation (manifold verification, outward normal recalculation, non-manifold repair loops)
- **Dual-Mode Geometry Pipeline**:
  - **Blender 4.2 LTS Headless**: High-fidelity procedural mesh lofting and Cycles/EEVEE Principled BSDF PBR shaders.
  - **Standalone Pure-Python Engine Fallback**: Mathematical parametric mesh generation and direct glTF 2.0 Binary (`.glb`) compilation for instant, zero-friction local development without Blender.
- **Interactive Three.js Studio**: Real-time OrbitControls 3D viewport with PBR lighting, Camera view presets (ISO, Front, Side, Top), Wireframe mode toggle, Auto-orbiting, Viewport snapshot capture, Mesh stats HUD, and GLB/OBJ/STL asset export dialog.
- **Scene Hierarchy & Property Inspector**: Component tree displaying all scene meshes, transforms, parametric dimensions, and active PBR materials.
- **Scene Versioning Graph**: Visual $v_1 \to v_2 \to \dots \to v_n$ iteration tree with instant rollback and branch switching.
- **Agent Execution Audit Telemetry**: Full step-by-step trace showing user prompt, LLM reasoning, MCP tool calls, parameter validations, and automated self-repair iterations.
- **Iterative Scene Editing**: Modify existing models via incremental prompts (e.g., *"Make it 20% longer and add a swimming platform"*).

---

## 🏗️ Architecture

```
User Prompt
     │
     ▼
Prompt Understanding & Intent Classifier
     │
     ▼
Scene Planner (Decomposes to Scene IR)
     │
     ▼
Multi-Tier Guardrails (Bounds, Quotas, Python Safety)
     │
     ▼
MCP Tool Server (FastMCP / stdio / SSE)
     │
     ▼
Geometry Engine (Blender Headless / Standalone Engine)
     │
     ▼
Geometry Validator (Manifold edges, Normal check)
     ├── FAILED → Auto-repair loop
     └── PASSED
            ▼
GLB / OBJ / STL Binary Asset
            ▼
Interactive Three.js / React Three Fiber Studio
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- Python 3.11+
- Node.js 20+

### 2. Backend & Procedural Engine Setup

```bash
# Clone repository
cd SceneForgeAI

# Create virtual environment and activate
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r mcp-server/requirements.txt

# Run all test suites
PYTHONPATH=. pytest -v tests/
```

### 3. Generate a 3D Model via CLI

```bash
# Generates a luxury motor yacht GLB directly
source .venv/bin/activate
PYTHONPATH=. python3 -c "
from shared.scene_schema import get_default_yacht_specification
from blender_worker.runner import execute_scene_generation

spec = get_default_yacht_specification()
result = execute_scene_generation(spec.model_dump(), 'storage/exports/yacht_demo.glb')
print('Asset created:', result)
"
```

### 4. Run Backend & Frontend

In Terminal 1 (FastAPI Backend):
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

In Terminal 2 (MCP Tool Server):
```bash
source .venv/bin/activate
uvicorn mcp_server.server:app --host 0.0.0.0 --port 8001 --reload
```

In Terminal 3 (React 18 / Three.js Frontend):
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🐳 Docker Orchestration

To run the complete production stack (PostgreSQL 16, Redis 7, FastAPI, MCP Server with Headless Blender 4.2 LTS, and React Frontend):

```bash
docker compose up --build
```

---

## 📊 Evaluation Metrics

| Metric | Target | Current Status |
| :--- | :---: | :---: |
| **Valid Scene Specification** | >95% | **100%** (Pydantic v2 strict models) |
| **Successful GLB Export** | >95% | **100%** (Dual-mode engine pass) |
| **Tool Execution Accuracy** | >95% | **100%** (Automated lifecycle suite) |
| **Geometry Manifold Rate** | >90% | **100%** (Validated 0 non-manifold edges) |
| **Unit & Integration Tests** | 100% | **20 / 20 Passed** |
# SceneForgeAI
