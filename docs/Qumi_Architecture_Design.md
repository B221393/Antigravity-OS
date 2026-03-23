# 統合思考OS（Qumi）システムアーキテクチャ図

このドキュメントは、Qumiの全体構成（フロントエンド、バックエンドエージェント、外部AI、データストア）のデータフローと各コンポーネントの関係性を可視化したものです。GitHub等でこのMarkdownを開くと、自動的に美しい図表としてレンダリングされます。

```mermaid
flowchart LR
    %% カラー定義（AWSの構成図に近いプロフェッショナルな配色）
    classDef userAccess fill:#ffffff,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5;
    classDef client fill:#f0f8ff,stroke:#0066cc,stroke-width:2px;
    classDef backend fill:#f5fffa,stroke:#00cc66,stroke-width:2px;
    classDef agent fill:#fff5ee,stroke:#ff6600,stroke-width:2px;
    classDef db fill:#f0f8ff,stroke:#6666cc,stroke-width:2px,shape:cylinder;
    classDef cloud fill:#fdf5e6,stroke:#cc0066,stroke-width:2px;

    User([👤 User / 面接官]):::userAccess

    %% エッジ・クライアント層（デプロイ済みUI）
    subgraph Client_Layer [Edge UI Layer / GitHub Pages]
        PWA[Qumi PWA\n(React Native Web)]:::client
        
        subgraph Core_Slots [12 Core OS Slots]
            direction TB
            UI_Memo[04 AI MEMO]
            UI_Daily[09 DAILY LOG]
            UI_LLM[05 LOCAL LLM]
            UI_Vision[06 VISION]
        end
        PWA --> Core_Slots
    end

    %% コアバックエンド層（ローカルサーバー/API）
    subgraph Core_Backend [Core Server / Local Network]
        direction TB
        API[🚀 FastAPI Server\n(Agent Router)]:::backend
        
        subgraph Agentic_Control [Agent & Automation Layer]
            direction TB
            MCP[MCP Protocol Server]:::agent
            SoulAgent[Soul Delegation Agent\n(Abstract Logic Layer)]:::agent
            BrowserCLI[Browser-Use CLI\n(Web Automation)]:::agent
        end
        
        subgraph Data_Storage [Local Encrypted Storage]
            direction TB
            VecDB[(AES-256\nVector Vault)]:::db
            JSONLog[(Daily Log\nJSON Store)]:::db
        end
    end

    %% クラウド層（外部プロバイダ）
    subgraph Cloud_Layer [External AI & Cloud]
        Gemini[Google Gemini 2.5\n/ Claude 3.5 Sonnet]:::cloud
        Web[🌐 Internet / Public Web]:::cloud
        GH[GitHub Actions\nCI/CD Pipeline]:::cloud
    end

    %% データフローと接続（矢印）
    User -->|Tap & Swipe\n(Bounce UI)| PWA
    Core_Slots -->|HTTP/WebSocket| API
    
    API <-->|Context Sync| MCP
    MCP <--> SoulAgent
    
    SoulAgent <-->|API Calls| Gemini
    SoulAgent <-->|RAG Query| VecDB
    SoulAgent -->|Execute CLI commands| BrowserCLI
    
    BrowserCLI -->|Automated Crawling| Web
    API -->|Write/Read Timeline| JSONLog
    
    GH -.->|Automated Deploy\n(gh-pages)| PWA

    %% 注釈
    note1>抽象レイヤーの本質: n8nのような視覚的ノード制御から、\nSoul Delegation Agent (LLM) へと委譲フローを移行。]
    SoulAgent -.-> note1
```

## アーキテクチャの解説（面接用ポイント）
1. **Edge UI Layer (Client)**: 
   - ユーザーが直接触れる「コロコロ転がる球体」や「すりガラス（Glassmorphism）」のUI設計を担保。
   - レスポンシブでスマホ（PWA）からPCブラウザまでシームレスに動作。
2. **Core Server (Backend)**: 
   - 送信された「思考（メモ）」をFastAPIが受け取り、MCP（Model Context Protocol）を介して非同期でエージェントへパスするハブ機能。
3. **Agent & Automation Layer**: 
   - `browser-use`によるブラウザ自己操作、及び魂をJSON化する論理エージェント。ここで**「問題のレイヤーを変えて解決する」**というエンジニアリングの真髄が実装されています。
