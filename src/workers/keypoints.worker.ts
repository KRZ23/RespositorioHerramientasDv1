/// <reference lib="webworker" />
import type { WorkerMsg, KeypointsFrame, InferenceInput } from "@/lib/types";
const ctx: DedicatedWorkerGlobalScope = self as DedicatedWorkerGlobalScope;

import { FilesetResolver, HandLandmarker, PoseLandmarker } from "@mediapipe/tasks-vision";
type MPHands = HandLandmarker;
type MPPose = PoseLandmarker;

let hands: MPHands | null = null;
let pose: MPPose | null = null;
let inferWorker: Worker | null = null;

let buffer: Float32Array[] = [];
let T = 48; // frames por ventana
let D = 225; // dimensiones del vector: pose(99) + left(63) + right(63)

// ---- Inicialización de Modelos y Workers ----
async function ensureMediapipe() {
  if (hands && pose) return;
  
  const fileset = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm"
  );

  hands = await HandLandmarker.createFromOptions(fileset, {
    baseOptions: {
      modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
    },
    numHands: 2,
    runningMode: "VIDEO",
  });

  pose = await PoseLandmarker.createFromOptions(fileset, {
    baseOptions: {
      modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
    },
    runningMode: "VIDEO",
  });
}

function initInferWorker() {
    if (inferWorker) return;
    inferWorker = new Worker(new URL("./infer.worker.ts", import.meta.url), { type: "module" });
    
    // Reenviamos los mensajes del worker de inferencia al hilo principal
    inferWorker.onmessage = (e: MessageEvent<WorkerMsg>) => {
        ctx.postMessage(e.data);
    };

    // Inicializamos el worker de inferencia
    inferWorker.postMessage({ type: 'init', payload: { threshold: 0.25 } });
}

// ---- Lógica de Procesamiento de Frames ----

// Empaqueta los landmarks en un solo vector Float32Array
function packFrame(hres: Awaited<ReturnType<MPHands['detectForVideo']>>, pres: Awaited<ReturnType<MPPose['detectForVideo']>>): Float32Array {
  const data = new Float32Array(D); // Inicializado con ceros

  // Pose (primer cuerpo detectado)
  if (pres?.landmarks?.[0]) {
    const flat = pres.landmarks[0].flatMap((p) => [p.x, p.y, p.z ?? 0]);
    data.set(flat, 0); // offset 0
  }

  // Manos
  if (hres?.landmarks?.length && hres.handedness?.length) {
    for (let j = 0; j < hres.landmarks.length; j++) {
      const handed = hres.handedness[j]?.[0]?.categoryName?.toLowerCase();
      if (!handed) continue;
      
      const flat = hres.landmarks[j].flatMap((p) => [p.x, p.y, p.z ?? 0]);
      if (handed === "left") {
        data.set(flat, 99); // offset pose
      } else if (handed === "right") {
        data.set(flat, 99 + 63); // offset pose + left
      }
    }
  }
  return data;
}

// ---- Manejador de Mensajes del Worker ----
ctx.onmessage = async (ev: MessageEvent<WorkerMsg>) => {
  const { type, payload } = ev.data;

  try {
    if (type === "init") {
      T = (payload as {T: number}).T || 48;
      D = (payload as {D: number}).D || 225;
      buffer = [];
      await ensureMediapipe();
      initInferWorker();
      // No enviamos "ready" hasta que el worker de inferencia también esté listo.
      // El worker de inferencia enviará su propio "ready", que será reenviado.
      return;
    }

    if (type === "frame") {
      if (!hands || !pose || !inferWorker) return;
      const { video, ts } = payload as { video: ImageBitmap; ts: number };

      const hres = hands.detectForVideo(video, ts);
      const pres = pose.detectForVideo(video, ts);
      const [hres_awaited, pres_awaited] = await Promise.all([hres, pres]);

      const vec = packFrame(hres_awaited, pres_awaited);
      buffer.push(vec);
      if (buffer.length > T) buffer.shift();

      if (buffer.length === T) {
        // Aplanar [T, D] -> [T * D] y enviar al worker de inferencia
        const flat = new Float32Array(T * D);
        for (let t = 0; t < T; t++) flat.set(buffer[t], t * D);
        
        const input: InferenceInput = { data: flat, T, D };
        inferWorker.postMessage({ type: "infer", payload: input } as WorkerMsg);
      }

      video.close();
      return;
    }

  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    ctx.postMessage({ type: "error", error: errorMessage } as WorkerMsg);
  }
};