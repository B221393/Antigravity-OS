import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, Grid } from '@react-three/drei';
import { Physics, useBox, usePlane } from '@react-three/cannon';
import { VoiceOverlay } from './components/VoiceOverlay';
import { useVoiceInput } from './hooks/useVoiceInput';
import { AnimePhysics } from './utils/physics';
import { Upload, Ruler, Zap, Box as BoxIcon } from 'lucide-react';

function FallingBox({ position, color = "#00f2fe" }: { position: [number, number, number], color?: string }) {
  const [ref] = useBox(() => ({ mass: 1, position }));
  return (
    <mesh ref={ref as any} castShadow>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={color} metalness={0.5} roughness={0.1} />
    </mesh>
  );
}

function Ground() {
  const [ref] = usePlane(() => ({ rotation: [-Math.PI / 2, 0, 0], position: [0, 0, 0] }));
  return (
    <mesh ref={ref as any} receiveShadow>
      <planeGeometry args={[1000, 1000]} />
      <meshStandardMaterial color="#1a1a1a" />
    </mesh>
  );
}

function App() {
  const { isRecording, transcript } = useVoiceInput();
  const [image, setImage] = useState<string | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [boxes, setBoxes] = useState<{ pos: [number, number, number], color: string }[]>([]);
  const [physicsStats, setPhysicsStats] = useState<any>(null);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => setImage(ev.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const spawnBox = (height = 10, color = "#00f2fe") => {
    setBoxes([...boxes, { pos: [Math.random() * 2 - 1, height, Math.random() * 2 - 1], color }]);
  };

  const applyZuneshaPreset = () => {
    const height = 35000; // 35km
    const result = AnimePhysics.calculateFall(Math.sqrt(2 * height / AnimePhysics.GRAVITY));
    setPhysicsStats({
      title: "象主（ズネーシャ）落下シミュレーション",
      height: `${height}m`,
      fallTime: `${result.time.toFixed(1)}秒`,
      impactVelocity: `${(result.velocity * 3.6).toFixed(0)} km/h`,
      note: "空気抵抗を無視した場合の理論値です。"
    });
    spawnBox(50, "#FF3366"); // Limited to 50 for visual representation in small grid
  };

  const getYoutubeEmbed = (url: string) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  };

  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
      <VoiceOverlay isRecording={isRecording} />

      {/* Main Canvas */}
      <Canvas shadows camera={{ position: [20, 20, 20], fov: 50 }}>
        <color attach="background" args={['#0c0c0e']} />
        <Grid infiniteGrid fadeDistance={100} sectionColor="#4facfe" cellColor="#1a1a1a" />
        <OrbitControls makeDefault />
        <Environment preset="city" />
        <ambientLight intensity={0.5} />
        <spotLight position={[50, 50, 50]} angle={0.15} penumbra={1} intensity={1} castShadow />

        <Physics>
          <Ground />
          {boxes.map((box, i) => (
            <FallingBox key={i} position={box.pos} color={box.color} />
          ))}
        </Physics>
      </Canvas>

      {/* UI Overlay */}
      <div style={{ position: 'absolute', top: '20px', right: '20px', display: 'flex', flexDirection: 'column', gap: '12px', width: '320px', maxHeight: '90vh', overflowY: 'auto', padding: '10px' }}>
        <div className="glass-card">
          <h2 style={{ margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1.2em' }}>
            <Zap size={20} color="#00f2fe" /> Anime Physics Engine
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ fontSize: '0.8em', color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>プリセットから再現</div>
            <button className="btn-primary" onClick={applyZuneshaPreset} style={{ width: '100%', background: 'linear-gradient(135deg, #FF3366 0%, #FF6B6B 100%)', color: 'white' }}>
              象主（ズネーシャ）の高さから落下
            </button>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', margin: '10px 0' }} />

            <button className="btn-outline" onClick={() => spawnBox(10)} style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
              <BoxIcon size={18} /> 通常物体をドロップ (10m)
            </button>

            <input
              type="text"
              placeholder="YouTube URLを入力..."
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '10px', borderRadius: '8px', color: 'white', fontSize: '0.9em' }}
            />

            <label className="btn-outline" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.9em' }}>
              <Upload size={18} /> スクリーンショットを解析
              <input type="file" hidden onChange={handleImageUpload} accept="image/*" />
            </label>
          </div>

          {transcript && (
            <div style={{ marginTop: '20px', padding: '12px', background: 'rgba(0, 242, 254, 0.1)', borderRadius: '8px', fontSize: '0.9em', borderLeft: '3px solid #00f2fe' }}>
              <strong>音声認識:</strong> {transcript}
            </div>
          )}
        </div>

        {physicsStats && (
          <div /* motion.div */ className="glass-card" style={{ borderLeft: '4px solid #FF3366' }}>
            <h3 style={{ margin: '0 0 10px', fontSize: '1em' }}>{physicsStats.title}</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.85em' }}>
              <div style={{ color: 'rgba(255,255,255,0.6)' }}>推定高さ:</div><div>{physicsStats.height}</div>
              <div style={{ color: 'rgba(255,255,255,0.6)' }}>落下時間:</div><div>{physicsStats.fallTime}</div>
              <div style={{ color: 'rgba(255,255,255,0.6)' }}>衝突速度:</div><div style={{ color: '#FF3366', fontWeight: 'bold' }}>{physicsStats.impactVelocity}</div>
            </div>
            <p style={{ margin: '10px 0 0', fontSize: '0.7em', color: 'rgba(255,255,255,0.4)' }}>{physicsStats.note}</p>
          </div>
        )}

        {youtubeUrl && getYoutubeEmbed(youtubeUrl) && (
          <div className="glass-card" style={{ padding: '8px' }}>
            <iframe
              width="100%"
              height="160"
              src={`https://www.youtube.com/embed/${getYoutubeEmbed(youtubeUrl)}`}
              title="YouTube video player"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              style={{ borderRadius: '12px' }}
            />
            <div style={{ padding: '8px', fontSize: '0.8em', color: 'rgba(255,255,255,0.6)' }}>
              動画内の特定フレームをキャプチャしてスケーリングに利用してください。
            </div>
          </div>
        )}

        {image && (
          <div className="glass-card" style={{ padding: '4px', overflow: 'hidden' }}>
            <img src={image} style={{ width: '100%', borderRadius: '16px', display: 'block' }} />
            <div style={{ padding: '12px', fontSize: '0.8em', color: 'rgba(255,255,255,0.6)' }}>
              <Ruler size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
              参照点を設定して計算を開始
            </div>
          </div>
        )}
      </div>

      <div style={{ position: 'absolute', bottom: '20px', left: '20px', color: 'rgba(255,255,255,0.3)', fontSize: '0.75em', pointerEvents: 'none' }}>
        Enterキーを押し続けて音声指示 | Zunesha Presetの実装テスト中
      </div>
    </div>
  );
}

export default App;
