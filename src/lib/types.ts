export type KeypointsFrame = {
  ts: number;                 // ms
  pose: number[];             // 33*3 = 99
  leftHand: number[];         // 21*3 = 63
  rightHand: number[];        // 21*3 = 63
};

export type WindowSample = { frames: KeypointsFrame[] };

export type InferenceInput = {
  data: Float32Array;         // [T*D]
  T: number;
  D: number;
};

export type TopK = { label: string; score: number };
export type InferenceOutput = {
  topk: TopK[];
  accepted: boolean;
  latencyMs: number;
};

export type WorkerMsg<T = unknown> = { type: string; payload?: T; error?: string };
