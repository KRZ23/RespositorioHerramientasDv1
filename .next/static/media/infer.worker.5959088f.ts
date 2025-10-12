/// <reference lib="webworker" />
import type { WorkerMsg, InferenceInput, InferenceOutput, TopK } from "@/lib/types";
const ctx: DedicatedWorkerGlobalScope = self as DedicatedWorkerGlobalScope;

// Si en el futuro pasas a ONNX, importaremos 'onnxruntime-web' aquí.
let THRESHOLD = 0.25; // umbral para aceptar en heurístico

// índices de ayuda (vector [pose(99), left(63), right(63)])
// OJO: este worker asume el orden [pose, left, right] del keypoints.worker (ajusta si cambias)
const OFFSET_POSE = 0;
const OFFSET_RIGHT = 99 + 63;

const POSE = {
  MOUTH_RIGHT: 87, // aproximado
  MOUTH_LEFT: 84,
  SHOULDER_R: 33,
  SHOULDER_L: 36,
};
const HAND = {
  WRIST: 0,
  THUMB_TIP: 4 * 3,
  INDEX_TIP: 8 * 3,
  MIDDLE_TIP: 12 * 3,
};

function getPoint(v: Float32Array, base: number, i: number) {
  const idx = base + i;
  return { x: v[idx], y: v[idx + 1], z: v[idx + 2] };
}

function heuristicInfer(input: InferenceInput): InferenceOutput {
  const { data, T, D } = input;
  const out: InferenceOutput = { topk: [], accepted: false, latencyMs: 0 };

  const W = Math.min(T, 24);
  const baseLast = (T - 1) * D;

  const shR = { x: data[baseLast + (OFFSET_POSE + POSE.SHOULDER_R * 3 + 0)],
                y: data[baseLast + (OFFSET_POSE + POSE.SHOULDER_R * 3 + 1)] };
  const shL = { x: data[baseLast + (OFFSET_POSE + POSE.SHOULDER_L * 3 + 0)],
                y: data[baseLast + (OFFSET_POSE + POSE.SHOULDER_L * 3 + 1)] };
  const shoulderWidth = Math.hypot(shR.x - shL.x, shR.y - shL.y) || 1;

  let waveEnergy = 0, indexOsc = 0, thumbUp = 0, thanksScore = 0;
  let prevWristX: number | null = null;
  let prevIndexX: number | null = null;
  let prevMouthDist: number | null = null;

  for (let t = T - W; t < T; t++) {
    const base = t * D;

    // mano derecha = usamos RIGHT
    const rWrist = getPoint(data, base + OFFSET_RIGHT, HAND.WRIST * 3);
    const rIndex = getPoint(data, base + OFFSET_RIGHT, HAND.INDEX_TIP);
    const rThumb = getPoint(data, base + OFFSET_RIGHT, HAND.THUMB_TIP);
    const rMiddle = getPoint(data, base + OFFSET_RIGHT, HAND.MIDDLE_TIP);

    const mouthR = getPoint(data, base + OFFSET_POSE, POSE.MOUTH_RIGHT * 3);
    const mouthL = getPoint(data, base + OFFSET_POSE, POSE.MOUTH_LEFT * 3);
    const mouth = { x: (mouthR.x + mouthL.x) / 2, y: (mouthR.y + mouthL.y) / 2 };

    // HOLA: oleada (oscilación X de muñeca)
    if (prevWristX !== null) waveEnergy += Math.abs(rWrist.x - prevWristX);
    prevWristX = rWrist.x;

    // NO: oscilación lateral del índice
    if (prevIndexX !== null) indexOsc += Math.abs(rIndex.x - prevIndexX);
    prevIndexX = rIndex.x;

    // SI: pulgar arriba (pulgar y < índice/medio y)
    const thumbAbove = (rThumb.y + 0.02) < Math.min(rIndex.y, rMiddle.y);
    thumbUp += thumbAbove ? 1 : 0;

    // GRACIAS (demo): mano cerca boca → alejamiento
    const handMouthDist = Math.hypot(rWrist.x - mouth.x, rWrist.y - mouth.y) / shoulderWidth;
    if (prevMouthDist !== null && prevMouthDist < 0.2 && handMouthDist > prevMouthDist + 0.05) {
      thanksScore += 1;
    }
    prevMouthDist = handMouthDist;
  }

  const waveNorm = waveEnergy / W / shoulderWidth;
  const indexNorm = indexOsc / W / shoulderWidth;
  const thumbNorm = thumbUp / W;
  const thanksNorm = thanksScore / W;

  const scores: TopK[] = [
    { label: "HOLA", score: Number(waveNorm.toFixed(3)) },
    { label: "SI", score: Number(thumbNorm.toFixed(3)) },
    { label: "NO", score: Number((indexNorm * 0.8).toFixed(3)) },
    { label: "GRACIAS(DEMO)", score: Number((thanksNorm * 1.5).toFixed(3)) },
  ].sort((a, b) => b.score - a.score);

  const accepted = scores[0].score >= THRESHOLD;
  out.topk = scores.slice(0, 3);
  out.accepted = accepted;
  return out;
}

ctx.onmessage = async (ev: MessageEvent<WorkerMsg>) => {
  const { type, payload } = ev.data;

  try {
    if (type === "init") {
      // Para heurístico no necesitamos cargar nada.
      if (payload && typeof payload === "object" && "threshold" in payload && typeof payload.threshold === "number") {
        THRESHOLD = payload.threshold;
      }
      ctx.postMessage({ type: "ready" } as WorkerMsg);
      return;
    }

    if (type === "infer") {
      const t0 = performance.now();
      const res = heuristicInfer(payload as InferenceInput);
      res.latencyMs = performance.now() - t0;
      ctx.postMessage({ type: "result", payload: res } as WorkerMsg<InferenceOutput>);
      return;
    }
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    ctx.postMessage({ type: "error", error: errorMessage } as WorkerMsg);
  }
};