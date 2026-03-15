'use client';

import React from 'react';
import { VisualNode } from '@/lib/types';

interface GameCanvasProps {
    nodes: VisualNode[]; // All nodes, for runtime lookup
    currentNodeId: string | null;
    variables: Record<string, any>;
    advanceStory: (choiceId?: string) => void;
    handleChoice: (choiceId: string) => void;
}

const GameCanvas: React.FC<GameCanvasProps> = ({ nodes, currentNodeId, variables, advanceStory, handleChoice }) => {
    const currentNode = currentNodeId ? nodes.find(n => n.id === currentNodeId) : null;
    const speakerName = currentNode?.data.speaker || "???";
    const messageText = currentNode?.data.text || (currentNodeId ? "シナリオが終了しました。" : "ゲーム開始ノードがありません。");
    const choices = currentNode?.data.choices || [];

    // Debug info display
    const debugInfo = (
        <div className="absolute top-2 left-2 text-xs text-gray-500 bg-gray-900 bg-opacity-50 p-1 rounded z-10">
            <div>Current Node: {currentNodeId || 'None'}</div>
            <div>Variables: {JSON.stringify(variables)}</div>
            <div>Nodes: {nodes.length}</div>
        </div>
    );

    // If no current node, show a message or a start button
    if (!currentNodeId) {
        return (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 text-white font-serif antialiased">
                <div className="text-center">
                    <h2 className="text-3xl font-bold mb-4">ゲーム開始</h2>
                    <p className="text-lg mb-6">ゲーム開始ノードが見つからないか、ストーリーが終了しました。</p>
                    <button
                        onClick={() => advanceStory()} // Trigger advance story to try and find a start node
                        className="py-3 px-6 bg-green-600 hover:bg-green-700 rounded-md text-white font-semibold text-xl transition-colors duration-200"
                    >
                        ゲームを開始
                    </button>
                </div>
                {debugInfo}
            </div>
        );
    }

    return (
        <div className="absolute inset-0 flex flex-col bg-gray-900 text-white font-serif antialiased">
            {/* Background/Scene Area */}
            <div className="flex-1 relative flex items-center justify-center bg-cover bg-center"
                 style={{ backgroundImage: 'linear-gradient(to bottom, #2d3748, #1a202c)' }}> {/* Placeholder background */}
                {/* Visual elements for character/scene could go here eventually */}
                <h2 className="text-3xl font-bold text-gray-400">Game Scene</h2>
            </div>

            {/* Message Box */}
            <div className="relative w-full p-4 bg-gray-800 bg-opacity-80 backdrop-blur-sm border-t border-gray-700">
                {/* Speaker Name Box */}
                <div className="absolute -top-8 left-4 px-4 py-1 bg-blue-700 text-white text-lg font-bold rounded-t-lg shadow-md">
                    {speakerName}
                </div>
                {/* Message Text */}
                <p className="text-lg leading-relaxed mb-4 min-h-[4.5em]"> {/* min-h to prevent layout shift */}
                    {messageText}
                </p>

                {/* Choices */}
                {choices && choices.length > 0 ? (
                    <div className="flex flex-col gap-2">
                        {choices.map((choice: any, index: number) => ( // choice type might need more definition
                            <button
                                key={index} // Use index as key for now, as choice.id is not defined yet
                                onClick={() => handleChoice(choice.nextNode)} // Choice button should trigger handleChoice with its target node
                                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 rounded-md text-white font-semibold transition-colors duration-200"
                            >
                                {choice.text}
                            </button>
                        ))}
                    </div>
                ) : (
                    // Next Button (only if no choices are present)
                    <button
                        onClick={() => advanceStory()} // Advance story on click
                        className="absolute bottom-2 right-4 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md text-white font-semibold transition-colors duration-200"
                    >
                        次へ &raquo;
                    </button>
                )}
            </div>
            {debugInfo}
        </div>
    );
};

export default GameCanvas;
