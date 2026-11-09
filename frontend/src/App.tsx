import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Brain, 
  Briefcase, 
  Zap, 
  Database, 
  BookOpen, 
  MapPin, 
  DollarSign, 
  CheckCircle, 
  RefreshCw, 
  Search, 
  Terminal, 
  ChevronRight,
  Sparkles,
  Sliders
} from 'lucide-react';

interface OverviewData {
  total_listings: number;
  median_lpa: number;
  median_inr: number;
  avg_lpa: number;
  avg_inr: number;
  remote_percentage: number;
  top_skill: string;
  hub_distribution: Record<string, number>;
}

interface Metadata {
  job_families: string[];
  experience_tiers: string[];
  indian_hubs: string[];
  skill_taxonomy: Record<string, Record<string, string[]>>;
  all_skills: string[];
}

interface SkillData {
  skill: string;
  category: string;
  demand_count: number;
  avg_salary_lpa: number;
  avg_salary_inr: number;
  remote_pct: number;
}

interface TierData {
  experience_tier: string;
  job_count: number;
  avg_salary_lpa: number;
  min_salary_lpa: number;
  max_salary_lpa: number;
  avg_salary_inr: number;
}

interface HubData {
  tech_hub: string;
  job_count: number;
  avg_salary_lpa: number;
  avg_salary_inr: number;
  remote_pct: number;
}

interface MatrixData {
  columns: string[];
  rows: Array<Record<string, any>>;
}

interface JobRecord {
  id: number;
  title: string;
  company: string;
  job_family: string;
  experience_tier: string;
  salary_min_lpa: number;
  salary_max_lpa: number;
  salary_avg_lpa: number;
  salary_avg_inr: number;
  region: string;
  is_remote: boolean;
  skills: string[];
}

interface PredictionResult {
  predicted_median_lpa: number;
  salary_bracket_low_lpa: number;
  salary_bracket_high_lpa: number;
  predicted_median_inr: number;
  salary_bracket_low_inr: number;
  salary_bracket_high_inr: number;
  confidence_margin_lpa: number;
  total_skill_premium_lpa: number;
  total_skill_premium_inr: number;
  skill_breakdown_lpa: Record<string, number>;
  model_used: string;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'predictor' | 'jobs' | 'stream' | 'sql' | 'taxonomy'>('dashboard');
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [metadata, setMetadata] = useState<Metadata | null>(null);
  const [topSkills, setTopSkills] = useState<SkillData[]>([]);
  const [tiers, setTiers] = useState<TierData[]>([]);
  const [hubs, setHubs] = useState<HubData[]>([]);
  const [matrix, setMatrix] = useState<MatrixData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Filter States for Dashboard & Jobs
  const [selectedHub, setSelectedHub] = useState<string>('All Tech Hubs');
  const [selectedFamily, setSelectedFamily] = useState<string>('All Job Families');
  const [selectedTier, setSelectedTier] = useState<string>('All Tiers');
  const [jobSearch, setJobSearch] = useState<string>('');
  const [jobsList, setJobsList] = useState<JobRecord[]>([]);

  // ML Predictor States
  const [predFamily, setPredFamily] = useState<string>('Machine Learning & AI');
  const [predTier, setPredTier] = useState<string>('Senior (6-8 yrs)');
  const [predHub, setPredHub] = useState<string>('Bengaluru (Bangalore)');
  const [predYears, setPredYears] = useState<number>(6);
  const [predRemote, setPredRemote] = useState<boolean>(false);
  const [predSkills, setPredSkills] = useState<string[]>(['Python', 'PyTorch', 'LLMs / Generative AI', 'Kubernetes']);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [isPredicting, setIsPredicting] = useState<boolean>(false);

  // Streaming State
  const [streamCount, setStreamCount] = useState<number>(10);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [streamStatus, setStreamStatus] = useState<string>('');

  // SQL State
  const [sqlQuery, setSqlQuery] = useState<string>(
    "SELECT job_family, COUNT(*) AS total_postings, ROUND(AVG(salary_avg_lpa), 2) AS avg_lpa FROM cleaned_jobs GROUP BY job_family ORDER BY avg_lpa DESC;"
  );
  const [sqlResults, setSqlResults] = useState<{ columns: string[]; rows: any[]; row_count: number } | null>(null);
  const [sqlError, setSqlError] = useState<string>('');

