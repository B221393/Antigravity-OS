export type Language = 'ja' | 'en'

export type Surface = 'turf' | 'dirt'

export interface RaceConditions {
  title: string
  location: string
  surface: Surface
  distance: number // meters
  weather: 'sunny' | 'cloudy' | 'rainy'
  trackState: 'fast' | 'good' | 'yielding' | 'sloppy'
  temperature: number // Celsius
  humidity: number // %
  windSpeed: number // km/h
  raceClass: 'G1' | 'G2' | 'G3' | 'Listed' | 'Allowance'
}

export interface HorseEntry {
  id: string
  name: string
  jockey: string
  trainer: string
  age: number
  weight: number
  draw: number
  recentForm: number[] // finishing positions
  speedFigure: number // 0-110
  stamina: number // 0-100
  breakSpeed: number // 0-100
  closingKick: number // 0-100
  surfacePreference: Surface | 'both'
  runningStyle: 'front-runner' | 'stalker' | 'closer'
  restDays: number
  odds: number // decimal odds
  notes?: string
}

export interface HorseScore {
  horse: HorseEntry
  baseScore: number
  adjustments: {
    surface: number
    weather: number
    rest: number
    draw: number
    styleFit: number
    momentum: number
  }
  total: number
  normalized: number
  projectedTime: number
  confidence: 'high' | 'medium' | 'low'
  strategy: string
}
