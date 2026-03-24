
'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import ReactFlow, {
    addEdge,
    useNodesState,
    useEdgesState,
    Controls,
    Background,
    Connection,
    Panel,
    MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';
import Editor from '@monaco-editor/react';
import { generatePython } from '@/lib/python-compiler';
import { generateRust } from '@/lib/rust-transpiler';
import { generateC } from '@/lib/c-transpiler';
import { decompilePython } from '@/lib/python-decompiler';
import { VisualNode } from '@/lib/types';
import ThreeBackground from './ThreeBackground';
import GameCanvas from './GameCanvas';
import {
    Play, Code, Plus, Save, Sparkles, Folder, FileCode,
    RefreshCw, Languages, Upload, Wand2, ArrowLeftRight,
    Package, AlignVerticalJustifyCenter, ToggleLeft, ToggleRight,
    Copy, Trash2, Download, MessageSquare, Undo2, Palette,
    Keyboard, Zap, Search, X, Box, Circle, Terminal, Square
} from 'lucide-react';

// Pre-built Sets
interface PresetNode {
    type: string;
    label: string;
    value?: string;
    variable?: string;
    code?: string;
}

interface PresetSet {
    name: string;
    nodes: PresetNode[];
}

const PRESET_SETS: Record<string, PresetSet> = {
    'hello_world': {
        name: '🌍 Hello World',
        nodes: [{ type: 'print', label: 'Print', value: '"Hello, World!"' }]
    },
    'input_output': {
        name: '⌨️ 入出力',
        nodes: [
            { type: 'var', label: 'Var: name', variable: 'name', value: 'input("名前を入力: ")' },
            { type: 'print', label: 'Print', value: 'f"こんにちは、{name}さん!"' }
        ]
    },
    'loop_basic': {
        name: '🔄 ループ',
        nodes: [
            { type: 'for', label: 'Loop: range(10)', code: 'for i in range(10):' },
            { type: 'print', label: 'Print', value: 'i' }
        ]
    },
    'file_read': {
        name: '📁 ファイル読込',
        nodes: [
            { type: 'python', label: 'Open File', code: 'with open("data.txt", "r") as f:' },
            { type: 'var', label: 'Var: content', variable: 'content', value: 'f.read()' },
            { type: 'print', label: 'Print', value: 'content' }
        ]
    },
    'api_fetch': {
        name: '🌐 API取得',
        nodes: [
            { type: 'import', label: 'Import: requests', code: 'import requests' },
            { type: 'var', label: 'Var: response', variable: 'response', value: 'requests.get("https://api.example.com/data")' },
            { type: 'var', label: 'Var: data', variable: 'data', value: 'response.json()' },
            { type: 'print', label: 'Print', value: 'data' }
        ]
    },
    'pandas_basic': {
        name: '🐼 Pandas',
        nodes: [
            { type: 'import', label: 'Import: pandas', code: 'import pandas as pd' },
            { type: 'var', label: 'Var: df', variable: 'df', value: 'pd.read_csv("data.csv")' },
            { type: 'print', label: 'Print', value: 'df.head()' }
        ]
    },
    'try_except': {
        name: '⚠️ エラー処理',
        nodes: [
            { type: 'python', label: 'Try', code: 'try:' },
            { type: 'python', label: 'Except', code: 'except Exception as e:\n    print(f"Error: {e}")' }
        ]
    },
    'class_basic': {
        name: '🏗️ クラス定義',
        nodes: [
            { type: 'python', label: 'Class', code: 'class MyClass:\n    def __init__(self):\n        pass' },
            { type: 'var', label: 'Instance', variable: 'obj', value: 'MyClass()' }
        ]
    }
};

// Node colors
const NODE_COLORS = [
    { name: 'Default', bg: '#334155', border: '#475569' },
    { name: 'Blue', bg: '#1e3a5f', border: '#3b82f6' },
    { name: 'Green', bg: '#14532d', border: '#22c55e' },
    { name: 'Purple', bg: '#4c1d95', border: '#a855f7' },
    { name: 'Orange', bg: '#7c2d12', border: '#f97316' },
    { name: 'Pink', bg: '#831843', border: '#ec4899' },
];

const initialNodes: VisualNode[] = [
    { id: '1', type: 'start', position: { x: 150, y: 50 }, data: { label: 'Start', realType: 'start', gameModeStart: true } }
];

// History for Undo
interface HistoryState {
    nodes: VisualNode[];
    edges: any[];
}

