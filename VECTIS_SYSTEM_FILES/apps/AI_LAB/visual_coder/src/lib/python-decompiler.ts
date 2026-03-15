/**
 * Python Decompiler - Converts Python code to Visual Nodes
 * Uses AI to parse Python AST and generate node structures
 */

import { Edge } from 'reactflow';
import { VisualNode } from './types';

interface DecompileResult {
    nodes: VisualNode[];
    edges: Edge[];
    warnings?: string[]; // Add optional warnings
}

/**
 * Simple Python statement parser (client-side heuristic)
 * For complex parsing, use the /api/decompile endpoint
 */
export function decompilePython(code: string): DecompileResult {
    const lines = code.split('\n').filter(line => line.trim() && !line.trim().startsWith('#'));
    const nodes: VisualNode[] = [];
    const edges: Edge[] = [];
    const warnings: string[] = []; // Initialize warnings array

    let yPos = 50;
    const xPos = 150;
    const yStep = 100;

    // Add Start node
    const startNode: VisualNode = {
        id: 'start-1',
        type: 'start',
        position: { x: xPos, y: yPos },
        data: { label: 'Start', realType: 'start' }
    };
    nodes.push(startNode);
    yPos += yStep;

    let prevNodeId = 'start-1';
    let nodeCounter = 0;

    // Parse each line
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        nodeCounter++;
        const nodeId = `node-${nodeCounter}-${Date.now()}`;
        let newNode: VisualNode | null = null;

        // Detect import statements
        if (trimmed.startsWith('import ') || trimmed.startsWith('from ')) {
            newNode = {
                id: nodeId,
                type: 'default',
                position: { x: xPos, y: yPos },
                data: {
                    label: `Import: ${trimmed.replace(/^(import|from)\s+/, '').split(' ')[0]}`,
                    code: trimmed,
                    realType: 'import'
                }
            };
        }
        // Detect print statements
        else if (trimmed.startsWith('print(')) {
            const match = trimmed.match(/print\((.+)\)$/);
            const value = match ? match[1] : '""';
            newNode = {
                id: nodeId,
                type: 'default',
                position: { x: xPos, y: yPos },
                data: {
                    label: 'Print',
                    value: value,
                    realType: 'print'
                }
            };
        }
        // Detect variable assignments
        else if (trimmed.includes('=') && !trimmed.includes('==')) {
            const [varPart, ...valueParts] = trimmed.split('=');
            const varName = varPart.trim();
            const varValue = valueParts.join('=').trim();
            newNode = {
                id: nodeId,
                type: 'default',
                position: { x: xPos, y: yPos },
                data: {
                    label: `Var: ${varName}`,
                    variable: varName,
                    value: varValue,
                    realType: 'var'
                }
            };
        }
        // Detect function definitions
        else if (trimmed.startsWith('def ')) {
            const match = trimmed.match(/def\s+(\w+)\s*\(/);
            const funcName = match ? match[1] : 'function';
            newNode = {
                id: nodeId,
                type: 'default',
                position: { x: xPos, y: yPos },
                data: {
                    label: `Func: ${funcName}`,
                    code: trimmed,
                    realType: 'function'
                }
            };
        }
        // Detect if statements
        else if (trimmed.startsWith('if ')) {
            const condition = trimmed.replace(/^if\s+/, '').replace(/:$/, '');
            newNode = {
                id: nodeId,
                type: 'default',
                position: { x: xPos, y: yPos },
                data: {
                    label: `If: ${condition.substring(0, 20)}...`,
                    condition: condition,
                    realType: 'if'
                }
            };
        }
        // Detect for loops
        else if (trimmed.startsWith('for ')) {
            newNode = {
                id: nodeId,
                type: 'default',
                position: { x: xPos, y: yPos },
                data: {
                    label: `Loop: ${trimmed.substring(4, 24)}...`,
                    code: trimmed,
                    realType: 'for'
                }
            };
        }
        // Generic Python block (or unrecognized statement)
        else {
            // Add a warning if the line is very generic/ambiguous
            if (trimmed.length > 0 && !trimmed.includes('=') && !trimmed.includes('(') && !trimmed.includes('def') && !trimmed.includes('if') && !trimmed.includes('for') && !trimmed.includes('import')) {
                warnings.push(`Line "${trimmed.substring(0, 30)}..." was not recognized as a specific pattern and treated as generic Python. Its visual representation might be limited.`);
            }
            newNode = {
                id: nodeId,
                type: 'default',
                position: { x: xPos, y: yPos },
                data: {
                    label: trimmed.substring(0, 20) + (trimmed.length > 20 ? '...' : ''),
                    code: trimmed,
                    realType: 'python'
                }
            };
        }

        if (newNode) {
            nodes.push(newNode);

            // Create edge from previous node
            edges.push({
                id: `edge-${prevNodeId}-${nodeId}`,
                source: prevNodeId,
                target: nodeId
            });

            prevNodeId = nodeId;
            yPos += yStep;
        }
    }

    return { nodes, edges, warnings }; // Include warnings in the return
}

/**
 * Decompile using AI (server-side)
 */
export async function decompilePythonWithAI(code: string): Promise<DecompileResult> {
    try {
        const response = await fetch('/api/decompile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });

        if (!response.ok) {
            throw new Error('AI decompilation failed');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('AI Decompile error, falling back to heuristic:', error);
        // Fallback to client-side parser
        return decompilePython(code);
    }
}