  // Load initial backend data
  const fetchData = async () => {
    try {
      const [ovRes, metaRes, skillsRes, tiersRes, hubsRes, matRes] = await Promise.all([
        fetch('/api/overview').then(r => r.json()),
        fetch('/api/metadata').then(r => r.json()),
        fetch('/api/top-skills?limit=20').then(r => r.json()),
        fetch('/api/compensation-by-tier').then(r => r.json()),
        fetch('/api/compensation-by-hub').then(r => r.json()),
        fetch('/api/supply-demand-matrix').then(r => r.json())
      ]);

      setOverview(ovRes);
      setMetadata(metaRes);
      setTopSkills(skillsRes);
      setTiers(tiersRes);
      setHubs(hubsRes);
      setMatrix(matRes);
    } catch (err) {
      console.error('Failed to load API data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Fetch Jobs list
  const fetchJobs = async () => {
    try {
      let url = `/api/jobs?limit=50`;
      if (selectedHub !== 'All Tech Hubs') url += `&hub=${encodeURIComponent(selectedHub)}`;
      if (selectedFamily !== 'All Job Families') url += `&family=${encodeURIComponent(selectedFamily)}`;
      if (selectedTier !== 'All Tiers') url += `&tier=${encodeURIComponent(selectedTier)}`;
      if (jobSearch) url += `&search=${encodeURIComponent(jobSearch)}`;

      const res = await fetch(url).then(r => r.json());
      setJobsList(res.jobs || []);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [selectedHub, selectedFamily, selectedTier, jobSearch]);

  // Run ML Prediction
  const runPrediction = async () => {
    setIsPredicting(true);
    try {
      const res = await fetch('/api/predict-salary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_family: predFamily,
          experience_tier: predTier,
          region: predHub,
          is_remote: predRemote,
          years_min: predYears,
          skills: predSkills
        })
      });
      const data = await res.json();
      setPrediction(data);
    } catch (err) {
      console.error('Prediction failed:', err);
    } finally {
      setIsPredicting(false);
    }
  };

  // Run default prediction on mount once metadata is ready
  useEffect(() => {
    runPrediction();
  }, [predFamily, predTier, predHub, predRemote, predYears, predSkills]);

  // Trigger Real-Time Stream
  const triggerStream = async () => {
    setIsStreaming(true);
    setStreamStatus('Ingesting real-time Indian tech postings into SQLite...');
    try {
      const res = await fetch('/api/ingest-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: streamCount })
      });
      const data = await res.json();
      setStreamStatus(`✓ ${data.message}`);
      await fetchData();
      await fetchJobs();
    } catch (err) {
      setStreamStatus('Stream ingestion failed.');
    } finally {
      setIsStreaming(false);
    }
  };

  // Run SQL
  const executeSQL = async () => {
    setSqlError('');
    try {
      const res = await fetch('/api/sql-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: sqlQuery })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'SQL Query failed');
      }
      const data = await res.json();
      setSqlResults(data);
    } catch (err: any) {
      setSqlError(err.message);
      setSqlResults(null);
    }
  };

  const toggleSkill = (skill: string) => {
    if (predSkills.includes(skill)) {
      setPredSkills(predSkills.filter(s => s !== skill));
    } else {
      setPredSkills([...predSkills, skill]);
    }
  };