export default function FlowEditor() {
    const [nodes, setNodes, onNodesChange] = useNodesState<VisualNode['data']>(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [generatedCode, setGeneratedCode] = useState("# Python Code will appear here\n# Connect nodes on the left to generate code\n\n# Keyboard Shortcuts:\n# Ctrl+C: Copy code\n# Ctrl+S: Download .py\n# Ctrl+Z: Undo\n# Delete: Clear all");
    const [language, setLanguage] = useState<'python' | 'rust' | 'c'>('python');
    const [showFiles, setShowFiles] = useState(false);
    const [showCodeInput, setShowCodeInput] = useState(false);
    const [showSets, setShowSets] = useState(false);
    const [showColorPicker, setShowColorPicker] = useState(false);
    const [showShortcuts, setShowShortcuts] = useState(false);
    const [inputCode, setInputCode] = useState('');
    const [fileList, setFileList] = useState<any[]>([]);
    const [currentPath, setCurrentPath] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);
    const [isRefactoring, setIsRefactoring] = useState(false);
    const [statusMessage, setStatusMessage] = useState('');
    const [aiMode, setAiMode] = useState(false); // Retain for now, might be removed later
    const [aiCodeProcessingMode, setAiCodeProcessingMode] = useState(false);
    const [aiRefactoringMode, setAiRefactoringMode] = useState(false);
    const [history, setHistory] = useState<HistoryState[]>([]);
    const [selectedColor, setSelectedColor] = useState(NODE_COLORS[0]);
    const [searchQuery, setSearchQuery] = useState('');
    const [showSearch, setShowSearch] = useState(false);
    const [editorMode, setEditorMode] = useState<'code' | 'game'>('code');
    const [currentSceneNodeId, setCurrentSceneNodeId] = useState<string | null>(null);
    const [gameVariables, setGameVariables] = useState<Record<string, any>>({});
    const [gameHistory, setGameHistory] = useState<string[]>([]); // For basic save/load game progress

    // New states for generic input modal
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalTitle, setModalTitle] = useState('');
    const [modalInputValue, setModalInputValue] = useState('');
    const [modalCallback, setModalCallback] = useState<((value: string) => void) | null>(null);
    const [modalPlaceholder, setModalPlaceholder] = useState('');

    // Execution states
    const [isExecuting, setIsExecuting] = useState(false);
    const [executionOutput, setExecutionOutput] = useState('');
    const [showOutput, setShowOutput] = useState(false);

    // Layout State
    const [isLeftPanelOpen, setIsLeftPanelOpen] = useState(true);
    const [isRightPanelOpen, setIsRightPanelOpen] = useState(true);
    const [activeRightTab, setActiveRightTab] = useState<'code' | 'preview' | 'console'>('code');

    // Refs
    const containerRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null); // For hidden file input

    // Save to history (for undo)
    const saveToHistory = useCallback(() => {
        setHistory(prev => [...prev.slice(-20), { nodes: [...nodes], edges: [...edges] }]);
    }, [nodes, edges]);

    // Status message handler
    const showStatus = (msg: string, duration = 3000) => {
        setStatusMessage(msg);
        setTimeout(() => setStatusMessage(''), duration);
    };

    // Function to open the generic input modal
    const openInputModal = (title: string, defaultValue: string, placeholder: string, callback: (value: string) => void) => {
        setModalTitle(title);
        setModalInputValue(defaultValue);
        setModalPlaceholder(placeholder);
        setModalCallback(() => callback); // Use functional update for callback
        setIsModalOpen(true);
    };

    // === GAME RUNTIME ===
    const startGame = useCallback(() => {
        // Find the designated start node for game mode
        const startNode = nodes.find(n => n.data.realType === 'start' && n.data.gameModeStart); // Assuming a gameModeStart flag
        if (startNode) {
            setCurrentSceneNodeId(startNode.id);
            setGameVariables({}); // Reset variables
            setGameHistory([startNode.id]); // Start history
            showStatus('Game started!');
        } else {
            // Fallback to the first node if no explicit game start node
            if (nodes.length > 0) {
                setCurrentSceneNodeId(nodes[0].id);
                setGameVariables({});
                setGameHistory([nodes[0].id]);
                showStatus('Game started from first node (no explicit start node).');
            } else {
                setCurrentSceneNodeId(null);
                showStatus('No nodes to start game from!', 5000);
            }
        }
    }, [nodes]);

    const evaluateCondition = useCallback((conditionNode: VisualNode): boolean => {
        const varName = conditionNode.data.variable;
        const operator = conditionNode.data.operator;
        const value = conditionNode.data.value; // Stored as string, might need type conversion

        if (!varName || !operator || value === undefined) {
            console.error("Malformed condition node:", conditionNode);
            return false;
        }

        const currentVarValue = gameVariables[varName] || 0; // Default to 0 if not set

        // Basic type conversion for comparison
        let compareValue: any = value;
        if (typeof currentVarValue === 'number' && typeof value === 'string') {
            compareValue = parseFloat(value);
            if (isNaN(compareValue)) compareValue = value; // Fallback if not a number
        }

        switch (operator) {
            case '==': return currentVarValue == compareValue;
            case '!=': return currentVarValue != compareValue;
            case '>': return currentVarValue > compareValue;
            case '<': return currentVarValue < compareValue;
            case '>=': return currentVarValue >= compareValue;
            case '<=': return currentVarValue <= compareValue;
            default: return false;
        }
    }, [gameVariables]);

    const advanceStory = useCallback((choiceId?: string) => {
        if (!currentSceneNodeId) return;

        const currentNode = nodes.find(n => n.id === currentSceneNodeId);
        if (!currentNode) {
            console.error("Current scene node not found:", currentSceneNodeId);
            setCurrentSceneNodeId(null);
            showStatus('Game error: current node not found.', 5000);
            return;
        }

        // Handle current node's effects before moving to next
        if (currentNode.data.realType === 'setVar') {
            setGameVariables(prev => ({
                ...prev,
                [currentNode.data.variable]: currentNode.data.value
            }));
        }

        // Determine next node(s)
        let nextNodeIds: string[] = [];

        if (currentNode.data.realType === 'choice') {
            const chosenEdge = edges.find(e => e.source === currentSceneNodeId && e.sourceHandle === choiceId);
            if (chosenEdge) {
                nextNodeIds.push(chosenEdge.target);
            } else {
                console.warn("No edge found for choice:", choiceId, "from node:", currentSceneNodeId);
            }
        } else if (currentNode.data.realType === 'condition') {
            const conditionMet = evaluateCondition(currentNode);
            const trueEdge = edges.find(e => e.source === currentSceneNodeId && e.sourceHandle === 'true');
            const falseEdge = edges.find(e => e.source === currentSceneNodeId && e.sourceHandle === 'false');

            if (conditionMet && trueEdge) {
                nextNodeIds.push(trueEdge.target);
            } else if (!conditionMet && falseEdge) {
                nextNodeIds.push(falseEdge.target);
            } else {
                console.warn("Condition path not fully defined for node:", currentSceneNodeId);
                // Fallback: if condition doesn't match and no false path, try true path as default
                if (trueEdge) nextNodeIds.push(trueEdge.target);
            }
        } else if (currentNode.data.realType === 'end') {
            showStatus('End of scene!', 3000);
            setCurrentSceneNodeId(null); // End the game flow
            return;
        } else {
            // For dialogue, setVar, etc. - just follow the next single edge
            const nextEdge = edges.find(e => e.source === currentSceneNodeId && !e.sourceHandle); // Default handle for single outgoing edge
            if (nextEdge) {
                nextNodeIds.push(nextEdge.target);
            }
        }

        if (nextNodeIds.length > 0) {
            const nextNodeId = nextNodeIds[0]; // For now, only take the first next node
            setCurrentSceneNodeId(nextNodeId);
            setGameHistory(prev => [...prev, nextNodeId]);
        } else {
            setCurrentSceneNodeId(null); // No more nodes to follow
            showStatus('End of story path!', 3000);
        }
    }, [currentSceneNodeId, nodes, edges, gameVariables, evaluateCondition]);

    const handleGameChoice = useCallback((choiceId: string) => {
        advanceStory(choiceId);
    }, [advanceStory]);

    // Effect to start game when mode changes to game
    useEffect(() => {
        if (editorMode === 'game' && !currentSceneNodeId) {
            startGame();
        }
    }, [editorMode, currentSceneNodeId, startGame]);

    // === KEYBOARD SHORTCUTS ===
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Ctrl+C: Copy code
            if (e.ctrlKey && e.key === 'c' && !window.getSelection()?.toString()) {
                handleCopyCode();
                e.preventDefault();
            }
            // Ctrl+S: Download
            if (e.ctrlKey && e.key === 's') {
                handleDownload();
                e.preventDefault();
            }
            // Ctrl+Z: Undo
            if (e.ctrlKey && e.key === 'z') {
                handleUndo();
                e.preventDefault();
            }
            // Delete: Clear (only if not in input)
            if (e.key === 'Delete' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
                // Don't clear all, just show warning
                showStatus('Press Ctrl+Delete to clear all nodes');
            }
            // Ctrl+Delete: Clear all
            if (e.ctrlKey && e.key === 'Delete') {
                handleClearAll();
            }
            // Ctrl+Enter: Run Python
            if (e.ctrlKey && e.key === 'Enter') {
                handleRunCode();
                e.preventDefault();
            }
            // Ctrl+F: Search
            if (e.ctrlKey && e.key === 'f') {
                setShowSearch(s => !s);
                e.preventDefault();
            }
            // Escape: Close modals
            if (e.key === 'Escape') {
                setShowCodeInput(false);
                setShowSets(false);
                setShowSearch(false);
                setShowShortcuts(false);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [generatedCode, history, nodes, edges]);

    // === COPY CODE ===
    const handleCopyCode = async () => {
        try {
            await navigator.clipboard.writeText(generatedCode);
            showStatus('📋 Copied to clipboard!');
        } catch (e) {
            showStatus('Copy failed');
        }
    };

    // === DOWNLOAD .py ===
    const handleDownload = () => {
        const blob = new Blob([generatedCode], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `visual_coder_output.${language === 'python' ? 'py' : language === 'rust' ? 'rs' : 'c'}`;
        a.click();
        URL.revokeObjectURL(url);
        showStatus('💾 Downloaded!');
    };

    // === UNDO ===
    const handleUndo = () => {
        if (history.length === 0) {
            showStatus('Nothing to undo');
            return;
        }
        const prev = history[history.length - 1];
        setNodes(prev.nodes);
        setEdges(prev.edges);
        setHistory(h => h.slice(0, -1));
        showStatus('↩️ Undo!');
    };

    // === CLEAR ALL ===
    const handleClearAll = () => {
        saveToHistory();
        setNodes(initialNodes);
        setEdges([]);
        showStatus('🗑️ Cleared! (Ctrl+Z to undo)');
    };

    // === SAVE/LOAD PROJECT ===
    const handleSaveProject = () => {
        const projectData = { nodes, edges };
        const jsonString = JSON.stringify(projectData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `visual_coder_project_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showStatus('💾 Project Saved!');
    };

    const handleLoadProjectClick = () => {
        fileInputRef.current?.click(); // Trigger click on hidden file input
    };

    const handleLoadProject = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) {
            showStatus('No file selected.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const loadedData = JSON.parse(e.target?.result as string);
                if (loadedData.nodes && loadedData.edges) {
                    saveToHistory(); // Save current state before loading new
                    setNodes(loadedData.nodes);
                    setEdges(loadedData.edges);
                    showStatus('✅ Project Loaded!');
                } else {
                    showStatus('Invalid project file format.');
                }
            } catch (error) {
                console.error("Error loading project:", error);
                showStatus('Failed to load project file.');
            }
        };
        reader.readAsText(file);
    };

    // AI Generation Handler
    const generateAINodeCode = async (nodeId: string, prompt: string) => {
        if (!aiMode) {
            showStatus('AI Mode is OFF. Enable it to use AI features.');
            return;
        }
        setIsGenerating(true);
        showStatus('AI generating code...');
        try {
            const res = await fetch('/api/ai', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });
            const data = await res.json();

            setNodes((nds) => nds.map(n => {
                if (n.id === nodeId) {
                    return {
                        ...n,
                        data: { ...n.data, code: data.code, label: `AI: ${prompt}` }
                    };
                }
                return n;
            }));
            showStatus('AI code generated!');
        } catch (e) {
            console.error(e);
            showStatus('AI Generation Failed');
        } finally {
            setIsGenerating(false);
        }
    };

    // AUTO-ALIGN
    const alignNodes = () => {
        saveToHistory();
        const xPos = 150;
        const yStep = 100;
        let yPos = 50;

        const sortedNodes = [...nodes].sort((a, b) => a.position.y - b.position.y);

        setNodes(sortedNodes.map((node, index) => ({
            ...node,
            position: { x: xPos, y: yPos + (index * yStep) }
        })));

        showStatus('📐 Nodes aligned!');
    };

    // ADD PRESET SET
    const addPresetSet = (setKey: string) => {
        saveToHistory();
        const preset = PRESET_SETS[setKey as keyof typeof PRESET_SETS];
        if (!preset) return;

        const maxY = Math.max(...nodes.map(n => n.position.y), 0);
        let yPos = maxY + 100;
        const xPos = 150;
        let prevNodeId = nodes.length > 0 ? nodes[nodes.length - 1].id : null;

        if (edges.length > 0) {
            const targetIds = new Set(edges.map(e => e.target));
            const sourceIds = new Set(edges.map(e => e.source));
            const endNodes = nodes.filter(n => !targetIds.has(n.id) || !sourceIds.has(n.id));
            if (endNodes.length > 0) {
                prevNodeId = endNodes[endNodes.length - 1].id;
            }
        }

        const newNodes: VisualNode[] = [];
        const newEdges: any[] = [];

        preset.nodes.forEach((nodeData, index) => {
            const nodeId = `${nodeData.type}-${Date.now()}-${index}`;

            newNodes.push({
                id: nodeId,
                type: 'default',
                position: { x: xPos, y: yPos },
                data: {
                    label: nodeData.label,
                    value: nodeData.value,
                    variable: nodeData.variable,
                    code: nodeData.code,
                    realType: nodeData.type
                },
                style: { backgroundColor: selectedColor.bg, borderColor: selectedColor.border }
            });

            if (prevNodeId) {
                newEdges.push({
                    id: `edge-${prevNodeId}-${nodeId}`,
                    source: prevNodeId,
                    target: nodeId
                });
            }

            prevNodeId = nodeId;
            yPos += 100;
        });

        setNodes((nds) => [...nds, ...newNodes]);
        setEdges((eds) => [...eds, ...newEdges]);
        setShowSets(false);
        showStatus(`✅ ${preset.name} を追加`);
    };

    // Code → Visual
    const handleCodeToVisual = async () => {
        if (!inputCode.trim()) {
            showStatus('Please enter some Python code');
            return;
        }

        saveToHistory();
        setIsGenerating(true);
        showStatus('Converting code to visual nodes...');

        try {
            if (aiCodeProcessingMode) { // Use granular AI code processing mode
                const res = await fetch('/api/decompile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: inputCode })
                });

                const data = await res.json();

                if (data.nodes && data.edges) {
                    setNodes(data.nodes);
                    setEdges(data.edges);
                    if (data.warnings && data.warnings.length > 0) {
                        showStatus(`AI converted to nodes with warnings: ${data.warnings.join('; ')}`);
                    } else {
                        showStatus('AI converted to nodes!');
                    }
                } else { // AI failed to provide nodes/edges, fallback to local parser
                    const result = decompilePython(inputCode);
                    setNodes(result.nodes);
                    setEdges(result.edges);
                    if (result.warnings && result.warnings.length > 0) {
                        showStatus(`AI failed. Local parser converted with warnings: ${result.warnings.join('; ')}`);
                    } else {
                        showStatus('AI failed. Converted using local parser!');
                    }
                }
            } else { // Not AI mode, use local parser
                const result = decompilePython(inputCode);
                setNodes(result.nodes);
                setEdges(result.edges);
                if (result.warnings && result.warnings.length > 0) {
                    showStatus(`Code converted to nodes with warnings: ${result.warnings.join('; ')}`);
                } else {
                    showStatus('Code converted to nodes!');
                }
            }

            setShowCodeInput(false);
            setInputCode('');
            // Status messages are now handled within the if/else branches based on warnings.
        } catch (e: any) { // Catch any error during AI decompilation
            console.error(e);
            showStatus(`AI Decompilation failed: ${e.message || 'Unknown error'}. Attempting local parser...`);
            try {
                const result = decompilePython(inputCode);
                setNodes(result.nodes);
                setEdges(result.edges);
                showStatus('Converted using local parser!');
            } catch (localError: any) { // Catch errors from local parser
                console.error("Local decompilation failed:", localError);
                setNodes(initialNodes); // Clear nodes on severe error
                setEdges([]);
                showStatus(`Local Decompilation failed: ${localError.message || 'Unknown error'}.`);
            }
        } finally {
            setIsGenerating(false);
        }
    };

    // AI Refactor
    const handleRefactor = async () => {
        if (!aiRefactoringMode) { // Use granular AI refactoring mode
            showStatus('AI Refactoring is OFF. Enable it to use AI Refactor.');
            return;
        }
        if (!generatedCode || generatedCode.startsWith('#')) {
            showStatus('No code to refactor');
            return;
        }

        setIsRefactoring(true);
        showStatus('AI refactoring code...');

        try {
            const res = await fetch('/api/refactor', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: generatedCode })
            });

            const data = await res.json();

            if (data.refactoredCode) {
                setGeneratedCode(data.refactoredCode);
                showStatus(`Refactored: ${data.improvements?.join(', ') || 'Code optimized'}`);
            }
        } catch (e) {
            console.error(e);
            showStatus('Refactor failed');
        } finally {
            setIsRefactoring(false);
        }
    };

    // === PYTHON EXECUTION ===
    const handleRunCode = async () => {
        if (!generatedCode || generatedCode.startsWith('#') || language !== 'python') {
            showStatus('No Python code to run.');
            return;
        }
        setIsExecuting(true);
        setShowOutput(true);
        setExecutionOutput('⏳ Running...\n');
        showStatus('Executing Python...');

        try {
            const res = await fetch('/api/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: generatedCode }),
            });
            const data = await res.json();

            let output = '';
            if (data.timedOut) {
                output += '⚠️ TIMEOUT: Execution exceeded 10 seconds.\n\n';
            }
            if (data.stdout) {
                output += data.stdout;
            }
            if (data.stderr) {
                output += '\n--- STDERR ---\n' + data.stderr;
            }
            if (data.error) {
                output += '\n❌ Error: ' + data.error;
            }
            if (!output.trim()) {
                output = '✅ Executed successfully (no output).';
            }

            output += `\n\n--- Exit Code: ${data.exitCode ?? 'N/A'} | ${data.timestamp || new Date().toISOString()} ---`;

            setExecutionOutput(output);
            showStatus(data.exitCode === 0 ? '✅ Execution complete!' : `⚠️ Exit code: ${data.exitCode}`);
        } catch (e: any) {
            setExecutionOutput(`❌ Request failed: ${e.message}`);
            showStatus('Execution failed');
        } finally {
            setIsExecuting(false);
        }
    };

    // File System
    const loadFiles = async (path = "") => {
        try {
            const res = await fetch(`/api/files?path=${encodeURIComponent(path)}`);
            const data = await res.json();
            if (data.files) {
                setFileList(data.files);
                setCurrentPath(path);
            }
        } catch (e) { console.error(e); }
    };

    useEffect(() => {
        if (showFiles) loadFiles();
    }, [showFiles]);

    // Compiler
    const compile = useCallback(() => {
        let code = "";
        const visualNodes = nodes as VisualNode[];

        if (language === 'python') code = generatePython(visualNodes, edges);
        else if (language === 'rust') code = generateRust(visualNodes, edges);
        else if (language === 'c') code = generateC(visualNodes, edges);

        setGeneratedCode(code);
    }, [nodes, edges, language]);

    useEffect(() => {
        compile();
    }, [nodes, edges, language, compile]);

    // Run/Compile Button Handler
    const handleRunClick = useCallback(() => {
        compile();
        setIsRightPanelOpen(true);
        if (editorMode === 'game') {
            setActiveRightTab('preview');
            startGame();
        } else {
            setActiveRightTab('code');
            // Optional: Trigger python run if needed, but for now just show code
        }
    }, [compile, editorMode, startGame]);

    const onConnect = useCallback(
        (params: Connection) => {
            saveToHistory();
            setEdges((eds) => addEdge(params, eds));
        },
        [setEdges, saveToHistory],
    );

    const addNode = (type: string) => {
        saveToHistory();
        const id = `${type}-${Date.now()}`;
        const newNode: VisualNode = {
            id,
            type: 'default',
            position: { x: Math.random() * 400 + 100, y: Math.random() * 400 + 50 },
            data: {
                label: type.toUpperCase(),
                value: type === 'print' ? '"Hello"' : '0',
                variable: 'x',
                code: type === 'python' ? '# Raw Code' : undefined,
                realType: type,
                aiPrompt: ''
            },
            style: { backgroundColor: selectedColor.bg, borderColor: selectedColor.border }
        };

        if (type === 'ai') {
            if (!aiCodeProcessingMode) {
                showStatus('AI Code Processing is OFF. Enable it first.');
                return;
            }
            openInputModal(
                "AI Node Prompt",
                "",
                "What should this block do?",
                (userPrompt) => {
                    if (userPrompt) {
                        newNode.data.aiPrompt = userPrompt;
                        newNode.data.label = `AI: ${userPrompt} (Generating...)`;
                        newNode.data.realType = 'python';
                        generateAINodeCode(id, userPrompt);
                        setNodes((nds) => nds.concat(newNode)); // Add node only after prompt is entered
                    }
                }
            );
            return; // Exit addNode for async input
        } else if (type === 'python') newNode.data.label = 'Python Script';
        else if (type === 'print') newNode.data.label = 'Print';
        else if (type === 'comment') {
            let commentText: string | null = null;
            openInputModal(
                "Add Comment",
                "TODO",
                "Comment text",
                (value) => {
                    const finalCommentText = value || 'TODO'; // Handle empty input
                    newNode.data.label = `📝 ${finalCommentText}`;
                    newNode.data.code = `# ${finalCommentText}`;
                    newNode.data.realType = 'python';
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return; // Exit addNode for async input
        } else if (type === 'import') {
            openInputModal(
                "Import Module",
                "module",
                "Module name (e.g., requests, numpy)",
                (moduleName) => {
                    const finalModuleName = moduleName || 'module';
                    newNode.data.label = `Import: ${finalModuleName}`;
                    newNode.data.code = `import ${finalModuleName}`;
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return;
        } else if (type === 'function') {
            openInputModal(
                "Define Function",
                "my_func",
                "Function name",
                (funcName) => {
                    const finalFuncName = funcName || 'my_func';
                    newNode.data.label = `Def: ${finalFuncName}`;
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return;
        } else if (type === 'var') {
            openInputModal(
                "Variable Name",
                "x",
                "Variable name",
                (varName) => {
                    openInputModal(
                        "Variable Value",
                        "0",
                        "Value",
                        (varValue) => {
                            const finalVarName = varName || 'x';
                            const finalVarValue = varValue || '0';
                            newNode.data.label = `Var: ${finalVarName}`;
                            newNode.data.variable = finalVarName;
                            newNode.data.value = finalVarValue;
                            setNodes((nds) => nds.concat(newNode));
                        }
                    );
                }
            );
            return;
        } else if (type === 'if') {
            openInputModal(
                "If Condition",
                "True",
                "Condition (e.g. x > 5)?",
                (cond) => {
                    const finalCond = cond || 'True';
                    newNode.data.label = `If: ${finalCond}`;
                    newNode.data.condition = finalCond;
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return;
        } else if (type === 'while') {
            openInputModal(
                "While Condition",
                "True",
                "While Condition?",
                (cond) => {
                    const finalCond = cond || 'True';
                    newNode.data.label = `While: ${finalCond}`;
                    newNode.data.condition = finalCond;
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return;
        } else if (type === 'for') {
            openInputModal(
                "For Loop Iterator",
                "i in range(10)",
                "Iterator? (e.g. i in range(10))",
                (iterator) => {
                    const finalIterator = iterator || 'i in range(10)';
                    newNode.data.label = `For: ${finalIterator}`;
                    newNode.data.code = `for ${finalIterator}:`;
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return;
        } else if (type === 'list') {
            openInputModal(
                "List Name",
                "my_list",
                "List Name?",
                (listName) => {
                    openInputModal(
                        "List Items",
                        "1, 2, 3",
                        "Items? (comma separated)",
                        (items) => {
                            const finalListName = listName || 'my_list';
                            const finalItems = items || '1, 2, 3';
                            newNode.data.label = `List: ${finalListName}`;
                            newNode.data.variable = finalListName;
                            newNode.data.value = `[${finalItems}]`;
                            newNode.data.realType = 'var';
                            setNodes((nds) => nds.concat(newNode));
                        }
                    );
                }
            );
            return;
        } else if (type === 'dict') {
            openInputModal(
                "Dictionary Name",
                "my_dict",
                "Dictionary Name?",
                (dictName) => {
                    const finalDictName = dictName || 'my_dict';
                    newNode.data.label = `Dict: ${finalDictName}`;
                    newNode.data.variable = finalDictName;
                    newNode.data.value = `{'key': 'value'}`; // Value remains hardcoded for now
                    newNode.data.realType = 'var';
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return;
        } else if (type === 'class') {
            openInputModal(
                "Class Name",
                "MyClass",
                "Class Name?",
                (className) => {
                    const finalClassName = className || 'MyClass';
                    newNode.data.label = `Class: ${finalClassName}`;
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return;
        } else if (type === 'return') {
            openInputModal(
                "Return Value",
                "",
                "Return value?",
                (retVal) => {
                    const finalRetVal = retVal || '';
                    newNode.data.label = `Return: ${finalRetVal}`;
                    newNode.data.value = finalRetVal;
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return;
        } else if (type === 'try') {
            newNode.data.label = 'Try / Except';
        } else if (type === 'math') {
            openInputModal(
                "Math Expression",
                "0",
                "Expression? (e.g. a + b)",
                (expr) => {
                    openInputModal(
                        "Assign to Variable",
                        "result",
                        "Assign to variable?",
                        (target) => {
                            const finalExpr = expr || '0';
                            const finalTarget = target || 'result';
                            newNode.data.label = `${finalTarget} = ${finalExpr}`;
                            newNode.data.variable = finalTarget;
                            newNode.data.value = finalExpr;
                            newNode.data.realType = 'var';
                            setNodes((nds) => nds.concat(newNode));
                        }
                    );
                }
            );
            return;
        } else if (type === 'compare') {
            openInputModal(
                "Comparison Expression",
                "True",
                "Comparison? (e.g. a == b)",
                (expr) => {
                    const finalExpr = expr || 'True';
                    newNode.data.label = `Compare: ${finalExpr}`;
                    newNode.data.condition = finalExpr;
                    newNode.data.realType = 'if';
                    setNodes((nds) => nds.concat(newNode));
                }
            );
            return;
        } else if (type === 'cube') {
            openInputModal(
                "Cube X Position",
                "0",
                "X Coordinate (e.g., 0)",
                (xPosStr) => {
                    openInputModal(
                        "Cube Y Position",
                        "0",
                        "Y Coordinate (e.g., 0)",
                        (yPosStr) => {
                            const x = parseFloat(xPosStr) || 0;
                            const y = parseFloat(yPosStr) || 0;

                            // Update position of newNode
                            newNode.position = { x: x, y: y };
                            newNode.data.label = 'Cube';
                            newNode.data.color = '#00f3ff';
                            newNode.data.size = 1;
                            newNode.data.realType = 'cube';
                            newNode.style = { ...newNode.style, backgroundColor: 'rgba(0, 243, 255, 0.2)', borderColor: '#00f3ff' };
                            setNodes((nds) => nds.concat(newNode)); // Add node only after all inputs
                        }
                    );
                }
            );
            return; // Exit addNode for async input
        } else if (type === 'sphere') {
            openInputModal(
                "Sphere X Position",
                "0",
                "X Coordinate (e.g., 0)",
                (xPosStr) => {
                    openInputModal(
                        "Sphere Y Position",
                        "0",
                        "Y Coordinate (e.g., 0)",
                        (yPosStr) => {
                            const x = parseFloat(xPosStr) || 0;
                            const y = parseFloat(yPosStr) || 0;

                            // Update position of newNode
                            newNode.position = { x: x, y: y };
                            newNode.data.label = 'Sphere';
                            newNode.data.color = '#ff0055';
                            newNode.data.size = 1.5;
                            newNode.data.realType = 'sphere';
                            newNode.style = { ...newNode.style, backgroundColor: 'rgba(255, 0, 85, 0.2)', borderColor: '#ff0055' };
                            setNodes((nds) => nds.concat(newNode)); // Add node only after all inputs
                        }
                    );
                }
            );
            return; // Exit addNode for async input
        } else if (type === 'dialogue') {
            openInputModal(
                "Speaker Name",
                "???",
                "Enter speaker name (or ??? for narration)",
                (speaker) => {
                    openInputModal(
                        "Dialogue Text",
                        "Hello, World!",
                        "Enter dialogue or narration text",
                        (text) => {
                            newNode.data.label = `${speaker}: ${text.substring(0, 20)}...`;
                            newNode.data.speaker = speaker;
                            newNode.data.text = text;
                            newNode.data.realType = 'dialogue';
                            newNode.style = { ...newNode.style, backgroundColor: '#4a0e4e', borderColor: '#a855f7' }; // Purple for dialogue
                            setNodes((nds) => nds.concat(newNode));
                        }
                    );
                }
            );
            return;
        } else if (type === 'end') {
            newNode.data.label = 'End Scene';
            newNode.data.realType = 'end';
            newNode.style = { ...newNode.style, backgroundColor: '#4a1111', borderColor: '#ef4444' }; // Red for end
            setNodes((nds) => nds.concat(newNode));
            return; // No modal, so add immediately and return
        } else if (type === 'setVar') {
            openInputModal(
                "Variable Name",
                "affection",
                "Enter variable name (e.g., affection, flag)",
                (varName) => {
                    openInputModal(
                        "Variable Value",
                        "0",
                        "Enter value (e.g., 1, true, character_name)",
                        (varValue) => {
                            newNode.data.label = `Set Var: ${varName} = ${varValue.substring(0, 15)}...`;
                            newNode.data.variable = varName;
                            newNode.data.value = varValue;
                            newNode.data.realType = 'setVar';
                            newNode.style = { ...newNode.style, backgroundColor: '#3d4b0f', borderColor: '#d9f99d' }; // Green-ish for variables
                            setNodes((nds) => nds.concat(newNode));
                        }
                    );
                }
            );
            return;
        } else if (type === 'condition') {
            openInputModal(
                "Condition Variable",
                "affection",
                "Enter variable name (e.g., affection)",
                (varName) => {
                    openInputModal(
                        "Condition Operator",
                        "==",
                        "Enter operator (e.g., ==, >, <, >=, <=, !=)",
                        (operator) => {
                            openInputModal(
                                "Condition Value",
                                "5",
                                "Enter value to compare (e.g., 5, true)",
                                (varValue) => {
                                    newNode.data.label = `If ${varName} ${operator} ${varValue.substring(0, 10)}...`;
                                    newNode.data.variable = varName;
                                    newNode.data.operator = operator;
                                    newNode.data.value = varValue;
                                    newNode.data.realType = 'condition';
                                    newNode.style = { ...newNode.style, backgroundColor: '#5c1a0e', borderColor: '#fca5a5' }; // Red-ish for conditions
                                    setNodes((nds) => nds.concat(newNode));
                                }
                            );
                        }
                    );
                }
            );
            return;
        } else if (type === 'choice') {
            openInputModal(
                "Choice Node Label",
                "Make a choice",
                "Enter label for this choice node",
                (label) => {
                    openInputModal(
                        "Choice 1 Text",
                        "Option A",
                        "Enter text for Choice 1",
                        (choice1Text) => {
                            openInputModal(
                                "Choice 2 Text",
                                "Option B",
                                "Enter text for Choice 2",
                                (choice2Text) => {
                                    newNode.data.label = label;
                                    newNode.data.choices = [
                                        { text: choice1Text || "Option A", nextNode: '' },
                                        { text: choice2Text || "Option B", nextNode: '' }
                                    ];
                                    newNode.data.realType = 'choice';
                                    newNode.style = { ...newNode.style, backgroundColor: '#105252', borderColor: '#2dd4bf' }; // Teal for choices
                                    setNodes((nds) => nds.concat(newNode));
                                }
                            );
                        }
                    );
                }
            );
            return;
        }

        // For nodes that don't use modals, add them directly
        setNodes((nds) => nds.concat(newNode));
    };

    // Filter nodes by search
    const filteredPresets = Object.entries(PRESET_SETS).filter(([_, set]) =>
        set.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Helper to filter and render node buttons
    const filterNodeButtons = (categoryButtons: { type: string; label: string; icon: React.ReactNode; className?: string }[]) => {
        if (!searchQuery) {
            return categoryButtons.map(btn => (
                <button key={btn.type} onClick={() => addNode(btn.type)} className={`btn-node ${btn.className || ''}`}>
                    {btn.icon} {btn.label}
                </button>
            ));
        }
        const lowerCaseQuery = searchQuery.toLowerCase();
        return categoryButtons
            .filter(btn => btn.label.toLowerCase().includes(lowerCaseQuery) || btn.type.toLowerCase().includes(lowerCaseQuery))
            .map(btn => (
                <button key={btn.type} onClick={() => addNode(btn.type)} className={`btn-node ${btn.className || ''}`}>
                    {btn.icon} {btn.label}
                </button>
            ));
    };

    return (
        <div ref={containerRef} className="flex h-screen w-full bg-slate-900 text-white overflow-hidden font-sans">

            {/* LEFT SIDEBAR (Toolbox) */}
            <div className={`${isLeftPanelOpen ? 'w-64' : 'w-0'} flex flex-col border-r border-slate-700 bg-slate-800/90 backdrop-blur-md transition-all duration-300 ease-in-out relative z-20`}>
                <div className={`flex flex-col h-full w-64 ${!isLeftPanelOpen && 'invisible'}`}>
                    <div className="p-3 border-b border-slate-700 flex justify-between items-center bg-slate-900/50">
                        <h1 className="text-sm font-bold flex items-center gap-2">
                            <Code className="text-blue-400" size={16} /> Visual Coder
                        </h1>
                        <div className="flex gap-1">
                            <button onClick={() => setIsLeftPanelOpen(false)} className="hover:text-white text-slate-400"><ToggleLeft size={16} /></button>
                        </div>
                    </div>

                    {/* Search & Filter */}
                    <div className="p-2 border-b border-slate-700/50">
                        <div className="relative">
                            <Search size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Search nodes..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-7 pr-2 py-1 bg-slate-900 text-xs rounded border border-slate-700 focus:border-blue-500 focus:outline-none text-slate-300 placeholder-slate-600"
                            />
                        </div>
                    </div>

                    {/* Scrollable Node List */}
                    <div className="flex-1 overflow-y-auto p-2 space-y-4">

                        {/* AI Section */}
                        <div className="space-y-1">
                            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex justify-between items-center">
                                AI Assistant
                                <div className="flex gap-1">
                                    <button
                                        onClick={() => setAiCodeProcessingMode(!aiCodeProcessingMode)}
                                        title={aiCodeProcessingMode ? "AI Generation ON" : "AI Generation OFF"}
                                        className={`p-0.5 rounded ${aiCodeProcessingMode ? 'text-purple-400 bg-purple-900/30' : 'text-slate-600'}`}
                                    >
                                        <Sparkles size={10} />
                                    </button>
                                    <button
                                        onClick={() => setAiRefactoringMode(!aiRefactoringMode)}
                                        title={aiRefactoringMode ? "AI Refactor ON" : "AI Refactor OFF"}
                                        className={`p-0.5 rounded ${aiRefactoringMode ? 'text-orange-400 bg-orange-900/30' : 'text-slate-600'}`}
                                    >
                                        <Wand2 size={10} />
                                    </button>
                                </div>
                            </div>
                            {aiCodeProcessingMode && (
                                <button onClick={() => addNode('ai')} className="w-full flex items-center gap-2 p-2 bg-gradient-to-r from-purple-900/40 to-blue-900/40 border border-purple-500/30 hover:border-purple-400/50 rounded text-xs text-purple-200 transition-all group">
                                    <Sparkles size={14} className="group-hover:text-purple-300" />
                                    <span>Ask AI to Generate Node...</span>
                                </button>
                            )}
                        </div>

                        {/* Node Categories */}
                        <div className="space-y-3">
                            {/* Basic Logic */}
                            <div>
                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 ml-1">Logic & Control</div>
                                <div className="grid grid-cols-2 gap-1.5">
                                    {filterNodeButtons([
                                        { type: 'if', label: 'If / Else', icon: <Play size={10} className="rotate-90" />, className: 'border-l-2 border-l-purple-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'for', label: 'Loop', icon: <RefreshCw size={10} />, className: 'border-l-2 border-l-purple-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'while', label: 'While', icon: <RefreshCw size={10} />, className: 'border-l-2 border-l-purple-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'try', label: 'Try/Catch', icon: <Zap size={10} />, className: 'border-l-2 border-l-red-500 bg-slate-700/50 hover:bg-slate-700' },
                                    ])}
                                </div>
                            </div>

                            {/* Variables & Data */}
                            <div>
                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 ml-1">Variables & Data</div>
                                <div className="grid grid-cols-2 gap-1.5">
                                    {filterNodeButtons([
                                        { type: 'var', label: 'Variable', icon: <Box size={10} />, className: 'border-l-2 border-l-yellow-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'list', label: 'List', icon: <AlignVerticalJustifyCenter size={10} />, className: 'border-l-2 border-l-blue-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'dict', label: 'Dictionary', icon: <Package size={10} />, className: 'border-l-2 border-l-blue-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'print', label: 'Print', icon: <Terminal size={10} />, className: 'border-l-2 border-l-gray-500 bg-slate-700/50 hover:bg-slate-700' },
                                    ])}
                                </div>
                            </div>

                            {/* Math */}
                            <div>
                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 ml-1">Math</div>
                                <div className="grid grid-cols-1 gap-1.5">
                                    {filterNodeButtons([
                                        { type: 'math', label: 'Math Operation', icon: <Plus size={10} />, className: 'border-l-2 border-l-green-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'compare', label: 'Compare', icon: <ArrowLeftRight size={10} />, className: 'border-l-2 border-l-green-500 bg-slate-700/50 hover:bg-slate-700' },
                                    ])}
                                </div>
                            </div>

                            {/* Functions & Classes */}
                            <div>
                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 ml-1">Structure</div>
                                <div className="grid grid-cols-2 gap-1.5">
                                    {filterNodeButtons([
                                        { type: 'function', label: 'Function', icon: <Code size={10} />, className: 'border-l-2 border-l-pink-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'return', label: 'Return', icon: <Undo2 size={10} />, className: 'border-l-2 border-l-pink-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'class', label: 'Class', icon: <Box size={10} />, className: 'border-l-2 border-l-pink-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'import', label: 'Import', icon: <Download size={10} />, className: 'border-l-2 border-l-gray-500 bg-slate-700/50 hover:bg-slate-700' },
                                    ])}
                                </div>
                            </div>

                            {/* Game Nodes */}
                            <div>
                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 ml-1 text-emerald-400">Game Engine</div>
                                <div className="grid grid-cols-2 gap-1.5">
                                    {filterNodeButtons([
                                        { type: 'game_start', label: 'Start Game', icon: <Play size={10} />, className: 'border-l-2 border-l-emerald-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'scene_bg', label: 'Background', icon: <Box size={10} />, className: 'border-l-2 border-l-emerald-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'dialogue', label: 'Dialogue', icon: <MessageSquare size={10} />, className: 'border-l-2 border-l-cyan-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'choice', label: 'Choice', icon: <ArrowLeftRight size={10} />, className: 'border-l-2 border-l-orange-500 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'show_char', label: 'Character', icon: <Circle size={10} />, className: 'border-l-2 border-l-pink-400 bg-slate-700/50 hover:bg-slate-700' },
                                        { type: 'condition', label: 'Game Logic', icon: <Zap size={10} />, className: 'border-l-2 border-l-red-400 bg-slate-700/50 hover:bg-slate-700' },
                                    ])}
                                </div>
                            </div>

                            {/* Presets */}
                            <div>
                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 ml-1">Presets</div>
                                <div className="flex flex-col gap-1">
                                    {Object.entries(PRESET_SETS).map(([key, set]) => (
                                        <button key={key} onClick={() => addPresetSet(key)} className="text-left text-xs p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors">
                                            {set.name}
                                        </button>
                                    ))}
                                </div>
                            </div>

                        </div>
                    </div>

                    {/* Files & Project */}
                    <div className="border-t border-slate-700 p-2">
                        <div className="flex flex-col gap-1">
                            <button onClick={() => setShowFiles(!showFiles)} className="flex items-center gap-2 p-1.5 hover:bg-slate-700 rounded text-xs text-slate-400 hover:text-white">
                                <Folder size={12} /> {showFiles ? 'Hide Files' : 'Show Files'}
                            </button>
                            {showFiles && (
                                <div className="pl-4 border-l border-slate-700 ml-2 mt-1 space-y-1">
                                    <div className="text-[10px] text-slate-500 mb-1">/{currentPath || 'root'}</div>
                                    {currentPath !== "" && (
                                        <div onClick={() => loadFiles(currentPath.split('/').slice(0, -1).join('/'))} className="cursor-pointer hover:text-white text-slate-400 text-xs">..</div>
                                    )}
                                    {fileList.slice(0, 5).map((f, i) => (
                                        <div key={i} onClick={() => f.isDirectory ? loadFiles(f.path) : null} className="flex items-center gap-1 text-xs text-slate-400 cursor-pointer hover:text-white truncate">
                                            {f.isDirectory ? <Folder size={10} className="text-yellow-500" /> : <FileCode size={10} className="text-blue-400" />}
                                            {f.name}
                                        </div>
                                    ))}
                                </div>
                            )}
                            <div className="grid grid-cols-2 gap-1 mt-2">
                                <button onClick={handleSaveProject} className="flex items-center justify-center gap-1 p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-[10px]"><Save size={10} /> Save</button>
                                <button onClick={handleLoadProjectClick} className="flex items-center justify-center gap-1 p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-[10px]"><Upload size={10} /> Load</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* MAIN CANVAS AREA (Center) */}
            <div className="flex-1 relative flex flex-col min-w-0 bg-[#1e1e1e]">

                {/* Top Toolbar (Canvas Controls) */}
                <div className="h-10 border-b border-slate-700 bg-slate-800 flex items-center justify-between px-3">
                    <div className="flex items-center gap-2">
                        {!isLeftPanelOpen && (
                            <button onClick={() => setIsLeftPanelOpen(true)} className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white" title="Open Toolbox">
                                <ToggleLeft size={18} className="rotate-180" />
                            </button>
                        )}
                        <div className="h-4 w-px bg-slate-700 mx-1" />
                        <button onClick={handleUndo} className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white" title="Undo"><Undo2 size={14} /></button>
                        <button onClick={handleClearAll} className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-red-400" title="Clear Canvas"><Trash2 size={14} /></button>
                        <button onClick={alignNodes} className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white" title="Auto Align"><AlignVerticalJustifyCenter size={14} /></button>
                    </div>

                    <div className="flex items-center gap-2">
                        <div className="bg-slate-900 rounded px-2 py-1 flex items-center gap-2 text-xs border border-slate-700">
                            <span className="text-slate-500">Mode:</span>
                            <span className="text-slate-300 font-bold">{editorMode === 'code' ? 'Code Logic' : 'Game Logic'}</span>
                        </div>
                        <button
                            onClick={handleRunClick}
                            className="flex items-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-500 text-white text-xs font-bold rounded shadow-lg shadow-green-900/20 transition-all hover:scale-105 active:scale-95"
                        >
                            <Play size={12} fill="currentColor" /> Run {editorMode === 'game' ? '(Game)' : ''}
                        </button>

                        {!isRightPanelOpen && (
                            <button onClick={() => setIsRightPanelOpen(true)} className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white ml-2" title="Open Preview">
                                <ToggleRight size={18} />
                            </button>
                        )}
                    </div>
                </div>

                {/* Canvas */}
                <div className="flex-1 relative bg-[#0f1115]">
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onConnect={onConnect}
                        fitView
                        className="bg-dots-pattern"
                    >
                        <Background color="#333" gap={20} size={1} />
                        <Controls className="bg-slate-800 border-slate-700 fill-slate-400" />
                        <MiniMap
                            className="bg-slate-800 border-slate-700 rounded-lg overflow-hidden"
                            maskColor="rgba(0, 0, 0, 0.4)"
                            nodeColor={(n) => n.style?.backgroundColor as string || '#334155'}
                        />
                        <Panel position="bottom-center" className="bg-slate-800/80 backdrop-blur px-3 py-1 rounded-full border border-slate-700 text-[10px] text-slate-400">
                            {nodes.length} nodes • {edges.length} connections
                        </Panel>
                    </ReactFlow>

                    {/* Background Visuals (Subtle 3D or Pattern) */}
                    {editorMode === 'code' && (
                        <div className="absolute inset-0 pointer-events-none opacity-20 z-0">
                            <ThreeBackground nodes={nodes} />
                        </div>
                    )}
                </div>
            </div>

            {/* RIGHT SIDEBAR (Preview & Code) */}
            <div className={`${isRightPanelOpen ? 'w-[400px]' : 'w-0'} flex flex-col border-l border-slate-700 bg-[#1e1e1e] transition-all duration-300 ease-in-out relative`}>
                <div className={`flex flex-col h-full w-[400px] ${!isRightPanelOpen && 'invisible'}`}>

                    {/* Tab Header */}
                    <div className="flex items-center bg-slate-800 border-b border-slate-700">
                        <button
                            onClick={() => setActiveRightTab('code')}
                            className={`flex-1 py-2 text-xs font-medium border-b-2 transition-colors ${activeRightTab === 'code' ? 'border-blue-500 text-white bg-slate-700/50' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
                        >
                            Generated Code
                        </button>
                        <button
                            onClick={() => setActiveRightTab('preview')}
                            className={`flex-1 py-2 text-xs font-medium border-b-2 transition-colors ${activeRightTab === 'preview' ? 'border-purple-500 text-white bg-slate-700/50' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
                        >
                            Game Stage
                        </button>
                        <button
                            onClick={() => setActiveRightTab('console')}
                            className={`flex-1 py-2 text-xs font-medium border-b-2 transition-colors ${activeRightTab === 'console' ? 'border-green-500 text-white bg-slate-700/50' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
                        >
                            Console
                        </button>
                        <button onClick={() => setIsRightPanelOpen(false)} className="px-2 text-slate-400 hover:text-white"><ToggleRight size={16} /></button>
                    </div>

                    {/* Content Area */}
                    <div className="flex-1 relative overflow-hidden flex flex-col">

                        {/* CODE TAB */}
                        {activeRightTab === 'code' && (
                            <div className="flex-1 flex flex-col">
                                <div className="p-2 border-b border-slate-700 flex justify-between items-center bg-slate-900/50">
                                    <div className="flex items-center gap-2">
                                        <Languages size={14} className="text-slate-400" />
                                        <select
                                            value={language}
                                            onChange={(e) => setLanguage(e.target.value as any)}
                                            className="bg-transparent text-xs text-white outline-none cursor-pointer hover:text-blue-300"
                                        >
                                            <option value="python">Python</option>
                                            <option value="rust">Rust</option>
                                            <option value="c">C</option>
                                        </select>
                                    </div>
                                    <div className="flex gap-2">
                                        <button onClick={handleCopyCode} title="Copy Code" className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white"><Copy size={14} /></button>
                                        <button onClick={handleDownload} title="Download File" className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white"><Download size={14} /></button>
                                    </div>
                                </div>
                                <div className="flex-1">
                                    <Editor
                                        height="100%"
                                        defaultLanguage="python"
                                        language={language === 'rust' ? 'rust' : language === 'c' ? 'c' : 'python'}
                                        value={generatedCode}
                                        theme="vs-dark"
                                        options={{ readOnly: true, minimap: { enabled: false }, fontSize: 13, scrollBeyondLastLine: false }}
                                    />
                                </div>
                            </div>
                        )}

                        {/* PREVIEW TAB (Game Stage) */}
                        {activeRightTab === 'preview' && (
                            <div className="flex-1 flex flex-col bg-black relative">
                                <div className="absolute top-2 right-2 z-10 flex gap-2">
                                    <button onClick={() => { startGame(); showStatus('Restarting game...'); }} className="bg-green-600/80 hover:bg-green-500 p-1.5 rounded-full backdrop-blur">
                                        <RefreshCw size={14} className="text-white" />
                                    </button>
                                </div>
                                <GameCanvas
                                    nodes={nodes}
                                    currentNodeId={currentSceneNodeId}
                                    variables={gameVariables}
                                    advanceStory={advanceStory}
                                    handleChoice={handleGameChoice}
                                />
                            </div>
                        )}

                        {/* CONSOLE TAB */}
                        {activeRightTab === 'console' && (
                            <div className="flex-1 bg-[#0d1117] p-2 font-mono text-xs overflow-auto text-green-300 whitespace-pre-wrap">
                                <div className="text-slate-500 mb-2 border-b border-slate-800 pb-1">Output Terminal >_</div>
                                {executionOutput || (
                                    <div className="text-slate-600 italic">
                                        Run code to see output here...
                                        <br />
                                        <br />
                                        supports: print(), errors, exit codes
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Hidden Input for generic modals */}
            <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept=".json"
                onChange={handleLoadProject}
            />

            {/* Modals Overlay (Shortcuts, Code Input, Generic Input) */}
            {/* Shortcuts Modal */}
            {showShortcuts && (
                <div className="absolute inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm">
                    <div className="bg-slate-800 rounded-lg p-4 w-80 shadow-2xl border border-slate-700">
                        <div className="flex justify-between items-center mb-3 border-b border-slate-700 pb-2">
                            <h3 className="font-bold flex items-center gap-2"><Keyboard size={16} /> Shortcuts</h3>
                            <button onClick={() => setShowShortcuts(false)} className="text-slate-400 hover:text-white"><X size={16} /></button>
                        </div>
                        <div className="text-sm space-y-2">
                            <div className="flex justify-between"><span>Ctrl+C</span><span className="text-slate-400">Copy code</span></div>
                            <div className="flex justify-between"><span>Ctrl+S</span><span className="text-slate-400">Download .py</span></div>
                            <div className="flex justify-between"><span>Ctrl+Z</span><span className="text-slate-400">Undo</span></div>
                            <div className="flex justify-between"><span>Ctrl+Delete</span><span className="text-slate-400">Clear all</span></div>
                            <div className="flex justify-between"><span>Escape</span><span className="text-slate-400">Close modal</span></div>
                        </div>
                    </div>
                </div>
            )}

            {/* Code Input Modal */}
            {showCodeInput && (
                <div className="absolute inset-0 bg-black/80 flex items-center justify-center p-8 z-50 backdrop-blur-sm">
                    <div className="bg-slate-800 rounded-lg w-full max-w-2xl flex flex-col gap-0 overflow-hidden shadow-2xl border border-slate-700">
                        <div className="flex justify-between items-center p-4 bg-slate-900 border-b border-slate-700">
                            <h2 className="text-lg font-bold flex items-center gap-2 text-blue-400">
                                <Code size={20} /> Code to Visual
                            </h2>
                            <button onClick={() => setShowCodeInput(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
                        </div>
                        <div className="p-4 flex-1">
                            <textarea
                                value={inputCode}
                                onChange={(e) => setInputCode(e.target.value)}
                                placeholder="Paste Python code here..."
                                className="w-full h-64 bg-[#0d1117] border border-slate-700 rounded p-4 font-mono text-sm text-gray-300 resize-none focus:outline-none focus:border-blue-500"
                            />
                        </div>
                        <div className="flex justify-end gap-2 p-4 bg-slate-900 border-t border-slate-700">
                            <button onClick={() => setShowCodeInput(false)} className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 text-sm">Cancel</button>
                            <button onClick={handleCodeToVisual} disabled={isGenerating}
                                className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500 flex items-center gap-2 text-sm font-bold shadow-lg shadow-blue-900/20">
                                {isGenerating ? <RefreshCw className="animate-spin" size={16} /> : <ArrowLeftRight size={16} />}
                                Convert to Nodes
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Generic Input Modal */}
            {isModalOpen && (
                <div className="absolute inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm">
                    <div className="bg-slate-800 rounded-lg p-5 w-96 shadow-2xl border border-slate-700 transform transition-all scale-100">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="font-bold text-white flex items-center gap-2 text-lg">{modalTitle}</h3>
                            <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white transition-colors"><X size={18} /></button>
                        </div>
                        <input
                            type="text"
                            value={modalInputValue}
                            onChange={(e) => setModalInputValue(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && modalCallback) {
                                    modalCallback(modalInputValue);
                                    setIsModalOpen(false);
                                }
                            }}
                            autoFocus
                            placeholder={modalPlaceholder}
                            className="w-full bg-slate-900 border border-slate-600 rounded-md p-3 text-sm text-white focus:outline-none focus:border-blue-500 placeholder-slate-500 shadow-inner"
                        />
                        <div className="flex justify-end gap-2 mt-4">
                            <button onClick={() => setIsModalOpen(false)} className="px-4 py-2 bg-slate-700 rounded-md hover:bg-slate-600 text-sm text-white transition-colors">Cancel</button>
                            <button
                                onClick={() => {
                                    if (modalCallback) {
                                        modalCallback(modalInputValue);
                                        setIsModalOpen(false);
                                    }
                                }}
                                className="px-4 py-2 bg-blue-600 rounded-md hover:bg-blue-500 text-sm text-white transition-colors font-medium shadow-lg shadow-blue-900/20"
                            >
                                Confirm
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <style jsx global>{`
                .btn-node {
                    @apply w-full p-2 bg-slate-800 hover:bg-slate-700 rounded text-left flex items-center gap-2 transition-colors text-xs border border-transparent hover:border-slate-600 text-slate-300 hover:text-white;
                }
                /* Custom Scrollbar */
                ::-webkit-scrollbar {
                    width: 6px;
                    height: 6px;
                }
                ::-webkit-scrollbar-track {
                    background: #1e293b; 
                }
                ::-webkit-scrollbar-thumb {
                    background: #475569; 
                    border-radius: 3px;
                }
                ::-webkit-scrollbar-thumb:hover {
                    background: #64748b; 
                }
            `}</style>
        </div>
    );
}


