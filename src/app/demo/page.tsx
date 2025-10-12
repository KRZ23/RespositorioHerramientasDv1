"use client";

import { useEffect, useRef, useState } from "react";
import Container from "@/components/ui/container";
import { Button } from "@/components/ui/button";
import type { WorkerMsg, InferenceInput, InferenceOutput } from "@/lib/types";

type MPHands = import("@mediapipe/tasks-vision").HandLandmarker;
type MPPose = import("@mediapipe/tasks-vision").PoseLandmarker;

export default function DemoPage() {
  const videoRef = useRef<HTMLVideoElement>(null);

  const [mpReady, setMpReady] = useState(false);
  const [iReady, setIReady] = useState(false);
  const [result, setResult] = useState<InferenceOutput | null>(null);
  const [running, setRunning] = useState(false);

  const inferWRef = useRef<Worker | null>(null);
  const handsRef = useRef<MPHands | null>(null);
  const poseRef = useRef<MPPose | null>(null);

  const T = 48;
  const D = 99 + 63 + 63; // pose + left + right
  const bufferRef = useRef<Float32Array[]>([]);

  // -------- MediaPipe en el hilo principal --------
  useEffect(() => {
    let cancelled = false;

    async function initMP() {
      const vision = await import("@mediapipe/tasks-vision");
      const { FilesetResolver, HandLandmarker, PoseLandmarker } = vision;

      const fileset = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm"
      );

      handsRef.current = await HandLandmarker.createFromOptions(fileset, {
        baseOptions: {
          modelAssetPath:
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        },
        numHands: 2,
        runningMode: "VIDEO",
      });

      poseRef.current = await PoseLandmarker.createFromOptions(fileset, {
        baseOptions: {
          modelAssetPath:
            "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
        },
        runningMode: "VIDEO",
      });

      if (!cancelled) setMpReady(true);
    }

    // worker de inferencia (heurístico)
    const iw = new Worker(new URL("@/workers/infer.worker.ts", import.meta.url), { type: "module" });
    inferWRef.current = iw;
    iw.onmessage = (e: MessageEvent<WorkerMsg>) => {
      if (e.data.type === "ready") setIReady(true);
      if (e.data.type === "result") setResult(e.data.payload as InferenceOutput);
      if (e.data.type === "error") console.error("Infer worker error:", e.data.error);
    };
    iw.postMessage({ type: "init", payload: { threshold: 0.25 } } as WorkerMsg);

    initMP();
    return () => {
      cancelled = true;
      iw.terminate();
    };
  }, []);

  async function startCamera() {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false,
    });
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
      setRunning(true);
      loop();
    }
  }

  // Convierte landmarks de MP a vector [pose(99), left(63), right(63)]
  function packFrame(hres: ReturnType<MPHands['detectForVideo']>, pres: ReturnType<MPPose['detectForVideo']>): Float32Array {
    const left = new Array(63).fill(0);
    const right = new Array(63).fill(0);
    const pose = new Array(99).fill(0);

    // manos
    if (hres?.landmarks?.length && hres.handedness?.length) {
      for (let j = 0; j < hres.landmarks.length; j++) {
        const lm = hres.landmarks[j];
        const handed = hres.handedness[j]?.[0]?.categoryName?.toLowerCase();
        const flat = lm.flatMap((p) => [p.x, p.y, p.z ?? 0]);
        if (handed === "left") for (let i = 0; i < 63; i++) left[i] = flat[i] ?? 0;
        else for (let i = 0; i < 63; i++) right[i] = flat[i] ?? 0;
      }
    }

    // pose (primer cuerpo detectado)
    if (pres?.landmarks?.[0]) {
      const lm = pres.landmarks[0];
      const flat = lm.flatMap((p) => [p.x, p.y, p.z ?? 0]);
      for (let i = 0; i < 99; i++) pose[i] = flat[i] ?? 0;
    }

    return new Float32Array([...pose, ...left, ...right]);
  }

  function loop() {
    const v = videoRef.current;
    const hands = handsRef.current;
    const pose = poseRef.current;
    if (!v || !hands || !pose) return;

    const tick = async () => {
      if (!running) return;

      const ts = performance.now();
      const hres = await hands.detectForVideo(v, ts);
      const pres = await pose.detectForVideo(v, ts);

      const vec = packFrame(hres, pres); // [D]
      // ventana T
      const buf = bufferRef.current;
      buf.push(vec);
      if (buf.length > T) buf.shift();

      if (buf.length === T) {
        // aplanar [T,D]
        const flat = new Float32Array(T * D);
        for (let t = 0; t < T; t++) flat.set(buf[t], t * D);
        const input: InferenceInput = { data: flat, T, D };
        inferWRef.current?.postMessage({ type: "infer", payload: input } as WorkerMsg);
      }

      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  return (
    <main>
      <Container className="py-8 md:py-12">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Demo en vivo (heurístico)</h1>
        <p className="mt-2 text-slate-600">
          Señales soportadas (demo): <b>HOLA</b> (oleada), <b>SÍ</b> (pulgar arriba),
          <b> NO</b> (índice oscilando), <b>GRACIAS (demo)</b> (mano sale de la boca).
        </p>

        <div className="mt-6 grid gap-4 md:grid-cols-[1.5fr_1fr]">
          <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
            <div className="aspect-video overflow-hidden rounded-xl bg-slate-100 relative">
              <video ref={videoRef} playsInline muted className="h-full w-full object-cover" />
            </div>
            <div className="mt-3 flex items-center gap-3">
              <Button onClick={startCamera} disabled={!mpReady || !iReady}>
                {mpReady && iReady ? "Activar cámara" : "Inicializando…"}
              </Button>
              <span className="text-sm text-slate-500">
                {mpReady ? "Detección OK • " : "Detección … • "}
                {iReady ? "Heurístico OK" : "Heurístico …"}
              </span>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold">Resultado</h2>
            <div className="mt-3 grid gap-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate-600">Top-1:</span>
                <span className="font-semibold">
                  {result ? `${result.topk[0]?.label ?? "—"} (${result.topk[0]?.score ?? 0})` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-600">Top-k:</span>
                <span className="font-mono">
                  {result ? result.topk.map(t => `${t.label}:${t.score}`).join("  ") : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-600">Latencia (ms):</span>
                <span className="font-semibold">{result ? Math.round(result.latencyMs) : "—"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-600">Aceptado:</span>
                <span className={`font-semibold ${result?.accepted ? "text-green-600" : "text-slate-500"}`}>
                  {result?.accepted ? "Sí" : "No"}
                </span>
              </div>
            </div>
            <p className="mt-4 text-xs text-slate-500">
              Umbral heurístico actual: 0.25. Ajusta si es muy estricto o laxo.
            </p>
          </div>
        </div>
      </Container>
    </main>
  );
}
