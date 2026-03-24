import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Float, Box, Sphere } from '@react-three/drei';
import * as THREE from 'three';
import { VisualNode } from '@/lib/types';

function ParticleField() {
    const ref = useRef<THREE.Points>(null!);

    // Generate random particles
    const positions = useMemo(() => {
        const count = 2000;
        const positions = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 50;     // x
            positions[i * 3 + 1] = (Math.random() - 0.5) * 50; // y
            positions[i * 3 + 2] = (Math.random() - 0.5) * 50; // z
        }
        return positions;
    }, []);

    useFrame((state, delta) => {
        if (ref.current) {
            ref.current.rotation.x -= delta / 50;
            ref.current.rotation.y -= delta / 60;
        }
    });

    return (
        <group rotation={[0, 0, Math.PI / 4]}>
            <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
                <PointMaterial
                    transparent
                    color="#88ccff"
                    size={0.05}
                    sizeAttenuation={true}
                    depthWrite={false}
                    opacity={0.6}
                />
            </Points>
        </group>
    );
}

function GridPlane() {
    return (
        <group rotation={[Math.PI / 2, 0, 0]} position={[0, -5, 0]}>
            <gridHelper args={[100, 100, 0x444444, 0x222222]} />
        </group>
    );
}

function NodeObject({ node }: { node: VisualNode }) {
    // Map 2D canvas pos (approx 0-1000) to 3D world pos
    // 0,0 top-left -> -x, +y
    const x = (node.position.x - 500) / 50;
    const y = -(node.position.y - 300) / 50;

    // Animate rotation based on ID hash or random
    const ref = useRef<THREE.Mesh>(null!);
    useFrame((state, delta) => {
        if (ref.current) {
            ref.current.rotation.x += delta * 0.5;
            ref.current.rotation.y += delta * 0.2;
        }
    });

    const color = node.data.color || "#00f3ff";
    const size = node.data.size || 1;

    if (node.type === 'cube') {
        return (
            <Box ref={ref} position={[x, y, 0]} args={[size, size, size]}>
                <meshStandardMaterial color={color} wireframe={node.data.wireframe} />
            </Box>
        );
    }
    if (node.type === 'sphere') {
        return (
            <Sphere ref={ref} position={[x, y, 0]} args={[size * 0.6, 16, 16]}>
                <meshStandardMaterial color={color} wireframe={node.data.wireframe} />
            </Sphere>
        );
    }
    return null;
}

const ThreeBackground = ({ nodes = [] }: { nodes?: VisualNode[] }) => {
    return (
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0, pointerEvents: 'none' }}>
            <Canvas camera={{ position: [0, 0, 15], fov: 60 }}>
                <color attach="background" args={['#0f172a']} /> {/* Slate-900 match */}
                <fog attach="fog" args={['#0f172a', 5, 40]} />

                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
                    <ParticleField />
                </Float>

                <GridPlane />

                {/* Render Nodes as 3D Objects */}
                {nodes.map(node => (
                    <NodeObject key={node.id} node={node} />
                ))}
            </Canvas>
        </div>
    );
};

export default ThreeBackground;