  return (
    <div>
      {/* App Header */}
      <header className="app-header">
        <div className="header-container">
          <div className="brand">
            <span className="brand-flag">🇮🇳</span>
            <div>
              <div className="brand-title">Indian Tech Market Intelligence & Salary Predictor</div>
              <div className="brand-sub">Bengaluru • Hyderabad • Pune • Delhi NCR • Mumbai • Chennai (2025–2026)</div>
            </div>
          </div>

          <nav className="nav-tabs">
            <button 
              className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              <TrendingUp size={16} /> Market Dynamics
            </button>
            <button 
              className={`nav-tab ${activeTab === 'predictor' ? 'active' : ''}`}
              onClick={() => setActiveTab('predictor')}
            >
              <Brain size={16} /> ML Salary Predictor
            </button>
            <button 
              className={`nav-tab ${activeTab === 'jobs' ? 'active' : ''}`}
              onClick={() => setActiveTab('jobs')}
            >
              <Briefcase size={16} /> Live Jobs ({overview?.total_listings || 0})
            </button>
            <button 
              className={`nav-tab ${activeTab === 'stream' ? 'active' : ''}`}
              onClick={() => setActiveTab('stream')}
            >
              <Zap size={16} /> Real-Time Ingest
            </button>
            <button 
              className={`nav-tab ${activeTab === 'sql' ? 'active' : ''}`}
              onClick={() => setActiveTab('sql')}
            >
              <Database size={16} /> SQL Console
            </button>
            <button 
              className={`nav-tab ${activeTab === 'taxonomy' ? 'active' : ''}`}
              onClick={() => setActiveTab('taxonomy')}
            >
              <BookOpen size={16} /> Taxonomy
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {/* KPI Cards */}
        <section className="kpi-grid">
          <div className="kpi-card">
            <div>
              <div className="kpi-label">Active Indian Tech Postings</div>
              <div className="kpi-val">{overview ? overview.total_listings.toLocaleString() : '---'}</div>
              <div className="kpi-sub">Across 6 Major Tech Hubs</div>
            </div>
            <div className="kpi-icon"><Briefcase size={22} /></div>
          </div>

          <div className="kpi-card accent">
            <div>
              <div className="kpi-label">Median Annual CTC (India)</div>
              <div className="kpi-val">₹{overview?.median_lpa || '24.5'} LPA</div>
              <div className="kpi-sub">₹{overview ? (overview.median_inr).toLocaleString() : '---'} INR / year</div>
            </div>
            <div className="kpi-icon"><DollarSign size={22} /></div>
          </div>

          <div className="kpi-card amber">
            <div>
              <div className="kpi-label">Remote / WFH Roles</div>
              <div className="kpi-val">{overview?.remote_percentage || '32.0'}%</div>
              <div className="kpi-sub">Pan-India Flexibility</div>
            </div>
            <div className="kpi-icon"><MapPin size={22} /></div>
          </div>

          <div className="kpi-card purple">
            <div>
              <div className="kpi-label">#1 In-Demand Competency</div>
              <div className="kpi-val" style={{ fontSize: '1.5rem' }}>{overview?.top_skill || 'Python'}</div>
              <div className="kpi-sub">Market Taxonomy Leader</div>
            </div>
            <div className="kpi-icon"><Sparkles size={22} /></div>
          </div>
        </section>

        {/* TAB 1: DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div>
            <div className="filter-bar">
              <div className="filter-group">
                <label className="filter-label">Indian Tech Hub</label>
                <select 
                  className="filter-select"
                  value={selectedHub}
                  onChange={e => setSelectedHub(e.target.value)}
                >
                  <option value="All Tech Hubs">All Tech Hubs</option>
                  {metadata?.indian_hubs.map(h => <option key={h} value={h}>{h}</option>)}
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label">Job Family</label>
                <select 
                  className="filter-select"
                  value={selectedFamily}
                  onChange={e => setSelectedFamily(e.target.value)}
                >
                  <option value="All Job Families">All Job Families</option>
                  {metadata?.job_families.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label">Seniority Tier</label>
                <select 
                  className="filter-select"
                  value={selectedTier}
                  onChange={e => setSelectedTier(e.target.value)}
                >
                  <option value="All Tiers">All Tiers</option>
                  {metadata?.experience_tiers.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(600px, 1fr))', gap: '24px', marginBottom: '24px' }}>
              {/* Top Demanded Skills */}
              <div className="card">
                <div className="card-title"><TrendingUp size={18} color="#2563eb" /> Top 20 In-Demand Technical Competencies in India</div>
                <div className="card-desc">Ranked by frequency in Indian listings, colored by average LPA.</div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {topSkills.map((s, idx) => {
                    const maxCount = Math.max(...topSkills.map(t => t.demand_count), 1);
                    const pct = (s.demand_count / maxCount) * 100;
                    return (
                      <div key={s.skill}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', fontWeight: 600, marginBottom: '4px' }}>
                          <span>{idx + 1}. {s.skill} <span className="badge badge-slate">{s.category}</span></span>
                          <span style={{ color: '#2563eb' }}>₹{s.avg_salary_lpa} LPA <span style={{ color: '#64748b', fontWeight: 400 }}>({s.demand_count} jobs)</span></span>
                        </div>
                        <div className="bar-track">
                          <div 
                            className="bar-fill" 
                            style={{ 
                              width: `${pct}%`, 
                              background: s.avg_salary_lpa > 30 ? 'linear-gradient(90deg, #3b82f6, #8b5cf6)' : '#3b82f6' 
                            }} 
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Experience Tier Progression */}
              <div className="card">
                <div className="card-title"><Sliders size={18} color="#10b981" /> SDE Compensation Dynamics by Experience Tier</div>
                <div className="card-desc">Progression ladder from Fresher (SDE-1) to Principal / Director in India (LPA).</div>

                <div className="data-table-wrapper" style={{ marginTop: '16px' }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Experience Tier</th>
                        <th>Postings</th>
                        <th>Min LPA</th>
                        <th>Median CTC</th>
                        <th>Max LPA</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tiers.map(t => (
                        <tr key={t.experience_tier}>
                          <td style={{ fontWeight: 600 }}>{t.experience_tier}</td>
                          <td><span className="badge badge-blue">{t.job_count}</span></td>
                          <td>₹{t.min_salary_lpa} LPA</td>
                          <td style={{ fontWeight: 700, color: '#1e3a8a' }}>₹{t.avg_salary_lpa} LPA</td>
                          <td style={{ color: '#059669', fontWeight: 600 }}>₹{t.max_salary_lpa} LPA</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Hub Breakdown */}
                <div style={{ marginTop: '28px' }}>
                  <div className="card-title" style={{ fontSize: '0.98rem' }}><MapPin size={16} color="#f59e0b" /> Compensation across Major Indian Tech Hubs</div>
                  <div className="data-table-wrapper" style={{ marginTop: '12px' }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Tech Hub</th>
                          <th>Openings</th>
                          <th>Mean CTC</th>
                          <th>Remote %</th>
                        </tr>
                      </thead>
                      <tbody>
                        {hubs.map(h => (
                          <tr key={h.tech_hub}>
                            <td style={{ fontWeight: 600 }}>{h.tech_hub}</td>
                            <td>{h.job_count}</td>
                            <td style={{ fontWeight: 700, color: '#2563eb' }}>₹{h.avg_salary_lpa} LPA</td>
                            <td><span className="badge badge-amber">{h.remote_pct}%</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>

            {/* Matrix Card */}
            {matrix && (
              <div className="card">
                <div className="card-title"><Database size={18} color="#8b5cf6" /> Talent Compensation Matrix across Indian Job Families (₹ LPA)</div>
                <div className="card-desc">Comprehensive cross-sectional compensation benchmarks.</div>
                
                <div className="data-table-wrapper">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Job Family</th>
                        {matrix.columns.map(col => <th key={col}>{col}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {matrix.rows.map((row, idx) => (
                        <tr key={idx}>
                          <td style={{ fontWeight: 600 }}>{row.job_family}</td>
                          {matrix.columns.map(col => (
                            <td key={col} style={{ fontWeight: row[col] > 40 ? 700 : 500, color: row[col] > 40 ? '#1e3a8a' : '#334155' }}>
                              ₹{row[col]} LPA
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: ML SALARY PREDICTOR */}
        {activeTab === 'predictor' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.25fr', gap: '24px' }}>
            {/* Parameters Form */}
            <div className="card">
              <div className="card-title"><Brain size={18} color="#2563eb" /> Profile & Role Parameters</div>
              <div className="card-desc">Configure your technical profile to evaluate expected Indian CTC.</div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="filter-group">
                  <label className="filter-label">Job Family</label>
                  <select className="filter-select" value={predFamily} onChange={e => setPredFamily(e.target.value)}>
                    {metadata?.job_families.map(f => <option key={f} value={f}>{f}</option>)}
                  </select>
                </div>

                <div className="filter-group">
                  <label className="filter-label">Experience Tier</label>
                  <select className="filter-select" value={predTier} onChange={e => setPredTier(e.target.value)}>
                    {metadata?.experience_tiers.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>

                <div className="filter-group">
                  <label className="filter-label">Indian Tech Hub</label>
                  <select className="filter-select" value={predHub} onChange={e => setPredHub(e.target.value)}>
                    {metadata?.indian_hubs.map(h => <option key={h} value={h}>{h}</option>)}
                  </select>
                </div>

                <div className="filter-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <label className="filter-label">Specific Experience</label>
                    <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>{predYears} Years</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="20" 
                    value={predYears} 
                    onChange={e => setPredYears(Number(e.target.value))}
                    style={{ width: '100%', cursor: 'pointer' }}
                  />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>Remote / WFH Position</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Pan-India remote flexibility</div>
                  </div>
                  <input 
                    type="checkbox" 
                    checked={predRemote} 
                    onChange={e => setPredRemote(e.target.checked)}
                    style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                  />
                </div>

                {/* Skill Pickers */}
                <div style={{ marginTop: '8px' }}>
                  <label className="filter-label">Select Core Technical Competencies</label>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Click to add/remove skills from prediction model.</div>
                  
                  {metadata && Object.entries(metadata.skill_taxonomy).map(([cat, skills]) => (
                    <div key={cat} style={{ marginBottom: '14px' }}>
                      <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#475569', marginBottom: '6px' }}>{cat}</div>
                      <div className="skills-selector-grid">
                        {Object.keys(skills).map(skill => {
                          const isSelected = predSkills.includes(skill);
                          return (
                            <button
                              key={skill}
                              type="button"
                              className={`skill-pill ${isSelected ? 'selected' : ''}`}
                              onClick={() => toggleSkill(skill)}
                            >
                              {skill} {isSelected ? '✓' : '+'}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Prediction Output */}
            <div>
              {prediction ? (
                <div>
                  <div className="salary-hero">
                    <div className="salary-hero-sub">PREDICTED COMPENSATION BRACKET (2025–2026 CTC)</div>
                    <div className="salary-hero-bracket">₹{prediction.salary_bracket_low_lpa} – ₹{prediction.salary_bracket_high_lpa} LPA</div>
                    <div className="salary-hero-median">
                      Estimated Median CTC: <strong>₹{prediction.predicted_median_lpa} LPA</strong> (₹{prediction.predicted_median_inr.toLocaleString()} INR / year)
                    </div>
                    <div className="salary-hero-meta">
                      <span>Engine: {prediction.model_used}</span>
                      <span>•</span>
                      <span>Margin: ±₹{prediction.confidence_margin_lpa} LPA</span>
                    </div>
                  </div>

                  <div className="card" style={{ marginBottom: '24px' }}>
                    <div className="card-title"><Sparkles size={18} color="#2563eb" /> Valuation Breakdown & Skill Premiums in India</div>
                    <div className="card-desc">Marginal annual compensation value added by your selected technical stack.</div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                      <div style={{ padding: '16px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-md)' }}>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>TOTAL SKILL PREMIUM</div>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#10b981' }}>+₹{prediction.total_skill_premium_lpa} LPA</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>+₹{prediction.total_skill_premium_inr.toLocaleString()} INR / yr</div>
                      </div>

                      <div style={{ padding: '16px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-md)' }}>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>SKILLS EVALUATED</div>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#2563eb' }}>{predSkills.length} Competencies</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Verified across Indian market</div>
                      </div>
                    </div>

                    {Object.keys(prediction.skill_breakdown_lpa).length > 0 && (
                      <div className="data-table-wrapper">
                        <table className="data-table">
                          <thead>
                            <tr>
                              <th>Technical Skill</th>
                              <th>Estimated Premium (LPA)</th>
                              <th>Annual INR Valuation</th>
                            </tr>
                          </thead>
                          <tbody>
                            {Object.entries(prediction.skill_breakdown_lpa).map(([skill, val]) => (
                              <tr key={skill}>
                                <td style={{ fontWeight: 600 }}>{skill}</td>
                                <td style={{ color: '#10b981', fontWeight: 700 }}>+₹{val} LPA</td>
                                <td style={{ color: '#334155' }}>+₹{(val * 100000).toLocaleString()} INR</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
                  <RefreshCw className="animate-spin" size={32} color="#2563eb" style={{ margin: '0 auto 16px' }} />
                  <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>Calculating Salary Prediction...</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: LIVE JOBS EXPLORER */}
        {activeTab === 'jobs' && (
          <div className="card">
            <div className="card-title"><Briefcase size={18} color="#2563eb" /> Active Indian Tech Postings Database</div>
            <div className="card-desc">Browse cleansed listings across top Indian unicorns, GCCs, and tech giants.</div>

            <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
              <div style={{ position: 'relative', flex: 2 }}>
                <Search size={18} style={{ position: 'absolute', left: '12px', top: '11px', color: '#94a3b8' }} />
                <input 
                  type="text"
                  placeholder="Search by role, company (e.g. Razorpay, Swiggy, Google) or skill..."
                  className="filter-input"
                  style={{ width: '100%', paddingLeft: '38px' }}
                  value={jobSearch}
                  onChange={e => setJobSearch(e.target.value)}
                />
              </div>

              <select className="filter-select" style={{ flex: 1 }} value={selectedHub} onChange={e => setSelectedHub(e.target.value)}>
                <option value="All Tech Hubs">All Tech Hubs</option>
                {metadata?.indian_hubs.map(h => <option key={h} value={h}>{h}</option>)}
              </select>

              <select className="filter-select" style={{ flex: 1 }} value={selectedFamily} onChange={e => setSelectedFamily(e.target.value)}>
                <option value="All Job Families">All Job Families</option>
                {metadata?.job_families.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>

            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Title & Company</th>
                    <th>Job Family</th>
                    <th>Seniority</th>
                    <th>Tech Hub</th>
                    <th>Compensation (LPA)</th>
                    <th>Required Skills</th>
                  </tr>
                </thead>
                <tbody>
                  {jobsList.map(j => (
                    <tr key={j.id}>
                      <td>
                        <div style={{ fontWeight: 700, color: '#1e293b' }}>{j.title}</div>
                        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{j.company}</div>
                      </td>
                      <td><span className="badge badge-slate">{j.job_family}</span></td>
                      <td><span className="badge badge-blue">{j.experience_tier}</span></td>
                      <td>
                        <div>{j.region}</div>
                        {j.is_remote && <span className="badge badge-green" style={{ marginTop: '2px' }}>Remote</span>}
                      </td>
                      <td style={{ fontWeight: 700, color: '#1e3a8a' }}>
                        ₹{j.salary_min_lpa} – ₹{j.salary_max_lpa} LPA
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '300px' }}>
                          {j.skills.slice(0, 4).map(s => <span key={s} className="badge badge-purple">{s}</span>)}
                          {j.skills.length > 4 && <span className="badge badge-slate">+{j.skills.length - 4}</span>}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: REAL-TIME STREAM */}
        {activeTab === 'stream' && (
          <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <div className="card-title"><Zap size={18} color="#f59e0b" /> Real-Time Indian Market Ingestion Engine</div>
            <div className="card-desc">Simulate continuous stream feeds from Indian product startups, MNC GCCs, and unicorn job boards.</div>

            <div style={{ padding: '24px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-md)', marginBottom: '20px' }}>
              <div style={{ fontWeight: 700, marginBottom: '6px' }}>Incremental Stream Generator</div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
                Generates realistic unstructured listings with Indian CTC bands, extracts NLP features, associates relational skills, and commits to SQLite.
              </p>

              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                <label style={{ fontSize: '0.88rem', fontWeight: 600 }}>Batch Size:</label>
                <select 
                  className="filter-select" 
                  value={streamCount} 
                  onChange={e => setStreamCount(Number(e.target.value))}
                >
                  <option value={5}>5 Postings</option>
                  <option value={10}>10 Postings</option>
                  <option value={25}>25 Postings</option>
                  <option value={50}>50 Postings</option>
                </select>

                <button 
                  className="btn btn-primary"
                  onClick={triggerStream}
                  disabled={isStreaming}
                >
                  {isStreaming ? <RefreshCw className="animate-spin" size={16} /> : <Zap size={16} />}
                  {isStreaming ? 'Ingesting Stream...' : 'Ingest Real-Time Stream Now'}
                </button>
              </div>

              {streamStatus && (
                <div style={{ padding: '10px 14px', background: '#ecfdf5', color: '#065f46', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', fontWeight: 600 }}>
                  {streamStatus}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 5: SQL QUERY CONSOLE */}
        {activeTab === 'sql' && (
          <div className="card">
            <div className="card-title"><Terminal size={18} color="#2563eb" /> Interactive SQL Analytics Console</div>
            <div className="card-desc">Execute direct analytical queries against the normalized SQLite relational schema.</div>

            <div style={{ display: 'flex', gap: '8px', marginBottom: '14px', flexWrap: 'wrap' }}>
              <button 
                className="btn btn-outline" 
                style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                onClick={() => setSqlQuery("SELECT s.name as skill, COUNT(j.id) as jobs, ROUND(AVG(j.salary_avg_lpa), 2) as avg_lpa FROM skills s JOIN job_skills js ON s.id = js.skill_id JOIN cleaned_jobs j ON js.job_id = j.id GROUP BY s.name HAVING jobs >= 5 ORDER BY avg_lpa DESC LIMIT 10;")}
              >
                Top 10 Paying Skills in India
              </button>

              <button 
                className="btn btn-outline" 
                style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                onClick={() => setSqlQuery("SELECT region as tech_hub, COUNT(*) as postings, ROUND(AVG(salary_avg_lpa), 2) as avg_ctc_lpa, ROUND(AVG(is_remote)*100, 1) as remote_pct FROM cleaned_jobs GROUP BY region ORDER BY avg_ctc_lpa DESC;")}
              >
                Compensation by Indian Tech Hub
              </button>

              <button 
                className="btn btn-outline" 
                style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                onClick={() => setSqlQuery("SELECT experience_tier, COUNT(*) as roles, ROUND(AVG(salary_avg_lpa), 2) as avg_lpa, ROUND(AVG(skill_count), 1) as avg_skills FROM cleaned_jobs GROUP BY experience_tier ORDER BY avg_lpa ASC;")}
              >
                SDE Experience Tier Ladder
              </button>
            </div>

            <textarea 
              rows={5}
              style={{ width: '100%', fontFamily: 'JetBrains Mono, monospace', fontSize: '0.88rem', padding: '12px', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', marginBottom: '14px' }}
              value={sqlQuery}
              onChange={e => setSqlQuery(e.target.value)}
            />

            <button className="btn btn-primary" onClick={executeSQL} style={{ marginBottom: '20px' }}>
              <Terminal size={16} /> Execute SQL Query
            </button>

            {sqlError && (
              <div style={{ padding: '12px', background: '#fef2f2', color: '#991b1b', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', marginBottom: '16px' }}>
                {sqlError}
              </div>
            )}

            {sqlResults && (
              <div>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#64748b', marginBottom: '8px' }}>Returned {sqlResults.row_count} rows.</div>
                <div className="data-table-wrapper">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {sqlResults.columns.map(col => <th key={col}>{col}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {sqlResults.rows.map((row, idx) => (
                        <tr key={idx}>
                          {sqlResults.columns.map(col => <td key={col}>{row[col] !== null ? String(row[col]) : 'NULL'}</td>)}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 6: TAXONOMY & DOCUMENTATION */}
        {activeTab === 'taxonomy' && (
          <div className="card">
            <div className="card-title"><BookOpen size={18} color="#2563eb" /> 120+ Technical Competencies Master Taxonomy</div>
            <div className="card-desc">Curated taxonomy of modern frameworks, cloud tools, and AI architectures recognized by the NLP pipeline.</div>

            {metadata && Object.entries(metadata.skill_taxonomy).map(([cat, skills]) => (
              <div key={cat} style={{ marginBottom: '24px' }}>
                <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1e293b', marginBottom: '10px' }}>{cat} ({Object.keys(skills).length} competencies)</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {Object.keys(skills).map(s => (
                    <span key={s} className="badge badge-blue" style={{ padding: '6px 10px', fontSize: '0.82rem' }}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
