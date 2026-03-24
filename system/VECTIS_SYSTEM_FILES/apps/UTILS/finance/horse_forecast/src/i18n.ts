import type { Language } from './types'

export const uiCopy: Record<
  Language,
  {
    title: string
    subtitle: string
    raceCard: string
    horseCard: string
    addHorse: string
    predict: string
    reset: string
    forecastTitle: string
    forecastsEmpty: string
    roadmapTitle: string
    roadmapHint: string
    languageLabel: string
    metrics: {
      temperature: string
      humidity: string
      wind: string
      score: string
      probability: string
      projectedTime: string
      confidence: string
      strategy: string
    }
    placeholders: {
      raceTitle: string
      location: string
      horseName: string
      jockey: string
      trainer: string
    }
  }
> = {
  ja: {
    title: 'Horse Intelligence Lab',
    subtitle:
      '競馬からスタートし、今後すべてのメジャースポーツへ広げる拡張性を備えた予想エンジンの実験場です。',
    raceCard: 'レース条件',
    horseCard: '出走馬プロフィール',
    addHorse: '馬を追加',
    predict: '予想計算',
    reset: 'サンプルに戻す',
    forecastTitle: 'リアルタイム予想レポート',
    forecastsEmpty: '対象データがありません。出走馬を追加してください。',
    roadmapTitle: 'マルチスポーツ対応ロードマップ',
    roadmapHint:
      '競艇・野球・サッカーなど他競技にも同じ分析エンジンを展開できる構造になっています。',
    languageLabel: '言語 / Language',
    metrics: {
      temperature: '気温',
      humidity: '湿度',
      wind: '風速',
      score: '指数',
      probability: '勝率',
      projectedTime: '想定ゴールタイム',
      confidence: '確信度',
      strategy: '推奨戦略',
    },
    placeholders: {
      raceTitle: '天皇賞 (秋)',
      location: '東京競馬場',
      horseName: 'ソラシティ',
      jockey: '川田',
      trainer: '友道厩舎',
    },
  },
  en: {
    title: 'Horse Intelligence Lab',
    subtitle:
      'An extensible forecasting lab that starts with horse racing and can expand to every major sport.',
    raceCard: 'Race Conditions',
    horseCard: 'Horse Profiles',
    addHorse: 'Add Horse',
    predict: 'Run Forecast',
    reset: 'Revert to Sample',
    forecastTitle: 'Live Forecast Report',
    forecastsEmpty: 'No entries yet. Please add at least one horse.',
    roadmapTitle: 'Roadmap toward Multi-Sport Coverage',
    roadmapHint:
      'The data + scoring architecture is ready to plug in boat racing, baseball, soccer, and more.',
    languageLabel: 'Language / 言語',
    metrics: {
      temperature: 'Temp',
      humidity: 'Humidity',
      wind: 'Wind',
      score: 'Score',
      probability: 'Win %',
      projectedTime: 'Projected Finish',
      confidence: 'Confidence',
      strategy: 'Strategy',
    },
    placeholders: {
      raceTitle: 'Autumn Tenno Sho',
      location: 'Tokyo Racecourse',
      horseName: 'Sky City',
      jockey: 'Kawada',
      trainer: 'Tomomichi Stable',
    },
  },
}
