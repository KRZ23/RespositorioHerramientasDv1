// src/app/coleccion/page.tsx

"use client";

import { useEffect, useRef, useState } from "react";
import Container from "@/components/ui/container";
import { Button } from "@/components/ui/button";
import type { WorkerMsg, WindowSample, KeypointsFrame } from "@/lib/types";

const VOCABULARIO_MVP = ["HOLA", "ADIOS", "GRACIAS", "PORFAVOR", "PERU"];

export default function ColeccionPage() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const loopRef = useRef<number | null>(null);
  const keypointsWRef = useRef<Worker | null>(null);

  const [status, setStatus] = useState("Inicializando…");
  const [running, setRunning] = useState(false);
  const [currentSign, setCurrentSign] = useState(VOCABULARIO_MVP[0]);
  const [sampleCount, setSampleCount] = useState(0);

  useEffect(() => {
    const kw = new Worker(new URL("@/workers/keypoints.worker.ts", import.meta.url), { type: "module" });
    keypointsWRef.current = kw;

    kw.onmessage = (e: MessageEvent<WorkerMsg>) => {
      const { type, payload } = e.data;
      if (type === "ready") setStatus("Listo para iniciar");
      if (type === "error") setStatus(`Error: ${e.data.error}`);
      
      if (type === "window_for_collection") {
        downloadSample(payload as WindowSample);
        setSampleCount(prev => prev + 1);
        setStatus(`Muestra #${sampleCount + 1} de "${currentSign}" guardada.`);
      }
    };

    return () => {
      if (loopRef.current) cancelAnimationFrame(loopRef.current);
      kw.terminate();
    };
  }, [currentSign, sampleCount]);

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setRunning(true);
        keypointsWRef.current?.postMessage({ type: "init", payload: { T: 48, D: 225, collectionMode: true } });
        loop();
      }
    } catch (error) {
      console.error("Error al acceder a la cámara:", error);
      setStatus("Error de cámara");
    }
  }

  function loop() {
    if (!videoRef.current || !keypointsWRef.current) return;
    const v = videoRef.current;
    if (v.readyState < 2) {
      loopRef.current = requestAnimationFrame(loop);
      return;
    }
    createImageBitmap(v).then(bitmap => {
      keypointsWRef.current?.postMessage({ type: "frame", payload: { video: bitmap, ts: performance.now() } }, [bitmap]);
    }).catch(console.error);
    loopRef.current = requestAnimationFrame(loop);
  }
  
  function captureSample() {
    if (!keypointsWRef.current) return;
    setStatus("Capturando...");
    keypointsWRef.current.postMessage({ type: "capture_window" });
  }

  function downloadSample(sample: WindowSample) {
    const filename = `${currentSign}_${Date.now()}.json`;
    // El error ha desaparecido. 'frame' es de tipo KeypointsFrame (Float32Array | number[]),
    // que es compatible con Array.from.
    const serializableFrames = sample.frames.map(frame => Array.from(frame));
    const dataToSave = { label: currentSign, frames: serializableFrames };
    
    const blob = new Blob([JSON.stringify(dataToSave, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <main>
      <Container className="py-8 md:py-12">
        <h1 className="text-3xl font-bold tracking-tight">Herramienta de Recolección de Datos</h1>
        <p className="mt-2 text-slate-600">Utiliza esta interfaz para generar el dataset de entrenamiento.</p>
        <div className="mt-6 grid gap-4 md:grid-cols-[1.5fr_1fr]">
          <div className="rounded-2xl border bg-white p-3 shadow-sm">
            <div className="aspect-video overflow-hidden rounded-xl bg-slate-100">
              <video ref={videoRef} playsInline muted className="h-full w-full object-cover" />
            </div>
            <div className="mt-3 flex items-center gap-3">
              <Button onClick={startCamera} disabled={running}>Activar cámara</Button>
              <span className="text-sm text-slate-500">{status}</span>
            </div>
          </div>
          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold">Panel de Captura</h2>
            <div className="mt-3 space-y-4">
              <div>
                <label htmlFor="sign-select" className="block text-sm font-medium text-slate-700">Seña a grabar:</label>
                <select
                  id="sign-select"
                  className="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                  value={currentSign}
                  onChange={(e) => {
                    setCurrentSign(e.target.value);
                    setSampleCount(0);
                  }}
                >
                  {VOCABULARIO_MVP.map(sign => <option key={sign} value={sign}>{sign}</option>)}
                </select>
              </div>
              <Button onClick={captureSample} disabled={!running} className="w-full">
                {`Grabar Muestra de "${currentSign}"`}
              </Button>
              <p className="text-sm text-slate-500">Muestras guardadas para esta seña: {sampleCount}</p>
            </div>
          </div>
        </div>
      </Container>
    </main>
  );
}