(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/src/workers/infer.worker.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/// <reference lib="webworker" />
__turbopack_context__.s([]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$onnxruntime$2d$web$2f$dist$2f$ort$2e$bundle$2e$min$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/onnxruntime-web/dist/ort.bundle.min.mjs [app-client] (ecmascript)");
;
const ctx = self;
let session = null;
let THRESHOLD = 0.25;
const LABELS = [
    "HOLA",
    "GRACIAS",
    "ADIOS",
    "SI",
    "NO",
    "PORFAVOR"
]; // Ejemplo
// ---- Carga del Modelo y Lógica de Inferencia ----
async function initONNX() {
    try {
        // Asegúrate de que el modelo está en la carpeta /public
        session = await __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$onnxruntime$2d$web$2f$dist$2f$ort$2e$bundle$2e$min$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InferenceSession"].create('./lsp_model.onnx');
        console.log("ONNX session created successfully.");
    } catch (error) {
        console.error("Failed to create ONNX session:", error);
        throw new Error("Could not load the ONNX model.");
    }
}
async function runONNXInference(input) {
    if (!session) throw new Error("ONNX session not initialized.");
    const { data, T, D } = input;
    const tensor = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$onnxruntime$2d$web$2f$dist$2f$ort$2e$bundle$2e$min$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Tensor"]('float32', data, [
        1,
        T,
        D
    ]);
    const feeds = {
        "input_sequence": tensor
    }; // El nombre "input_sequence" debe coincidir
    const results = await session.run(feeds);
    // El nombre "output_label" debe coincidir con el de tu modelo
    const outputTensor = results.output_label;
    // Procesa el tensor de salida para obtener scores
    const scores = Array.from(outputTensor.data);
    const topk = scores.map((score, i)=>({
            label: LABELS[i] || "class_".concat(i),
            score
        })).sort((a, b)=>b.score - a.score).slice(0, 3);
    const accepted = topk[0].score >= THRESHOLD;
    return {
        topk,
        accepted,
        latencyMs: 0
    }; // Latency se calculará fuera
}
// Inferencia SIMULADA para desarrollo sin un modelo real
function runMockInference(input) {
    const { T } = input;
    // Simulación: elige una etiqueta aleatoria y asígnale un score alto
    const randomIndex = Math.floor(Math.random() * LABELS.length);
    const topk = LABELS.map((label, i)=>({
            label,
            score: i === randomIndex ? 0.8 + Math.random() * 0.2 : Math.random() * 0.1
        })).sort((a, b)=>b.score - a.score).slice(0, 3);
    const accepted = topk[0].score >= THRESHOLD;
    return {
        topk,
        accepted,
        latencyMs: Math.random() * 20 + 5
    }; // Latencia simulada
}
// ---- Manejador de Mensajes del Worker ----
ctx.onmessage = async (ev)=>{
    const { type, payload } = ev.data;
    try {
        if (type === "init") {
            var _this;
            THRESHOLD = ((_this = payload) === null || _this === void 0 ? void 0 : _this.threshold) || 0.25;
            // Descomenta la siguiente línea para usar tu modelo ONNX real
            // await initONNX(); 
            ctx.postMessage({
                type: "ready"
            });
            return;
        }
        if (type === "infer") {
            const t0 = performance.now();
            // CAMBIA a runONNXInference cuando tengas tu modelo
            const res = runMockInference(payload);
            res.latencyMs = performance.now() - t0;
            ctx.postMessage({
                type: "result",
                payload: res
            });
            return;
        }
    } catch (err) {
        const errorMessage = err instanceof Error ? err.message : String(err);
        ctx.postMessage({
            type: "error",
            error: errorMessage
        });
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=src_workers_infer_worker_ts_5d18340b._.js.map