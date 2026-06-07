import React, { useState, useEffect } from 'react';
import { AlertCircle, Navigation, ShieldAlert, CheckCircle2, TrendingUp, CloudRain, Map } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

interface SidebarProps {
  state: any;
  onRouteCalculated: (path: string[]) => void;
  routeDetails?: any;
}

export default function Sidebar({ state, onRouteCalculated, routeDetails }: SidebarProps) {
  const [activeTab, setActiveTab] = useState<'main' | 'insights'>('main');
  const [sourceId, setSourceId] = useState('');
  const [targetId, setTargetId] = useState('');
  const [loadingRoute, setLoadingRoute] = useState(false);
  const [insights, setInsights] = useState<any>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Derive metrics
  const nodes = state?.nodes || [];
  const alerts = state?.alerts || [];
  const totalCrowd = nodes.reduce((acc: number, n: any) => acc + n.current_crowd_count, 0) || 0;
  const bottlenecks = alerts.length || 0;

  // Watch for critical alerts to trigger Toast
  useEffect(() => {
    if (alerts && alerts.length > 0) {
      // Find critical alerts
      const critical = alerts.find((a: any) => a.message.includes('CRITICAL'));
      if (critical) {
        setToastMessage(critical.message);
        // Toast auto-hides after 5 seconds
        const timer = setTimeout(() => setToastMessage(null), 5000);
        return () => clearTimeout(timer);
      }
    }
  }, [alerts]);

  useEffect(() => {
    let apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';
    if (apiUrl.endsWith('/')) apiUrl = apiUrl.slice(0, -1);
    if (!apiUrl.endsWith('/api')) apiUrl = `${apiUrl}/api`;
    
    fetch(`${apiUrl}/insights`)
      .then(res => res.json())
      .then(data => {
        const chartData = data.historical_data.map((d: any) => ({
          name: d.Year.toString(),
          visitors: d.Total_Visitors / 1000000 
        }));
        chartData.push({ name: '2028 (AI)', visitors: data.prediction_2028 / 1000000 });
        setInsights({
          chartData: chartData,
          historical_risks: data.historical_risks || []
        });
      })
      .catch(console.error);
  }, []);

  const calculateRoute = async () => {
    if (!sourceId || !targetId) return;
    setLoadingRoute(true);
    try {
      let apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';
      if (apiUrl.endsWith('/')) apiUrl = apiUrl.slice(0, -1);
      if (!apiUrl.endsWith('/api')) apiUrl = `${apiUrl}/api`;
      
      const res = await fetch(`${apiUrl}/route?source_id=${sourceId}&target_id=${targetId}`);
      const data = await res.json();
      if (data.path) {
        onRouteCalculated(data.path);
      }
    } catch (e) {
      console.error(e);
    }
    setLoadingRoute(false);
  };

  // Sort nodes by max_capacity so the order remains stable (no jumping)
  const leaderboard = [...nodes].sort((a, b) => b.max_capacity - a.max_capacity).slice(0, 5);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', background: 'var(--bg-dark)' }}>
      
      {/* Header */}
      <div style={{ padding: '20px 20px 0 20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '4px' }}>Unified Control Room</h1>
        <p className="text-secondary font-mono" style={{ fontSize: '12px' }}>MAHAKUMBH CROWD ROUTING SYSTEM</p>
      </div>

      {/* CRITICAL TOAST — sits right below header in normal flow */}
      {toastMessage && (
        <div style={{
          margin: '12px 20px 0 20px',
          background: '#ff0055', color: '#fff', padding: '14px 16px', borderRadius: '8px',
          boxShadow: '0 0 20px rgba(255,0,85,0.5)', border: '2px solid #ffaaaa',
          display: 'flex', alignItems: 'center', gap: '12px', animation: 'pulse 1s infinite'
        }}>
          <AlertCircle size={28} style={{ flexShrink: 0 }} />
          <div style={{ fontWeight: 'bold', fontSize: '13px', lineHeight: '1.4' }}>{toastMessage}</div>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', marginTop: '20px', borderBottom: '1px solid #222' }}>
        <button 
          onClick={() => setActiveTab('main')}
          style={{ 
            flex: 1, padding: '12px', background: 'transparent', border: 'none', color: activeTab === 'main' ? '#00d4ff' : '#888',
            borderBottom: activeTab === 'main' ? '2px solid #00d4ff' : '2px solid transparent', cursor: 'pointer', fontWeight: 'bold'
          }}
        >
          <Map size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'text-bottom' }} />
          Live Operations
        </button>
        <button 
          onClick={() => setActiveTab('insights')}
          style={{ 
            flex: 1, padding: '12px', background: 'transparent', border: 'none', color: activeTab === 'insights' ? '#00d4ff' : '#888',
            borderBottom: activeTab === 'insights' ? '2px solid #00d4ff' : '2px solid transparent', cursor: 'pointer', fontWeight: 'bold'
          }}
        >
          <TrendingUp size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'text-bottom' }} />
          Historical Insights
        </button>
      </div>

      {/* Scrollable Content */}
      <div style={{ padding: '20px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        {activeTab === 'main' && (
          <>
            {/* Global Metrics */}
            <div className="glass-panel" style={{ padding: '16px', display: 'flex', justifyContent: 'space-between' }}>
              <div>
                <p className="text-secondary" style={{ fontSize: '12px' }}>TOTAL CROWD</p>
                <h2 className="text-cyan font-mono" style={{ fontSize: '28px' }}>{totalCrowd.toLocaleString()}</h2>
              </div>
              <div>
                <p className="text-secondary" style={{ fontSize: '12px' }}>ACTIVE BOTTLENECKS</p>
                <h2 className="font-mono" style={{ fontSize: '28px', color: bottlenecks > 0 ? '#ff0055' : 'var(--accent-cyan)' }}>
                  {bottlenecks}
                </h2>
              </div>
            </div>

            {/* Routing Tool */}
            <div className="glass-panel" style={{ padding: '16px' }}>
              <h3 style={{ fontSize: '16px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Navigation size={18} className="text-cyan" />
                Diversion Routing
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <select className="input-select" value={sourceId} onChange={e => setSourceId(e.target.value)}>
                  <option value="">Select Source Node...</option>
                  {nodes.map((n: any) => <option key={n.id} value={n.id}>{n.name}</option>)}
                </select>
                <select className="input-select" value={targetId} onChange={e => setTargetId(e.target.value)}>
                  <option value="">Select Target Node...</option>
                  {nodes.map((n: any) => <option key={n.id} value={n.id}>{n.name}</option>)}
                </select>
                <button className="btn-primary" onClick={calculateRoute} disabled={loadingRoute || !sourceId || !targetId}>
                  {loadingRoute ? 'Calculating...' : 'Calculate Safe Route'}
                </button>
                {routeDetails && (
                  <div style={{ marginTop: '10px', padding: '10px', background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: '4px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                      <span className="text-secondary">Safe Distance:</span>
                      <strong className="text-cyan">{routeDetails.distance}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span className="text-secondary">Estimated Time (Traffic):</span>
                      <strong className="text-cyan">{routeDetails.duration}</strong>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Stable Sector Overview */}
            <div className="glass-panel" style={{ padding: '16px' }}>
              <h3 style={{ fontSize: '16px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldAlert size={18} className="text-cyan" />
                Major Sectors Overview
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {leaderboard.length === 0 ? <p className="text-secondary" style={{fontSize: '12px'}}>No nodes online.</p> : leaderboard.map((n, i) => {
                  const score = Math.round(n.safety_score || 100);
                  let color = '#00d4ff'; 
                  if (score < 60) color = '#ffaa00'; 
                  if (score < 30) color = '#ff0055'; 
                  
                  return (
                    <div key={n.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div>
                        <div style={{ fontWeight: '500', fontSize: '14px' }}>{i + 1}. {n.name}</div>
                        <div style={{ fontSize: '11px', color: '#888', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                          <CloudRain size={10} /> {n.weather_condition || 'Clear'} | {n.current_crowd_count.toLocaleString()} pax
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ color: color, fontWeight: 'bold', fontSize: '18px', fontFamily: 'monospace' }}>{score}%</div>
                        <div style={{ fontSize: '9px', color: '#666', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Safety Score</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}

        {activeTab === 'insights' && (
          <>
            {/* Historical Insights Chart */}
            <div className="glass-panel" style={{ padding: '16px' }}>
              <h3 style={{ fontSize: '16px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TrendingUp size={18} className="text-cyan" />
                AI Historical Insights
              </h3>
              <p style={{ fontSize: '12px', color: '#888', marginBottom: '10px' }}>Visitor Influx (Millions)</p>
              <div style={{ height: '250px', width: '100%' }}>
                {insights ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={insights.chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                      <XAxis dataKey="name" stroke="#888" fontSize={12} />
                      <YAxis stroke="#888" fontSize={12} />
                      <RechartsTooltip contentStyle={{ backgroundColor: '#111', borderColor: '#333' }} />
                      <Line type="monotone" dataKey="visitors" stroke="#00d4ff" strokeWidth={3} dot={{ fill: '#00d4ff', r: 4 }} activeDot={{ r: 8 }} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-secondary" style={{ fontSize: '12px' }}>Loading AI Projection...</p>
                )}
              </div>
            </div>

            {/* Historical Educational Insights */}
            <div className="glass-panel" style={{ padding: '16px' }}>
              <h3 style={{ fontSize: '16px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CloudRain size={18} className="text-cyan" />
                Pilgrim Safety & Educational Insights
              </h3>
              <p style={{ fontSize: '12px', color: '#888', marginBottom: '10px' }}>Learn from past historical events with low safety indexes to plan your visit.</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {insights?.historical_risks ? insights.historical_risks.map((risk: any, i: number) => (
                  <div key={i} style={{ padding: '12px', background: 'rgba(255,170,0,0.1)', border: '1px solid rgba(255,170,0,0.2)', borderRadius: '6px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <strong style={{ color: '#ffaa00', fontSize: '14px' }}>{risk.event}</strong>
                      <span style={{ fontSize: '12px', color: '#aaa' }}>{risk.date}</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#ccc', marginBottom: '6px', display: 'flex', gap: '10px' }}>
                      <span><strong>Weather:</strong> {risk.weather}</span>
                      <span><strong>Safety Index:</strong> {risk.safety_index}%</span>
                    </div>
                    <p style={{ fontSize: '13px', lineHeight: '1.4', margin: 0, color: '#e0e0e0' }}>
                      {risk.advice}
                    </p>
                  </div>
                )) : (
                  <p className="text-secondary" style={{ fontSize: '12px' }}>Loading educational insights...</p>
                )}
              </div>
            </div>

            {/* Alerts History (Currently active alerts mapped here for historical context) */}
            <div className="glass-panel" style={{ padding: '16px' }}>
              <h3 style={{ fontSize: '16px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertCircle size={18} className="text-cyan" />
                System Alerts Log
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {alerts.length === 0 ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#888', fontSize: '14px' }}>
                    <CheckCircle2 size={16} /> All sectors clear.
                  </div>
                ) : (
                  alerts.map((a: any) => (
                    <div key={a.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', padding: '10px', background: 'rgba(255,0,85,0.1)', border: '1px solid rgba(255,0,85,0.2)', borderRadius: '4px', color: '#ff0055' }}>
                      <AlertCircle size={16} style={{ marginTop: '2px', flexShrink: 0 }} />
                      <span style={{ fontSize: '14px', lineHeight: '1.4' }}>{a.message}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        )}

      </div>
    </div>
  );
}
