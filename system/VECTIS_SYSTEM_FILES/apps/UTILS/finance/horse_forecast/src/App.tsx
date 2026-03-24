import { useMemo, useState } from 'react'
import './App.css'
import { uiCopy } from './i18n'
import { buildPredictionReport } from './prediction'
import type { HorseEntry, HorseScore, Language, RaceConditions } from './types'

const createSampleRace = (): RaceConditions => ({
  title: '天皇賞 (秋)',
  location: '東京競馬場',
  surface: 'turf',
  distance: 2000,
  weather: 'sunny',
  trackState: 'fast',
  temperature: 21,
  humidity: 48,
  windSpeed: 9,
  raceClass: 'G1',
})

const createSampleHorses = (): HorseEntry[] => [
  {
    id: 'solaris',
    name: 'ソラリスアーク',
    jockey: '川田将雅',
    trainer: '友道康夫',
    age: 5,
    weight: 58,
    draw: 4,
    recentForm: [1, 2, 2],
    speedFigure: 106,
    stamina: 92,
    breakSpeed: 88,
    closingKick: 95,
    surfacePreference: 'turf',
    runningStyle: 'stalker',
    restDays: 35,
    odds: 3.8,
    notes: '府中2000m巧者',
  },
  {
    id: 'aqua',
    name: 'アクアダンサー',
    jockey: '横山武史',
    trainer: '宮田敬介',
    age: 4,
    weight: 57,
    draw: 2,
    recentForm: [3, 1, 5],
    speedFigure: 101,
    stamina: 87,
    breakSpeed: 91,
    closingKick: 89,
    surfacePreference: 'both',
    runningStyle: 'front-runner',
    restDays: 24,
    odds: 5.4,
    notes: '道悪でも粘れる先行型',
  },
  {
    id: 'meteora',
    name: 'メテオラライン',
    jockey: 'C. ルメール',
    trainer: '国枝栄',
    age: 6,
    weight: 58,
    draw: 8,
    recentForm: [4, 3, 1],
    speedFigure: 103,
    stamina: 95,
    breakSpeed: 79,
    closingKick: 97,
    surfacePreference: 'turf',
    runningStyle: 'closer',
    restDays: 52,
    odds: 7.1,
    notes: '上がり勝負に強い差し馬',
  },
]

const roadmap = [
  { sport: 'Horse Racing', status: 'LIVE', detail: '馬場・脚質適性とフォーム指数を統合' },
  { sport: 'Boat Racing', status: 'IN DESIGN', detail: 'モーター素性 + ピット離れで加点' },
  { sport: 'Baseball', status: '2025 Q1', detail: '先発 vs 打線マッチアップ指標を導入' },
  { sport: 'Soccer', status: '2025 Q2', detail: 'xG/xGA + 日程混雑の疲労モデル' },
]

const createEmptyHorse = (): HorseEntry => ({
  id: Math.random().toString(36).slice(2, 9),
  name: '',
  jockey: '',
  trainer: '',
  age: 4,
  weight: 56,
  draw: 1,
  recentForm: [5, 5, 5],
  speedFigure: 95,
  stamina: 80,
  breakSpeed: 80,
  closingKick: 80,
  surfacePreference: 'turf',
  runningStyle: 'stalker',
  restDays: 28,
  odds: 10,
})

