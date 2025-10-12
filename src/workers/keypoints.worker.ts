/// <reference lib="webworker" />
import type { WorkerMsg, InferenceInput } from "@/lib/types";
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

// ---- CONSTANTES Y LÓGICA DE NORMALIZACIÓN ----

// Índices basados en MediaPipe Pose: LEFT_SHOULDER = 11, RIGHT_SHOULDER = 12.
// Multiplicamos por 3 porque cada landmark tiene 3 coordenadas (x, y, z).
const POSE_L_SHOULDER_X = 11 * 3;     // 33
const POSE_L_SHOULDER_Y = 11 * 3 + 1; // 34
const POSE_R_SHOULDER_X = 12 * 3;     // 36
const POSE_R_SHOULDER_Y = 12 * 3 + 1; // 37

/**
 * Normaliza los keypoints para hacerlos invariantes a la posición y escala.
 * - Centra el esqueleto usando el punto medio de los hombros como origen.
 * - Escala los puntos basándose en la distancia entre los hombros.
 * @param data El vector de keypoints crudos [D].
 * @returns El vector de keypoints normalizado [D].
 */
function normalizeKeypoints(data: Float32Array): Float32Array {
  const shoulderL = { x: data[POSE_L_SHOULDER_X], y: data[POSE_L_SHOULDER_Y] };
  const shoulderR = { x: data[POSE_R_SHOULDER_X], y: data[POSE_R_SHOULDER_Y] };

  // Condición de escape: si no se detectan los hombros (valores en 0),
  // no se puede normalizar. Devolver los datos crudos para evitar división por cero.
  if (shoulderL.x === 0 && shoulderL.y === 0 && shoulderR.x === 0 && shoulderR.y === 0) {
    return data;
  }

  const origin = { x: (shoulderL.x + shoulderR.x) / 2, y: (shoulderL.y + shoulderR.y) / 2 };
  const scale = Math.hypot(shoulderR.x - shoulderL.x, shoulderR.y - shoulderR.y) || 1;

  const normalizedData = new Float32Array(data.length);
  for (let i = 0; i < data.length; i += 3) {
    // No normalizar puntos que no fueron detectados (quedaron como 0,0,0)
    if (data[i] === 0 && data[i + 1] === 0 && data[i + 2] === 0) continue;

    normalizedData[i] = (data[i] - origin.x) / scale;
    normalizedData[i + 1] = (data[i + 1] - origin.y) / scale;
    normalizedData[i + 2] = data[i + 2] / scale;
  }
  return normalizedData;
}


// ---- INICIALIZACIÓN Y PROCESAMIENTO DE FRAMES ----

async function ensureMediapipe() {
  if (hands && pose) return;
  const fileset = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm");
  hands = await HandLandmarker.createFromOptions(fileset, {
    baseOptions: { modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" },
    numHands: 2, runningMode: "VIDEO",
  });
  pose = await PoseLandmarker.createFromOptions(fileset, {
    baseOptions: { modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task" },
    runningMode: "VIDEO",
  });
}

function initInferWorker() {
  if (inferWorker) return;
  inferWorker = new Worker(new URL("./infer.worker.ts", import.meta.url), { type: "module" });
  inferWorker.onmessage = (e: MessageEvent<WorkerMsg>) => ctx.postMessage(e.data); // Reenviar mensajes a UI
  inferWorker.postMessage({ type: 'init', payload: { threshold: 0.25 } });
}

function packFrame(hres: Awaited<ReturnType<MPHands['detectForVideo']>>, pres: Awaited<ReturnType<MPPose['detectForVideo']>>): Float32Array {
  const data = new Float32Array(D); // Inicializado con ceros
  if (pres?.landmarks?.[0]) {
    data.set(pres.landmarks[0].flatMap((p) => [p.x, p.y, p.z ?? 0]), 0);
  }
  if (hres?.landmarks?.length && hres.handedness?.length) {
    for (let j = 0; j < hres.landmarks.length; j++) {
      const handed = hres.handedness[j]?.[0]?.categoryName?.toLowerCase();
      if (!handed) continue;
      const flat = hres.landmarks[j].flatMap((p) => [p.x, p.y, p.z ?? 0]);
      if (handed === "left") data.set(flat, 99);
      else if (handed === "right") data.set(flat, 99 + 63);
    }
  }
  return data;
}

// ---- MANEJADOR PRINCIPAL DEL WORKER ----

ctx.onmessage = async (ev: MessageEvent<WorkerMsg>) => {
  const { type, payload } = ev.data;
  try {
    if (type === "init") {
      T = (payload as { T: number }).T || 48;
      D = (payload as { D: number }).D || 225;
      buffer = [];
      await ensureMediapipe();
      initInferWorker();
      return;
    }

    if (type === "frame") {
      if (!hands || !pose || !inferWorker) return;
      const { video, ts } = payload as { video: ImageBitmap; ts: number };

      const [hres, pres] = await Promise.all([
        hands.detectForVideo(video, ts),
        pose.detectForVideo(video, ts)
      ]);

      const rawVec = packFrame(hres, pres);
      const normalizedVec = normalizeKeypoints(rawVec); // Invocación clave

      buffer.push(normalizedVec); // Se añade el vector ya normalizado
      if (buffer.length > T) buffer.shift();

      if (buffer.length === T) {
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