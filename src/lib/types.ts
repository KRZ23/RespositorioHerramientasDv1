// src/lib/types.ts

// Un KeypointsFrame ya no es un objeto complejo, es simplemente un vector de puntos clave.
export type KeypointsFrame = Float32Array | number[];

// Una muestra de ventana contiene una secuencia de estos vectores.
export type WindowSample = {
  frames: KeypointsFrame[];
};

// ... (El resto de los tipos pueden permanecer igual si no están relacionados)

export type WorkerMsg<T = unknown> = {
  type: "init" | "ready" | "error" | "frame" | "infer" | "result" | "reset" | "reset-ok" | "window" | "capture_window" | "window_for_collection";
  payload?: T;
  error?: string;
};

export type InferenceInput = {
  data: Float32Array;
  T: number;
  D: number;
};

export type TopK = {
  label: string;
  score: number;
};

export type InferenceOutput = {
  topk: TopK[];
  accepted: boolean;
  latencyMs: number;
};