import { useState, useEffect } from "react";
import { analyzePersona } from "./types/persona";
import type { PersonaData } from "./types/persona";
import { INITIAL_PERSONA } from "./data/seed";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { Camera, AlertTriangle, CheckCircle, BrainCircuit } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function App() {
  const [data, setData] = useState<PersonaData>(INITIAL_PERSONA);
  const [analysis, setAnalysis] = useState(analyzePersona(INITIAL_PERSONA));
  const [mode, setMode] = useState<"dashboard" | "camera">("dashboard");
  const [simulatedAnswer, setSimulatedAnswer] = useState<string>("");

  useEffect(() => {
    setAnalysis(analyzePersona(data));
  }, [data]);

  const handleSimulateScan = () => {
    // Mocking an AI generation process
    setTimeout(() => {
      setSimulatedAnswer(
        "【回答ドラフト】\n私の強みは「粘り強さ」です。広島大学工学部での研究において、実験装置の不具合に直面した際も、諦めずに原因を究明し、解決に至りました。この経験から、困難な課題に対しても多角的な視点からアプローチし、解決までやり遂げる力を培いました。入社後もこの粘り強さを活かし、貴社の技術開発に貢献したいと考えています。"
      );
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-500 selection:text-black">
      {/* Header */}
      <header className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-cyan-500 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.5)]">
            <BrainCircuit size={24} className="text-black" />
          </div>
          <div>
            <h1 className="font-bold text-xl tracking-wide">DIGITAL TWIN</h1>
            <p className="text-xs text-slate-400 tracking-wider">PERSONA ARCHITECT</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setMode("dashboard")}
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${mode === "dashboard" ? "bg-cyan-500 text-black shadow-[0_0_20px_rgba(6,182,212,0.4)]" : "bg-slate-800 text-slate-400 hover:bg-slate-700"}`}
          >
            DASHBOARD
          </button>
          <button
            onClick={() => setMode("camera")}
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${mode === "camera" ? "bg-pink-500 text-white shadow-[0_0_20px_rgba(236,72,153,0.4)]" : "bg-slate-800 text-slate-400 hover:bg-slate-700"}`}
          >
            ES SCANNER
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto p-6">
        <AnimatePresence mode="wait">
          {mode === "dashboard" ? (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-6"
            >
              {/* Left Col: Status */}
              <div className="md:col-span-1 space-y-6">
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-600"></div>
                  <h2 className="text-slate-400 text-sm font-bold mb-4 uppercase tracking-wider">Synchronization Rate</h2>
                  <div className="h-48 relative flex items-center justify-center">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={[{ value: analysis.score }, { value: 100 - analysis.score }]}
                          innerRadius={60}
                          outerRadius={80}
                          startAngle={90}
                          endAngle={-270}
                          dataKey="value"
                          stroke="none"
                        >
                          <Cell fill="#06b6d4" />
                          <Cell fill="#1e293b" />
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                      <span className="text-4xl font-black text-cyan-400">{analysis.score}%</span>
                      <span className="text-xs text-slate-500">COMPLETE</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                  <h2 className="text-slate-400 text-sm font-bold mb-4 flex items-center gap-2">
                    <AlertTriangle size={16} className="text-yellow-500" />
                    MISSING DATA
                  </h2>
                  {analysis.missing.length > 0 ? (
                    <ul className="space-y-3">
                      {analysis.missing.map((msg, i) => (
                        <li key={i} className="flex items-start gap-3 text-sm text-slate-300 bg-slate-800/50 p-3 rounded-lg border border-red-500/20">
                          <div className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 shrink-0" />
                          {msg}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="text-center py-8 text-green-400 flex flex-col items-center gap-2">
                      <CheckCircle size={32} />
                      <span className="font-bold">All Systems Go</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Col: Persona Data */}
              <div className="md:col-span-2 space-y-6">
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-8 relative overflow-hidden">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-1">{data.profile.name}</h2>
                      <p className="text-cyan-400">{data.profile.university}</p>
                      <p className="text-slate-400 text-sm">{data.profile.department}</p>
                      <p className="text-slate-500 text-xs mt-1 bg-slate-800 inline-block px-2 py-1 rounded">{data.profile.location}</p>
                    </div>
                    <div className="w-24 h-24 bg-slate-800 rounded-full border-2 border-slate-700 flex items-center justify-center overflow-hidden">
                      {/* Placeholder for user photo */}
                      <span className="text-4xl">👤</span>
                    </div>
                  </div>

                  <div className="mb-6 bg-cyan-950/30 border border-cyan-900/50 p-4 rounded-xl">
                    <h3 className="text-xs text-cyan-500 font-bold mb-2 uppercase tracking-widest">Core Essence</h3>
                    <p className="text-slate-200 text-sm italic leading-relaxed">
                      "内なるカオスを、整理された熱狂へ。<br />
                      私は思考のエンジニアであり、物語の建築家です。"
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                      <h3 className="text-xs text-slate-500 font-bold mb-2 uppercase">Core Values (就活の軸)</h3>
                      <div className="flex flex-wrap gap-2">
                        {data.attributes.values.map(v => (
                          <span key={v} className="bg-cyan-900/30 text-cyan-300 text-xs px-2 py-1 rounded border border-cyan-800">{v}</span>
                        ))}
                      </div>
                    </div>
                    <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                      <h3 className="text-xs text-slate-500 font-bold mb-2 uppercase">Strengths</h3>
                      <div className="flex flex-wrap gap-2">
                        {data.attributes.strengths.map(v => (
                          <span key={v} className="bg-emerald-900/30 text-emerald-300 text-xs px-2 py-1 rounded border border-emerald-800">{v}</span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xs text-slate-500 font-bold mb-3 uppercase">Portfolio / Connected Apps</h3>
                    <div className="flex gap-4">
                      <a href="http://localhost:5173" target="_blank" rel="noreferrer" className="flex items-center gap-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg p-3 transition-colors group">
                        <div className="w-10 h-10 bg-blue-500/20 rounded flex items-center justify-center group-hover:scale-110 transition-transform">
                          <span className="text-xl">🐘</span>
                        </div>
                        <div>
                          <div className="text-sm font-bold text-slate-200">Anime Physics Scaler</div>
                          <div className="text-xs text-slate-500">思考の実装・物理シミュレーション</div>
                        </div>
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="camera"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              <div className="bg-slate-900 border-2 border-dashed border-slate-700 rounded-3xl aspect-[3/4] flex flex-col items-center justify-center relative overflow-hidden group">
                <div className="absolute inset-0 bg-black/50 group-hover:bg-black/40 transition-colors pointer-events-none" />
                <Camera size={64} className="text-slate-600 mb-4 group-hover:text-cyan-500 transition-colors" />
                <p className="text-slate-500 font-bold">ESの問題文を撮影</p>
                <button
                  onClick={handleSimulateScan}
                  className="absolute bottom-8 left-1/2 -translate-x-1/2 px-8 py-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-full font-bold shadow-lg shadow-cyan-900/50 transition-all active:scale-95 pointer-events-auto"
                >
                  SCAN & GENERATE
                </button>
              </div>

              <div className="space-y-4">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <BrainCircuit className="text-pink-500" />
                  AI GENERATION
                </h2>
                <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 min-h-[400px] relative">
                  {simulatedAnswer ? (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                      <p className="whitespace-pre-wrap leading-relaxed text-slate-300">{simulatedAnswer}</p>
                      <div className="mt-8 pt-4 border-t border-slate-800 flex gap-2">
                        <button className="flex-1 bg-slate-800 hover:bg-slate-700 py-2 rounded text-sm font-bold transition-colors">COPY</button>
                        <button className="flex-1 bg-slate-800 hover:bg-slate-700 py-2 rounded text-sm font-bold transition-colors">EDIT</button>
                      </div>
                    </motion.div>
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-slate-600 text-sm">
                      Waiting for input...
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
