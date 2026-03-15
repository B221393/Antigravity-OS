import type { PersonaData } from "../types/persona";

export const INITIAL_PERSONA: PersonaData = {
    profile: {
        name: "あなた (Digital Twin)",
        university: "広島大学",
        department: "工学部 第一類 (機械・輸送・材料・エネルギー系)",
        location: "兵庫県 網干駅周辺",
        photoUrl: "",
    },
    attributes: {
        strengths: ["論理的結合力", "完成度への執着", "思考の言語化"],
        weaknesses: ["内なるカオス (制御対象)", "心配性"],
        values: [
            "思考のOS化 (認識の拡張)",
            "世界とのインターフェース創造",
            "自己の常時アップデート"
        ],
        skills: ["Python", "Engineering", "EGO OS Development"],
    },
    episodes: [
        {
            id: "1",
            title: "EGO OSの開発",
            description: "「理想の自分」を物理現実にマッピングするため、自己分析からタスク管理までを行う統合システム『EGO』を自作。思考の種を拾い上げ、システムとして実装し続けることで、「自ら作ったシステムの中で自己を更新する」という哲学を体現している。",
            tags: ["Self-Update", "Engineering", "Vision"],
            impact: 10
        },
        {
            id: "2",
            title: "研究室での課題解決",
            description: "実験装置の不具合を、粘り強く原因究明して解決した経験。現象をロジカルに分解し、再構築する「エンジニアリング思考」は、編集者としてコンテンツを構成する力にも通じている。",
            tags: ["Research", "Problem Solving"],
            impact: 8
        },
        {
            id: "3",
            title: "AIの本質的理解 (鳥と飛行機)",
            description: "AIを「思考のアウトソーシング」ではなく、「認識の拡張ツール（飛行機）」として捉えている。鳥（人間）の本質的な「飛ぶ（考える）」価値は失われないとし、AIと共存しながら、人間独自の文脈編集力を発揮するスタンスを持つ。",
            tags: ["AI Philosophy", "Modern Values"],
            impact: 9
        }
    ],
    gaps: []
};
