import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  Activity,
  Zap,
  Radio,
  Bell,
  BarChart3,
  FlaskConical,
  Menu,
  X,
  Server,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { api } from '../api/client';

export const Layout: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [health, setHealth] = useState<any>(null);
  const location = useLocation();

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'offline', model_loaded: false }));
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: Activity },
    { to: '/prediction', label: 'Prediction', icon: Zap },
    { to: '/telemetry', label: 'Telemetry', icon: Radio },
    { to: '/alerts', label: 'Alerts', icon: Bell },
    { to: '/model-performance', label: 'Model Performance', icon: BarChart3 },
    { to: '/boundary-tests', label: 'Boundary Tests', icon: FlaskConical },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
      {/* SIDEBAR */}
      <aside
        style={{
          width: '260px',
          backgroundColor: 'var(--bg-panel)',
          borderRight: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          position: 'fixed',
          top: 0,
          bottom: 0,
          left: 0,
          zIndex: 40,
          transform: mobileMenuOpen ? 'translateX(0)' : undefined,
          transition: 'transform 0.3s ease',
        }}
        className="sidebar-container"
      >
        <div>
          {/* Brand Header */}
          <div style={{ padding: '24px 20px', borderBottom: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #F59E0B, #D97706)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 15px rgba(245, 158, 11, 0.4)',
                }}
              >
                <Cpu size={22} color="#0B0A08" />
              </div>
              <div>
                <h1 style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '1px', color: 'var(--saffron-primary)', lineHeight: 1.1 }}>
                  NSQP
                </h1>
                <p style={{ fontSize: '10px', color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '0.5px' }}>
                  NETWORK QUALITY PREDICTOR
                </p>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav style={{ padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  style={({ isActive }) => ({
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    fontWeight: 600,
                    fontSize: '14px',
                    transition: 'all 0.2s',
                    backgroundColor: isActive ? 'var(--saffron-glow)' : 'transparent',
                    color: isActive ? 'var(--saffron-primary)' : 'var(--text-secondary)',
                    borderLeft: isActive ? '3px solid var(--saffron-primary)' : '3px solid transparent',
                  })}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Status Footer */}
        <div style={{ padding: '16px', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-elevated)', margin: '12px', borderRadius: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.5px', color: 'var(--text-muted)' }}>
              MODEL STATUS
            </span>
            <span className={`badge ${health?.model_loaded ? 'badge-online' : 'badge-danger'}`}>
              ● {health?.model_loaded ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-primary)', fontWeight: 600, margin: '2px 0' }}>
            MLP 128×64 (ANN)
          </p>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            <span>Threshold: <b style={{ color: 'var(--saffron-primary)' }}>0.80</b></span>
            <span>Mode: <b>Current State</b></span>
          </div>
          <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid rgba(58, 42, 22, 0.5)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span className="badge badge-sim" style={{ fontSize: '10px', padding: '2px 8px' }}>
              ◉ SIMULATION MODE
            </span>
          </div>
        </div>
      </aside>

      {/* MAIN CONTAINER */}
      <div style={{ flex: 1, marginLeft: '260px', display: 'flex', flexDirection: 'column' }} className="main-content-wrapper">
        {/* Top Header */}
        <header
          style={{
            height: '64px',
            backgroundColor: 'var(--bg-panel)',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 24px',
            position: 'sticky',
            top: 0,
            zIndex: 30,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                display: 'none',
              }}
              className="mobile-menu-btn"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Server size={18} color="var(--saffron-primary)" />
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Campus Core Network NOC • QoS Monitoring
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge badge-sim">
              ◉ HISTORICAL PLAYBACK
            </span>
            <span className="badge badge-online">
              <ShieldCheck size={14} /> REST API: ACTIVE (:8000)
            </span>
          </div>
        </header>

        {/* Page View Body */}
        <main style={{ padding: '28px', maxWidth: '1400px', width: '100%', margin: '0 auto' }}>
          <Outlet />
        </main>
      </div>

      <style>{`
        @media (max-width: 900px) {
          .sidebar-container {
            transform: translateX(-100%);
          }
          .main-content-wrapper {
            margin-left: 0 !important;
          }
          .mobile-menu-btn {
            display: block !important;
          }
        }
      `}</style>
    </div>
  );
};