function App() {
  const [language, setLanguage] = useState<Language>('ja')
  const [race, setRace] = useState<RaceConditions>(createSampleRace)
  const [horses, setHorses] = useState<HorseEntry[]>(createSampleHorses)
  const [report, setReport] = useState<{ ranked: HorseScore[]; narrative: string }>(() =>
    buildPredictionReport(race, horses),
  )

  const t = uiCopy[language]
  const numberFormat = useMemo(
    () =>
      new Intl.NumberFormat(language === 'ja' ? 'ja-JP' : 'en-US', {
        maximumFractionDigits: 1,
      }),
    [language],
  )

  const percentFormat = useMemo(
    () =>
      new Intl.NumberFormat(language === 'ja' ? 'ja-JP' : 'en-US', {
        style: 'percent',
        maximumFractionDigits: 1,
      }),
    [language],
  )

  const handleRaceChange = <K extends keyof RaceConditions>(field: K, value: RaceConditions[K]) => {
    setRace((prev: RaceConditions) => ({ ...prev, [field]: value }))
  }

  const handleHorseChange = <K extends keyof HorseEntry>(
    index: number,
    field: K,
    value: HorseEntry[K],
  ) => {
    setHorses((prev: HorseEntry[]) =>
      prev.map((horse, idx) => (idx === index ? { ...horse, [field]: value } : horse)),
    )
  }

  const addHorse = () => setHorses((prev) => [...prev, createEmptyHorse()])
  const removeHorse = (index: number) =>
    setHorses((prev) => prev.filter((_, idx) => idx !== index))

  const runForecast = () => setReport(buildPredictionReport(race, horses))
  const resetSample = () => {
    const nextRace = createSampleRace()
    const nextHorses = createSampleHorses()
    setRace(nextRace)
    setHorses(nextHorses)
    setReport(buildPredictionReport(nextRace, nextHorses))
  }

  const landscape = useMemo(() => report.ranked.slice(0, 3), [report])

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Sports Forecasting Studio</p>
          <h1>{t.title}</h1>
          <p className="subtitle">{t.subtitle}</p>
        </div>
        <div className="language-switcher">
          <label>{t.languageLabel}</label>
          <div>
            <button
              className={language === 'ja' ? 'toggle active' : 'toggle'}
              onClick={() => setLanguage('ja')}
            >
              日本語
            </button>
            <button
              className={language === 'en' ? 'toggle active' : 'toggle'}
              onClick={() => setLanguage('en')}
            >
              English
            </button>
          </div>
        </div>
      </header>

      <section className="cards-grid">
        <article className="panel">
          <header>
            <h2>{t.raceCard}</h2>
            <span className="tag">{race.raceClass}</span>
          </header>
          <div className="form-grid">
            <label>
              {t.placeholders.raceTitle}
              <input
                value={race.title}
                onChange={(e) => handleRaceChange('title', e.target.value)}
              />
            </label>
            <label>
              {t.placeholders.location}
              <input
                value={race.location}
                onChange={(e) => handleRaceChange('location', e.target.value)}
              />
            </label>
            <label>
              Distance (m)
              <input
                type="number"
                value={race.distance}
                onChange={(e) => handleRaceChange('distance', Number(e.target.value))}
              />
            </label>
            <label>
              Surface
              <select
                value={race.surface}
                onChange={(e) => handleRaceChange('surface', e.target.value as RaceConditions['surface'])}
              >
                <option value="turf">Turf</option>
                <option value="dirt">Dirt</option>
              </select>
            </label>
            <label>
              Weather
              <select
                value={race.weather}
                onChange={(e) => handleRaceChange('weather', e.target.value as RaceConditions['weather'])}
              >
                <option value="sunny">Sunny</option>
                <option value="cloudy">Cloudy</option>
                <option value="rainy">Rainy</option>
              </select>
            </label>
            <label>
              Track
              <select
                value={race.trackState}
                onChange={(e) =>
                  handleRaceChange('trackState', e.target.value as RaceConditions['trackState'])
                }
              >
                <option value="fast">Fast</option>
                <option value="good">Good</option>
                <option value="yielding">Yielding</option>
                <option value="sloppy">Sloppy</option>
              </select>
            </label>
            <label>
              {t.metrics.temperature} °C
              <input
                type="number"
                value={race.temperature}
                onChange={(e) => handleRaceChange('temperature', Number(e.target.value))}
              />
            </label>
            <label>
              {t.metrics.humidity} %
              <input
                type="number"
                value={race.humidity}
                onChange={(e) => handleRaceChange('humidity', Number(e.target.value))}
              />
            </label>
            <label>
              {t.metrics.wind} km/h
              <input
                type="number"
                value={race.windSpeed}
                onChange={(e) => handleRaceChange('windSpeed', Number(e.target.value))}
              />
            </label>
          </div>
        </article>

        <article className="panel">
          <header className="panel-header">
            <h2>{t.horseCard}</h2>
            <button className="ghost" onClick={addHorse}>
              + {t.addHorse}
            </button>
          </header>

          {horses.map((horse, index) => (
            <div key={horse.id} className="horse-card">
              <div className="horse-card__head">
                <input
                  className="horse-name"
                  placeholder={t.placeholders.horseName}
                  value={horse.name}
                  onChange={(e) => handleHorseChange(index, 'name', e.target.value)}
                />
                <span>#{horse.draw}</span>
              </div>
              <div className="horse-grid">
                <label>
                  {t.placeholders.jockey}
                  <input
                    value={horse.jockey}
                    onChange={(e) => handleHorseChange(index, 'jockey', e.target.value)}
                  />
                </label>
                <label>
                  {t.placeholders.trainer}
                  <input
                    value={horse.trainer}
                    onChange={(e) => handleHorseChange(index, 'trainer', e.target.value)}
                  />
                </label>
                <label>
                  Age
                  <input
                    type="number"
                    value={horse.age}
                    onChange={(e) => handleHorseChange(index, 'age', Number(e.target.value))}
                  />
                </label>
                <label>
                  Weight (kg)
                  <input
                    type="number"
                    value={horse.weight}
                    onChange={(e) => handleHorseChange(index, 'weight', Number(e.target.value))}
                  />
                </label>
                <label>
                  Draw
                  <input
                    type="number"
                    value={horse.draw}
                    onChange={(e) => handleHorseChange(index, 'draw', Number(e.target.value))}
                  />
                </label>
                <label>
                  Odds
                  <input
                    type="number"
                    value={horse.odds}
                    onChange={(e) => handleHorseChange(index, 'odds', Number(e.target.value))}
                  />
                </label>
                <label>
                  Speed Fig
                  <input
                    type="number"
                    value={horse.speedFigure}
                    onChange={(e) => handleHorseChange(index, 'speedFigure', Number(e.target.value))}
                  />
                </label>
                <label>
                  Stamina
                  <input
                    type="number"
                    value={horse.stamina}
                    onChange={(e) => handleHorseChange(index, 'stamina', Number(e.target.value))}
                  />
                </label>
                <label>
                  Break
                  <input
                    type="number"
                    value={horse.breakSpeed}
                    onChange={(e) => handleHorseChange(index, 'breakSpeed', Number(e.target.value))}
                  />
                </label>
                <label>
                  Kick
                  <input
                    type="number"
                    value={horse.closingKick}
                    onChange={(e) => handleHorseChange(index, 'closingKick', Number(e.target.value))}
                  />
                </label>
                <label>
                  Rest (days)
                  <input
                    type="number"
                    value={horse.restDays}
                    onChange={(e) => handleHorseChange(index, 'restDays', Number(e.target.value))}
                  />
                </label>
                <label>
                  Style
                  <select
                    value={horse.runningStyle}
                    onChange={(e) =>
                      handleHorseChange(index, 'runningStyle', e.target.value as HorseEntry['runningStyle'])
                    }
                  >
                    <option value="front-runner">Front</option>
                    <option value="stalker">Stalker</option>
                    <option value="closer">Closer</option>
                  </select>
                </label>
                <label>
                  Surface
                  <select
                    value={horse.surfacePreference}
                    onChange={(e) =>
                      handleHorseChange(index, 'surfacePreference', e.target.value as HorseEntry['surfacePreference'])
                    }
                  >
                    <option value="turf">Turf</option>
                    <option value="dirt">Dirt</option>
                    <option value="both">Both</option>
                  </select>
                </label>
                <label>
                  Recent form (1-5-3)
                  <input
                    value={horse.recentForm.join('-')}
                    onChange={(e) =>
                      handleHorseChange(
                        index,
                        'recentForm',
                        e.target.value
                          .split('-')
                          .map((value) => Number(value) || 5)
                          .slice(0, 3),
                      )
                    }
                  />
                </label>
              </div>
              <div className="horse-actions">
                <button className="ghost" onClick={() => removeHorse(index)}>
                  Remove
                </button>
              </div>
            </div>
          ))}
        </article>
      </section>

      <div className="actions">
        <button onClick={runForecast}>{t.predict}</button>
        <button className="ghost" onClick={resetSample}>
          {t.reset}
        </button>
      </div>

      <section className="panel panel--forecast">
        <header>
          <h2>{t.forecastTitle}</h2>
          <p className="narrative">{report.narrative}</p>
        </header>
        {report.ranked.length === 0 ? (
          <p>{t.forecastsEmpty}</p>
        ) : (
          <div className="forecast-grid">
            {report.ranked.map((score, idx) => (
              <div key={score.horse.id} className="forecast-card">
                <div className="forecast-head">
                  <span className="rank">#{idx + 1}</span>
                  <div>
                    <p className="horse-name">{score.horse.name}</p>
                    <p className="meta">
                      {score.horse.jockey} · {score.horse.trainer}
                    </p>
                  </div>
                  <span className={`confidence ${score.confidence}`}>{score.confidence}</span>
                </div>
                <dl>
                  <div>
                    <dt>{t.metrics.score}</dt>
                    <dd>{score.total}</dd>
                  </div>
                  <div>
                    <dt>{t.metrics.probability}</dt>
                    <dd>{percentFormat.format(score.normalized)}</dd>
                  </div>
                  <div>
                    <dt>{t.metrics.projectedTime}</dt>
                    <dd>{score.projectedTime}s</dd>
                  </div>
                </dl>
                <p className="strategy">
                  {t.metrics.strategy}: {score.strategy}
                </p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="panel panel--roadmap">
        <header>
          <h2>{t.roadmapTitle}</h2>
          <p>{t.roadmapHint}</p>
        </header>
        <ul>
          {roadmap.map((item) => (
            <li key={item.sport}>
              <div>
                <strong>{item.sport}</strong>
                <span className="status">{item.status}</span>
              </div>
              <p>{item.detail}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel panel--highlights">
        <header>
          <h2>Key Signals / 注目インサイト</h2>
        </header>
        <ul>
          {landscape.map((entry) => (
            <li key={entry.horse.id}>
              <strong>{entry.horse.name}</strong> — {entry.strategy} /{' '}
              {t.metrics.probability}: {percentFormat.format(entry.normalized)} /{' '}
              {t.metrics.score}: {numberFormat.format(entry.total)}
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

export default App
