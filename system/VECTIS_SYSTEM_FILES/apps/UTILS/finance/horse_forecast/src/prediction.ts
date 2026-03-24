import type { HorseEntry, HorseScore, RaceConditions } from './types'

const SURFACE_WEIGHT: Record<'turf' | 'dirt', Record<'front-runner' | 'stalker' | 'closer', number>> =
  {
    turf: {
      'front-runner': 0.95,
      stalker: 1,
      closer: 1.05,
    },
    dirt: {
      'front-runner': 1.05,
      stalker: 1,
      closer: 0.95,
    },
  }

const TRACK_STATE_BONUS: Record<RaceConditions['trackState'], number> = {
  fast: 1.03,
  good: 1,
  yielding: 0.97,
  sloppy: 0.95,
}

const CONFIDENCE_THRESHOLDS = {
  high: 0.32,
  medium: 0.22,
}

export function buildPredictionReport(
  race: RaceConditions,
  horses: HorseEntry[],
): { ranked: HorseScore[]; narrative: string } {
  if (!horses.length) {
    return { ranked: [], narrative: '' }
  }

  const scores = horses.map((horse) => evaluateHorse(horse, race))
  const total = scores.reduce((acc, item) => acc + Math.max(item.total, 0), 0) || 1

  const normalized = scores
    .map((entry) => ({
      ...entry,
      normalized: Number((Math.max(entry.total, 0) / total).toFixed(3)),
    }))
    .sort((a, b) => b.total - a.total)

  return {
    ranked: normalized,
    narrative: summarizeNarrative(normalized, race),
  }
}

function evaluateHorse(horse: HorseEntry, race: RaceConditions): HorseScore {
  const recentMomentum = horse.recentForm.reduce((acc, placing) => acc + (6 - placing), 0)
  const surfaceAffinity =
    horse.surfacePreference === 'both' || horse.surfacePreference === race.surface ? 1 : 0.92
  const weatherPenalty = race.weather === 'rainy' && race.surface === 'turf' ? 0.97 : 1
  const restAdjustment =
    horse.restDays < 10 ? 0.96 : horse.restDays > 45 ? 0.93 : 1.02 // prefer 2〜6 weeks
  const drawAdjustment = race.surface === 'turf' ? 1 - Math.abs(horse.draw - 4) * 0.01 : 1
  const styleFit = SURFACE_WEIGHT[race.surface][horse.runningStyle]

  const baseScore =
    horse.speedFigure * 0.45 +
    horse.stamina * 0.2 +
    horse.breakSpeed * 0.15 +
    horse.closingKick * 0.12 +
    recentMomentum * 1.5

  const adjustments = {
    surface: surfaceAffinity,
    weather: weatherPenalty,
    rest: restAdjustment,
    draw: drawAdjustment,
    styleFit,
    momentum: 1 + recentMomentum * 0.01,
  }

  const total =
    baseScore *
    adjustments.surface *
    adjustments.weather *
    adjustments.rest *
    adjustments.draw *
    adjustments.styleFit *
    adjustments.momentum *
    TRACK_STATE_BONUS[race.trackState]

  const projectedTime = Number((110 - total * 0.03 + race.distance / 400).toFixed(2))
  const normalizedConfidence = total / 200

  return {
    horse,
    baseScore: Number(baseScore.toFixed(1)),
    adjustments,
    total: Number(total.toFixed(2)),
    normalized: 0,
    projectedTime,
    confidence: deriveConfidence(normalizedConfidence),
    strategy: buildStrategyLabel(horse, race),
  }
}

function deriveConfidence(value: number): HorseScore['confidence'] {
  if (value >= CONFIDENCE_THRESHOLDS.high) return 'high'
  if (value >= CONFIDENCE_THRESHOLDS.medium) return 'medium'
  return 'low'
}

function buildStrategyLabel(horse: HorseEntry, race: RaceConditions): string {
  const isValue = horse.odds > 4 && horse.speedFigure > 98
  const isMomentum = horse.recentForm.slice(0, 2).every((p) => p <= 3)
  const surfaceMatch =
    horse.surfacePreference === 'both' || horse.surfacePreference === race.surface

  if (isValue && surfaceMatch) return 'Value + surface specialist'
  if (isMomentum) return 'Momentum play / 上昇気流'
  if (horse.runningStyle === 'front-runner') return '押し切り期待'
  return '穴候補・展開待ち'
}

function summarizeNarrative(scores: HorseScore[], race: RaceConditions): string {
  const [leader, challenger] = scores
  if (!leader) return ''

  const leaderText = `${leader.horse.name} shows a composite index of ${leader.total}, leveraging ${
    race.surface === 'turf' ? 'closing power' : 'gate speed'
  }.`

  if (!challenger) {
    return `${leaderText} Field depth is limited, so focus on weather + paddock cues.`
  }

  return `${leaderText} ${challenger.horse.name} stays within ${
    (leader.total - challenger.total).toFixed(1)
  } pts thanks to ${challenger.horse.runningStyle}. Pace bias will decide the final order.`
}
