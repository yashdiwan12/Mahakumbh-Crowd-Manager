import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import Head from 'next/head';
import Sidebar from '../components/Sidebar';

// Map container cannot be server-side rendered because it uses Leaflet
const MapWithNoSSR = dynamic(() => import('../components/Map'), {
  ssr: false,
});

export default function Dashboard() {
  const [globalState, setGlobalState] = useState<any>({});
  const [activeRoute, setActiveRoute] = useState<string[]>([]);
  const [routeDetails, setRouteDetails] = useState<any>(null);

  return (
    <>
      <Head>
        <title>Unified Control Room | Mahakumbh 2028</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <main style={{ display: 'flex', height: '100vh', width: '100vw', background: 'var(--bg-dark)' }}>
        {/* Sidebar Section (30%) */}
        <div style={{ flex: 3, minWidth: '350px', background: 'var(--bg-dark)', borderRight: '1px solid var(--glass-border)', zIndex: 10 }}>
          <Sidebar 
            state={globalState} 
            onRouteCalculated={setActiveRoute}
            routeDetails={routeDetails}
          />
        </div>

        {/* Map Section (70%) */}
        <div style={{ flex: 7, position: 'relative' }}>
          <MapWithNoSSR 
             onStateUpdate={setGlobalState} 
             activeRoute={activeRoute}
             onRouteDetailsUpdate={setRouteDetails}
          />
        </div>
      </main>
    </>
  );
}
