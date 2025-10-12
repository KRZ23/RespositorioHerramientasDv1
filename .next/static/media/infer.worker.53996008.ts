/// <reference lib="webworker" />
import type { WorkerMsg, InferenceInput, InferenceOutput, TopK } from "@/lib/types";
import { InferenceSession, Tensor } from 'onnxruntime-web';

const ctx: DedicatedWorkerGlobalScope = self as DedicatedWorkerGlobalScope;

let session: InferenceSession | null = null;
let THRESHOLD = 0.25;
const LABELS = ["HOLA", "GRACIAS", "ADIOS", "SI", "NO", "PORFAVOR"]; // Ejemplo

// ---- Carga del Modelo y Lógica de Inferencia ----

async function initONNX() {
  try {
    // Asegúrate de que el modelo está en la carpeta /public
    session = await InferenceSession.create('./lsp_model.onnx');
    console.log("ONNX session created successfully.");
  } catch (error) {
    console.error("Failed to create ONNX session:", error);
    throw new Error("Could not load the ONNX model.");
  }
}

async function runONNXInference(input: InferenceInput): Promise<InferenceOutput> {
    if (!session) throw new Error("ONNX session not initialized.");
    const { data, T, D } = input;
    
    const tensor = new Tensor('float32', data, [1, T, D]);
    const feeds = { "input_sequence": tensor }; // El nombre "input_sequence" debe coincidir
    
    const results = await session.run(feeds);
    // El nombre "output_label" debe coincidir con el de tu modelo
    const outputTensor = results.output_label; 
    
    // Procesa el tensor de salida para obtener scores
    const scores = Array.from(outputTensor.data as Float32Array);
    const topk: TopK[] = scores
      .map((score, i) => ({ label: LABELS[i] || `class_${i}`, score }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
      
    const accepted = topk[0].score >= THRESHOLD;
    return { topk, accepted, latencyMs: 0 }; // Latency se calculará fuera
}

// Inferencia SIMULADA para desarrollo sin un modelo real
function runMockInference(input: InferenceInput): InferenceOutput {
  const { T } = input;
  // Simulación: elige una etiqueta aleatoria y asígnale un score alto
  const randomIndex = Math.floor(Math.random() * LABELS.length);
  const topk: TopK[] = LABELS.map((label, i) => ({
    label,
    score: i === randomIndex ? 0.8 + Math.random() * 0.2 : Math.random() * 0.1,
  }))
  .sort((a, b) => b.score - a.score)
  .slice(0, 3);
  
  const accepted = topk[0].score >= THRESHOLD;
  return { topk, accepted, latencyMs: Math.random() * 20 + 5 }; // Latencia simulada
}

// ---- Manejador de Mensajes del Worker ----
ctx.onmessage = async (ev: MessageEvent<WorkerMsg>) => {
  const { type, payload } = ev.data;

  try {
    if (type === "init") {
      THRESHOLD = (payload as { threshold: number })?.threshold || 0.25;
      // Descomenta la siguiente línea para usar tu modelo ONNX real
      // await initONNX(); 
      ctx.postMessage({ type: "ready" } as WorkerMsg);
      return;
    }

    if (type === "infer") {
      const t0 = performance.now();
      
      // CAMBIA a runONNXInference cuando tengas tu modelo
      const res = runMockInference(payload as InferenceInput);
      
      res.latencyMs = performance.now() - t0;
      ctx.postMessage({ type: "result", payload: res } as WorkerMsg<InferenceOutput>);
      return;
    }
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    ctx.postMessage({ type: "error", error: errorMessage } as WorkerMsg);
  }
};