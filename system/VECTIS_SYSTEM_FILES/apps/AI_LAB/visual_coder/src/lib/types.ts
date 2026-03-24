
import { Node } from 'reactflow';

export type VisualNodeType =
    | 'start' | 'print' | 'var' | 'if' | 'for' | 'function' | 'import' | 'python'
    | 'while' | 'try' | 'list' | 'dict' | 'math' | 'compare' | 'class' | 'return' | 'comment'
    | 'cube' | 'sphere'
    // Game (Visual Novel) nodes
    | 'dialogue' | 'choice' | 'set_var' | 'if_var' | 'scene_bg' | 'show_char' | 'play_sfx' | 'game_start' | 'game_end';

export interface NodeData {
    label: string;
    code?: string;      // For raw Python blocks
    variable?: string;  // For Variable assignment
    value?: string;     // For Value or Print content
    condition?: string; // For IF/WHILE nodes
    operator?: string;  // For Math/Compare
    items?: string[];   // For List/Dict items (simplified)
    aiPrompt?: string;  // For AI nodes
    realType?: string;  // Fallback for UI default nodes
    // 3D Properties
    color?: string;
    size?: number;
    wireframe?: boolean;
    // Game (Visual Novel) Properties
    speaker?: string;       // Character name for dialogue
    dialogue?: string;      // Dialogue text
    choices?: { id: string; text: string; targetNodeId?: string }[];
    bgImage?: string;       // Background image URL/path
    charImage?: string;     // Character sprite URL/path
    charPosition?: 'left' | 'center' | 'right';
    sfxPath?: string;       // Sound effect path
    gameVarName?: string;   // Game variable name
    gameVarValue?: string;  // Game variable value
    onDelete?: () => void;
}

export type VisualNode = Node<NodeData>;
