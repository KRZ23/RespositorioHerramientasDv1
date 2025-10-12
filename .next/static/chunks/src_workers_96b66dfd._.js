(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/src/workers/infer.worker.ts (static in ecmascript)", ((__turbopack_context__) => {

__turbopack_context__.v("/_next/static/media/infer.worker.53996008.ts");}),
"[project]/src/workers/infer.worker.ts [app-client] (ecmascript, worker loader)", ((__turbopack_context__) => {

__turbopack_context__.v(__turbopack_context__.b([
  "static/chunks/node_modules_3b9bb2ae._.js",
  "static/chunks/src_workers_infer_worker_ts_5d18340b._.js",
  "static/chunks/src_workers_infer_worker_ts_b3f8fcd6._.js",
  "static/chunks/turbopack-src_workers_infer_worker_ts_27ed157d._.js"
]));
}),
"[project]/src/workers/keypoints.worker.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// src/workers/keypoints.worker.ts
/// <reference lib="webworker" />
__turbopack_context__.s([]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$mediapipe$2f$tasks$2d$vision$2f$vision_bundle$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@mediapipe/tasks-vision/vision_bundle.mjs [app-client] (ecmascript)");
const __TURBOPACK__import$2e$meta__ = {
    get url () {
        return `file://${__turbopack_context__.P("src/workers/keypoints.worker.ts")}`;
    }
};
const ctx = self;
;
let hands = null;
let pose = null;
let inferWorker = null;
let buffer = [];
let T = 48;
let D = 225;
let isCollectionMode = false;
const POSE_L_SHOULDER_X = 11 * 3;
const POSE_L_SHOULDER_Y = 11 * 3 + 1;
const POSE_R_SHOULDER_X = 12 * 3;
const POSE_R_SHOULDER_Y = 12 * 3 + 1;
function normalizeKeypoints(data) {
    const shoulderL = {
        x: data[POSE_L_SHOULDER_X],
        y: data[POSE_L_SHOULDER_Y]
    };
    const shoulderR = {
        x: data[POSE_R_SHOULDER_X],
        y: data[POSE_R_SHOULDER_Y]
    };
    if (shoulderL.x === 0 && shoulderL.y === 0 && shoulderR.x === 0 && shoulderR.y === 0) return data;
    const origin = {
        x: (shoulderL.x + shoulderR.x) / 2,
        y: (shoulderL.y + shoulderR.y) / 2
    };
    const scale = Math.hypot(shoulderR.x - shoulderL.x, shoulderR.y - shoulderR.y) || 1;
    const normalizedData = new Float32Array(data.length);
    for(let i = 0; i < data.length; i += 3){
        if (data[i] === 0 && data[i + 1] === 0 && data[i + 2] === 0) continue;
        normalizedData[i] = (data[i] - origin.x) / scale;
        normalizedData[i + 1] = (data[i + 1] - origin.y) / scale;
        normalizedData[i + 2] = data[i + 2] / scale;
    }
    return normalizedData;
}
async function ensureMediapipe() {
    if (hands && pose) return;
    const fileset = await __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$mediapipe$2f$tasks$2d$vision$2f$vision_bundle$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["FilesetResolver"].forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm");
    hands = await __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$mediapipe$2f$tasks$2d$vision$2f$vision_bundle$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["HandLandmarker"].createFromOptions(fileset, {
        baseOptions: {
            modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        },
        numHands: 2,
        runningMode: "VIDEO"
    });
    pose = await __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$mediapipe$2f$tasks$2d$vision$2f$vision_bundle$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["PoseLandmarker"].createFromOptions(fileset, {
        baseOptions: {
            modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
        },
        runningMode: "VIDEO"
    });
}
function initInferWorker() {
    if (inferWorker) return;
    inferWorker = new Worker(__turbopack_context__.r("[project]/src/workers/infer.worker.ts [app-client] (ecmascript, worker loader)"), {
        ...{
            type: "module"
        },
        type: undefined
    });
    inferWorker.onmessage = (e)=>ctx.postMessage(e.data);
    inferWorker.postMessage({
        type: 'init',
        payload: {
            threshold: 0.25
        }
    });
}
function packFrame(hres, pres) {
    var _pres_landmarks, _hres_landmarks, _hres_handedness;
    const data = new Float32Array(D);
    if (pres === null || pres === void 0 ? void 0 : (_pres_landmarks = pres.landmarks) === null || _pres_landmarks === void 0 ? void 0 : _pres_landmarks[0]) data.set(pres.landmarks[0].flatMap((p)=>{
        var _p_z;
        return [
            p.x,
            p.y,
            (_p_z = p.z) !== null && _p_z !== void 0 ? _p_z : 0
        ];
    }), 0);
    if ((hres === null || hres === void 0 ? void 0 : (_hres_landmarks = hres.landmarks) === null || _hres_landmarks === void 0 ? void 0 : _hres_landmarks.length) && ((_hres_handedness = hres.handedness) === null || _hres_handedness === void 0 ? void 0 : _hres_handedness.length)) {
        for(let j = 0; j < hres.landmarks.length; j++){
            var _hres_handedness_j__categoryName, _hres_handedness_j_, _hres_handedness_j;
            const handed = (_hres_handedness_j = hres.handedness[j]) === null || _hres_handedness_j === void 0 ? void 0 : (_hres_handedness_j_ = _hres_handedness_j[0]) === null || _hres_handedness_j_ === void 0 ? void 0 : (_hres_handedness_j__categoryName = _hres_handedness_j_.categoryName) === null || _hres_handedness_j__categoryName === void 0 ? void 0 : _hres_handedness_j__categoryName.toLowerCase();
            if (!handed) continue;
            const flat = hres.landmarks[j].flatMap((p)=>{
                var _p_z;
                return [
                    p.x,
                    p.y,
                    (_p_z = p.z) !== null && _p_z !== void 0 ? _p_z : 0
                ];
            });
            if (handed === "left") data.set(flat, 99);
            else if (handed === "right") data.set(flat, 99 + 63);
        }
    }
    return data;
}
ctx.onmessage = async (ev)=>{
    const { type, payload } = ev.data;
    try {
        if (type === "init") {
            T = payload.T || 48;
            D = payload.D || 225;
            isCollectionMode = payload.collectionMode || false;
            buffer = [];
            await ensureMediapipe();
            if (!isCollectionMode) {
                initInferWorker();
            } else {
                ctx.postMessage({
                    type: "ready"
                });
            }
            return;
        }
        if (type === "frame") {
            if (!hands || !pose) return;
            const { video, ts } = payload;
            const [hres, pres] = await Promise.all([
                hands.detectForVideo(video, ts),
                pose.detectForVideo(video, ts)
            ]);
            const rawVec = packFrame(hres, pres);
            const normalizedVec = normalizeKeypoints(rawVec);
            buffer.push(normalizedVec);
            if (buffer.length > T) buffer.shift();
            video.close();
            if (buffer.length === T && !isCollectionMode && inferWorker) {
                const flat = new Float32Array(T * D);
                for(let t = 0; t < T; t++)flat.set(buffer[t], t * D);
                const input = {
                    data: flat,
                    T,
                    D
                };
                inferWorker.postMessage({
                    type: "infer",
                    payload: input
                });
            }
            return;
        }
        if (type === "capture_window") {
            if (isCollectionMode && buffer.length === T) {
                // Ahora el tipo de `buffer` (Float32Array[]) es compatible con `KeypointsFrame[]`
                const sample = {
                    frames: [
                        ...buffer
                    ]
                };
                ctx.postMessage({
                    type: "window_for_collection",
                    payload: sample
                });
            }
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

//# sourceMappingURL=src_workers_96b66dfd._.js.map