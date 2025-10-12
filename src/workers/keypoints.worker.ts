/// <reference lib="webworker" />
import type { WorkerMsg, KeypointsFrame, WindowSample } from "@/lib/types";
const ctx: DedicatedWorkerGlobalScope = self as DedicatedWorkerGlobalScope;

type MPHands = import("@mediapipe/tasks-vision").HandLandmarker;
type MPPose = import("@mediapipe/tasks-vision").PoseLandmarker;
let hands: MPHands | null = null;
let pose: MPPose | null = null;

let buffer: KeypointsFrame[] = [];
let T = 48; // frames por ventana

function normalizeFrame(f: KeypointsFrame): KeypointsFrame {
  // TODO: normalizar por ancho de hombros/centrado (opcional en el heurístico)
  return f;
}

async function ensureMediapipe() {
  if (hands && pose) return;
  const vision = await import("@mediapipe/tasks-vision");
  const { FilesetResolver, HandLandmarker, PoseLandmarker } = vision;

  const fileset = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm"
  );

  hands = await HandLandmarker.createFromOptions(fileset, {
    baseOptions: {
      modelAssetPath:
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
    },
    numHands: 2,
    runningMode: "VIDEO",
  });

  pose = await PoseLandmarker.createFromOptions(fileset, {
    baseOptions: {
      modelAssetPath:
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
    },
    runningMode: "VIDEO",
  });
}

ctx.onmessage = async (ev: MessageEvent<WorkerMsg>) => {
  const { type, payload } = ev.data;

  try {
    if (type === "init") {
      if (payload && typeof payload === "object" && "T" in payload && typeof payload.T === "number") {
        T = payload.T;
      }
      buffer = [];
      await ensureMediapipe();
      ctx.postMessage({ type: "ready" } as WorkerMsg);
      return;
    }

    if (type === "frame") {
      const { video, ts } = payload as { video: ImageBitmap; ts: number };

      const hres = await hands!.detectForVideo(video, ts);
      const pres = await pose!.detectForVideo(video, ts);

      const leftHand: number[] = new Array(63).fill(0);
      const rightHand: number[] = new Array(63).fill(0);
      const poseArr: number[] = new Array(99).fill(0);

      if (hres?.landmarks?.length) {
        for (let hi = 0; hi < Math.min(2, hres.landmarks.length); hi++) {
          const lm = hres.landmarks[hi];
          const flat = lm.flatMap((p) => [p.x, p.y, p.z ?? 0]);
          if (hi === 0) for (let i = 0; i < 63; i++) leftHand[i] = flat[i] ?? 0;
          if (hi === 1) for (let i = 0; i < 63; i++) rightHand[i] = flat[i] ?? 0;
        }
      }

      if (pres?.landmarks?.[0]) {
        const lm = pres.landmarks[0];
        const flat = lm.flatMap((p) => [p.x, p.y, p.z ?? 0]);
        for (let i = 0; i < 99; i++) poseArr[i] = flat[i] ?? 0;
      }

      const frame: KeypointsFrame = normalizeFrame({ ts, pose: poseArr, leftHand, rightHand });
      buffer.push(frame);
      if (buffer.length > T) buffer.shift();

      if (buffer.length === T) {
        const sample: WindowSample = { frames: buffer };
        ctx.postMessage({ type: "window", payload: sample } as WorkerMsg<WindowSample>);
      }

      if (video && typeof video === "object" && "close" in video && typeof video.close === "function") {
        video.close();
      }
      return;
    }

    if (type === "reset") {
      buffer = [];
      ctx.postMessage({ type: "reset-ok" } as WorkerMsg);
      return;
    }
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    ctx.postMessage({ type: "error", error: errorMessage } as WorkerMsg);
  }
};
