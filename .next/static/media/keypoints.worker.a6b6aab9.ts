// src/workers/keypoints.worker.ts

/// <reference lib="webworker" />
import type { WorkerMsg, InferenceInput, WindowSample } from "@/lib/types";
const ctx: DedicatedWorkerGlobalScope = self as DedicatedWorkerGlobalScope;

import { FilesetResolver, HandLandmarker, PoseLandmarker } from "@mediapipe/tasks-vision";
type MPHands = HandLandmarker;
type MPPose = PoseLandmarker;

let hands: MPHands | null = null;
let pose: MPPose | null = null;
let inferWorker: Worker | null = null;

let buffer: Float32Array[] = [];
let T = 48;
let D = 225;
let isCollectionMode = false;

const POSE_L_SHOULDER_X = 11 * 3;
const POSE_L_SHOULDER_Y = 11 * 3 + 1;
const POSE_R_SHOULDER_X = 12 * 3;
const POSE_R_SHOULDER_Y = 12 * 3 + 1;

function normalizeKeypoints(data: Float32Array): Float32Array {
  const shoulderL = { x: data[POSE_L_SHOULDER_X], y: data[POSE_L_SHOULDER_Y] };
  const shoulderR = { x: data[POSE_R_SHOULDER_X], y: data[POSE_R_SHOULDER_Y] };
  if (shoulderL.x === 0 && shoulderL.y === 0 && shoulderR.x === 0 && shoulderR.y === 0) return data;
  const origin = { x: (shoulderL.x + shoulderR.x) / 2, y: (shoulderL.y + shoulderR.y) / 2 };
  const scale = Math.hypot(shoulderR.x - shoulderL.x, shoulderR.y - shoulderR.y) || 1;
  const normalizedData = new Float32Array(data.length);
  for (let i = 0; i < data.length; i += 3) {
    if (data[i] === 0 && data[i + 1] === 0 && data[i + 2] === 0) continue;
    normalizedData[i] = (data[i] - origin.x) / scale;
    normalizedData[i + 1] = (data[i + 1] - origin.y) / scale;
    normalizedData[i + 2] = data[i + 2] / scale;
  }
  return normalizedData;
}

async function ensureMediapipe() {
  if (hands && pose) return;
  const fileset = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm");
  hands = await HandLandmarker.createFromOptions(fileset, { baseOptions: { modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" }, numHands: 2, runningMode: "VIDEO" });
  pose = await PoseLandmarker.createFromOptions(fileset, { baseOptions: { modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task" }, runningMode: "VIDEO" });
}

function initInferWorker() {
  if (inferWorker) return;
  inferWorker = new Worker(new URL("./infer.worker.ts", import.meta.url), { type: "module" });
  inferWorker.onmessage = (e: MessageEvent<WorkerMsg>) => ctx.postMessage(e.data);
  inferWorker.postMessage({ type: 'init', payload: { threshold: 0.25 } });
}

function packFrame(hres: Awaited<ReturnType<MPHands['detectForVideo']>>, pres: Awaited<ReturnType<MPPose['detectForVideo']>>): Float32Array {
  const data = new Float32Array(D);
  if (pres?.landmarks?.[0]) data.set(pres.landmarks[0].flatMap(p => [p.x, p.y, p.z ?? 0]), 0);
  if (hres?.landmarks?.length && hres.handedness?.length) {
    for (let j = 0; j < hres.landmarks.length; j++) {
      const handed = hres.handedness[j]?.[0]?.categoryName?.toLowerCase();
      if (!handed) continue;
      const flat = hres.landmarks[j].flatMap(p => [p.x, p.y, p.z ?? 0]);
      if (handed === "left") data.set(flat, 99);
      else if (handed === "right") data.set(flat, 99 + 63);
    }
  }
  return data;
}

ctx.onmessage = async (ev: MessageEvent<WorkerMsg>) => {
  const { type, payload } = ev.data;
  try {
    if (type === "init") {
      T = (payload as { T: number }).T || 48;
      D = (payload as { D: number }).D || 225;
      isCollectionMode = (payload as { collectionMode?: boolean }).collectionMode || false;
      buffer = [];
      await ensureMediapipe();
      if (!isCollectionMode) {
        initInferWorker();
      } else {
        ctx.postMessage({ type: "ready" });
      }
      return;
    }

    if (type === "frame") {
      if (!hands || !pose) return;
      const { video, ts } = payload as { video: ImageBitmap; ts: number };
      const [hres, pres] = await Promise.all([hands.detectForVideo(video, ts), pose.detectForVideo(video, ts)]);
      const rawVec = packFrame(hres, pres);
      const normalizedVec = normalizeKeypoints(rawVec);
      buffer.push(normalizedVec);
      if (buffer.length > T) buffer.shift();
      video.close();
      
      if (buffer.length === T && !isCollectionMode && inferWorker) {
        const flat = new Float32Array(T * D);
        for (let t = 0; t < T; t++) flat.set(buffer[t], t * D);
        const input: InferenceInput = { data: flat, T, D };
        inferWorker.postMessage({ type: "infer", payload: input });
      }
      return;
    }

    if (type === "capture_window") {
      if (isCollectionMode && buffer.length === T) {
        const sample: WindowSample = { frames: [...buffer] };
        ctx.postMessage({ type: "window_for_collection", payload: sample });
      }
      return;
    }
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    ctx.postMessage({ type: "error", error: errorMessage });
  }
};