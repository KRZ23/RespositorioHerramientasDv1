"use client";

import { useEffect, useRef, useState } from "react";
import Container from "@/components/ui/container";
import { Button } from "@/components/ui/button";
import type { WorkerMsg, InferenceOutput } from "@/lib/types";

export default function DemoPage() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const loopRef = useRef<number | null>(null);
  const keypointsWRef = useRef<Worker | null>(null);
  const frameCounterRef = useRef<number>(0); // <-- NUEVO: Contador de fotogramas

  const [status, setStatus] = useState("Inicializando…");
  const [result, setResult] = useState<InferenceOutput | null>(null);
  const [running, setRunning] = useState(false);

  // -------- INICIALIZACIÓN DE WORKERS --------
  useEffect(() => {
    const kw = new Worker(new URL("@/workers/keypoints.worker.ts", import.meta.url), { type: "module" });
    keypointsWRef.current = kw;

    kw.onmessage = (e: MessageEvent<WorkerMsg>) => {
      const { type, payload } = e.data;
      
      if (type === "ready") {
        setStatus("Listo para iniciar");
      }
      
      if (type === "result") {
        setResult(payload as InferenceOutput);
      }
      
      if (type === "error") {
        console.error("Keypoints worker error:", e.data.error);
        setStatus(`Error: ${e.data.error}`);
      }
    };

    kw.postMessage({ type: "init", payload: { T: 48, D: 225 } } as WorkerMsg);

    return () => {
      if (loopRef.current) cancelAnimationFrame(loopRef.current);
      kw.terminate();
    };
  }, []);

  // -------- CONTROL DE LA CÁMARA Y BUCLE DE ENVÍO DE FRAMES --------
  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setRunning(true);
        frameCounterRef.current = 0; // Reiniciar contador al iniciar
        loop();
      }
    } catch (error) {
      console.error("Error al acceder a la cámara:", error);
      setStatus("Error de cámara");
    }
  }

  function stopCamera() {
    if (loopRef.current) cancelAnimationFrame(loopRef.current);
    if (videoRef.current?.srcObject) {
      (videoRef.current.srcObject as MediaStream).getTracks().forEach(track => track.stop());
    }
    setRunning(false);
  }

  // Bucle principal que envía frames al worker de keypoints
  function loop() {
    if (!videoRef.current || !keypointsWRef.current) return;

    const v = videoRef.current;
    if (v.readyState < 2) {
      loopRef.current = requestAnimationFrame(loop);
      return;
    }
    
    createImageBitmap(v).then(bitmap => {
      // Usamos el contador incremental para garantizar timestamps únicos y crecientes
      const ts = frameCounterRef.current++; // <-- MODIFICADO
      keypointsWRef.current?.postMessage({ type: "frame", payload: { video: bitmap, ts } }, [bitmap]);
    }).catch(console.error);
    
    loopRef.current = requestAnimationFrame(loop);
  }

  return (
    <main>
      <Container className="py-8 md:py-12">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Demo en vivo (Arquitectura Refactorizada)</h1>
        <p className="mt-2 text-slate-600">
          El procesamiento de MediaPipe y la inferencia ONNX ocurren en segundo plano.
        </p>

        <div className="mt-6 grid gap-4 md:grid-cols-[1.5fr_1fr]">
          <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
            <div className="aspect-video overflow-hidden rounded-xl bg-slate-100 relative">
              <video ref={videoRef} playsInline muted className="h-full w-full object-cover" />
            </div>
            <div className="mt-3 flex items-center gap-3">
              <Button onClick={running ? stopCamera : startCamera} disabled={status.startsWith("Inicializando")}>
                {running ? "Detener cámara" : "Activar cámara"}
              </Button>
              <span className="text-sm text-slate-500">{status}</span>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold">Resultado de Inferencia</h2>
            <div className="mt-3 grid gap-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate-600">Top-1:</span>
                <span className="font-semibold">
                  {result ? `${result.topk[0]?.label ?? "—"} (${result.topk[0]?.score.toFixed(3) ?? 0})` : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-600">Top-k:</span>
                <span className="font-mono text-xs">
                  {result ? result.topk.map(t => `${t.label}:${t.score.toFixed(2)}`).join(" ") : "—"}
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
              *Los resultados son simulados hasta que se entrene un modelo ONNX real.
            </p>
          </div>
        </div>
      </Container>
    </main>
  );
}