'use client';

import { VisualNode, NodeData } from '@/lib/types';
import { Edge } from 'reactflow';

// Game state managed by the runtime
export interface GameState {
    currentNodeId: string | null;
    variables: Record<string, string | number | boolean>;
    history: string[];  // Stack of visited node IDs for backtracking
    isWaitingForChoice: boolean;
    isFinished: boolean;
}

// What the GameCanvas needs to render
export interface GameFrame {
    speaker: string;
    dialogue: string;
    choices: { id: string; text: string; targetNodeId?: string }[];
    bgImage: string;
    characters: { image: string; position: 'left' | 'center' | 'right' }[];
    isFinished: boolean;
}

const EMPTY_FRAME: GameFrame = {
    speaker: '',
    dialogue: '',
    choices: [],
    bgImage: '',
    characters: [],
    isFinished: false,
};

export class GameRuntime {
    private nodes: Map<string, VisualNode> = new Map();
    private edges: Edge[] = [];
    private state: GameState;
    private onFrameUpdate: (frame: GameFrame) => void;
    private currentBg: string = '';
    private currentChars: { image: string; position: 'left' | 'center' | 'right' }[] = [];

    constructor(
        nodes: VisualNode[],
        edges: Edge[],
        onFrameUpdate: (frame: GameFrame) => void
    ) {
        this.edges = edges;
        nodes.forEach(n => this.nodes.set(n.id, n));
        this.onFrameUpdate = onFrameUpdate;
        this.state = {
            currentNodeId: null,
            variables: {},
            history: [],
            isWaitingForChoice: false,
            isFinished: false,
        };
    }

    // Find the starting node
    start() {
        const startNode = Array.from(this.nodes.values()).find(
            n => n.data.realType === 'game_start' || n.type === 'game_start'
        );

        if (!startNode) {
            // Fallback: find a node with no incoming edges
            const targetIds = new Set(this.edges.map(e => e.target));
            const rootNode = Array.from(this.nodes.values()).find(n => !targetIds.has(n.id));
            if (rootNode) {
                this.state.currentNodeId = rootNode.id;
                this.processCurrentNode();
            } else {
                this.onFrameUpdate({
                    ...EMPTY_FRAME,
                    dialogue: 'エラー: 開始ノードが見つかりません。\n「Game Start」ノードを追加してください。',
                    speaker: 'System',
                });
            }
            return;
        }

        this.state.currentNodeId = startNode.id;
        this.processCurrentNode();
    }

    // Process the current node and emit a frame
    private processCurrentNode() {
        if (!this.state.currentNodeId) return;

        const node = this.nodes.get(this.state.currentNodeId);
        if (!node) return;

        const data = node.data;
        const nodeType = data.realType || node.type;

        this.state.history.push(this.state.currentNodeId);

        switch (nodeType) {
            case 'game_start':
                this.advance(); // Just pass through
                break;

            case 'dialogue':
                this.onFrameUpdate({
                    speaker: data.speaker || '???',
                    dialogue: data.dialogue || data.value || '',
                    choices: [],
                    bgImage: this.currentBg,
                    characters: [...this.currentChars],
                    isFinished: false,
                });
                break;

            case 'choice':
                this.state.isWaitingForChoice = true;
                const choices = data.choices || [
                    { id: 'a', text: '選択肢A' },
                    { id: 'b', text: '選択肢B' },
                ];
                // Find edges from this node for each choice
                const outEdges = this.edges.filter(e => e.source === this.state.currentNodeId);
                const enrichedChoices = choices.map((c, i) => ({
                    ...c,
                    targetNodeId: outEdges[i]?.target || c.targetNodeId,
                }));

                this.onFrameUpdate({
                    speaker: data.speaker || '',
                    dialogue: data.dialogue || data.label || '選択してください',
                    choices: enrichedChoices,
                    bgImage: this.currentBg,
                    characters: [...this.currentChars],
                    isFinished: false,
                });
                break;

            case 'set_var':
                this.state.variables[data.gameVarName || data.variable || 'x'] =
                    data.gameVarValue || data.value || '';
                this.advance();
                break;

            case 'if_var': {
                const varName = data.gameVarName || data.variable || '';
                const varValue = this.state.variables[varName];
                const expectedValue = data.gameVarValue || data.value || '';
                const outEdgesIf = this.edges.filter(e => e.source === this.state.currentNodeId);

                // First edge = true, second edge = false
                if (String(varValue) === String(expectedValue) && outEdgesIf.length > 0) {
                    this.state.currentNodeId = outEdgesIf[0].target;
                } else if (outEdgesIf.length > 1) {
                    this.state.currentNodeId = outEdgesIf[1].target;
                } else {
                    this.advance();
                    return;
                }
                this.processCurrentNode();
                break;
            }

            case 'scene_bg':
                this.currentBg = data.bgImage || data.value || '';
                this.advance();
                break;

            case 'show_char':
                this.currentChars = [
                    ...this.currentChars.filter(c => c.position !== (data.charPosition || 'center')),
                    { image: data.charImage || data.value || '', position: data.charPosition || 'center' },
                ];
                this.advance();
                break;

            case 'game_end':
                this.state.isFinished = true;
                this.onFrameUpdate({
                    ...EMPTY_FRAME,
                    dialogue: data.dialogue || '— END —',
                    speaker: 'System',
                    isFinished: true,
                    bgImage: this.currentBg,
                });
                break;

            default:
                // Unknown node, just advance
                this.advance();
                break;
        }
    }

    // Move to the next connected node
    advance() {
        if (this.state.isFinished) return;

        const outEdges = this.edges.filter(e => e.source === this.state.currentNodeId);
        if (outEdges.length > 0) {
            this.state.currentNodeId = outEdges[0].target;
            this.processCurrentNode();
        } else {
            // No more nodes
            this.state.isFinished = true;
            this.onFrameUpdate({
                ...EMPTY_FRAME,
                dialogue: '— END —',
                speaker: 'System',
                isFinished: true,
                bgImage: this.currentBg,
            });
        }
    }

    // Handle choice selection
    selectChoice(targetNodeId: string) {
        if (!this.state.isWaitingForChoice) return;
        this.state.isWaitingForChoice = false;
        this.state.currentNodeId = targetNodeId;
        this.processCurrentNode();
    }

    // Get current state (for debugging)
    getState(): GameState {
        return { ...this.state };
    }

    getVariables(): Record<string, string | number | boolean> {
        return { ...this.state.variables };
    }
}
