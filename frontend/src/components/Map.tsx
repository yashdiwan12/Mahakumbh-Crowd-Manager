import React, { useEffect, useRef, useState } from 'react';
import { Wrapper } from '@googlemaps/react-wrapper';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'wss://mahakumbh-backend.onrender.com/api/v1/stream';

// Dark "Neural Noir" Map Style
const mapStyles = [
  { elementType: "geometry", stylers: [{ color: "#050505" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#050505" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#888888" }] },
  {
    featureType: "administrative.locality",
    elementType: "labels.text.fill",
    stylers: [{ color: "#e0e0e0" }],
  },
  {
    featureType: "poi",
    elementType: "labels.text.fill",
    stylers: [{ color: "#888888" }],
  },
  {
    featureType: "poi.park",
    elementType: "geometry",
    stylers: [{ color: "#0a0a0a" }],
  },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ color: "#111111" }],
  },
  {
    featureType: "road",
    elementType: "geometry.stroke",
    stylers: [{ color: "#222222" }],
  },
  {
    featureType: "road",
    elementType: "labels.text.fill",
    stylers: [{ color: "#555555" }],
  },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#000000" }],
  },
  {
    featureType: "water",
    elementType: "labels.text.fill",
    stylers: [{ color: "#333333" }],
  },
];

interface InnerMapProps {
  onStateUpdate: (state: any) => void;
  activeRoute: string[];
  onRouteDetailsUpdate?: (details: any) => void;
}

function InnerMap({ onStateUpdate, activeRoute, onRouteDetailsUpdate }: InnerMapProps) {
  const ref = useRef<HTMLDivElement>(null);
  const mapRef = useRef<google.maps.Map | null>(null);
  const nodesRef = useRef<{ [id: string]: google.maps.Circle }>({});
  const edgesRef = useRef<{ [id: string]: google.maps.Polyline }>({});
  const tooltipsRef = useRef<{ [id: string]: google.maps.InfoWindow }>({});
  const latestNodesRef = useRef<any[]>([]);
  
  const activeRouteLineRef = useRef<google.maps.Polyline | null>(null);
  const animationTimerRef = useRef<number | null>(null);

  useEffect(() => {
    if (ref.current && !mapRef.current) {
      mapRef.current = new window.google.maps.Map(ref.current, {
        center: { lat: 23.1765, lng: 75.7885 },
        zoom: 13,
        styles: mapStyles,
        disableDefaultUI: true,
      });
      
      // Add Traffic Layer (Red/Yellow/Green lines on roads)
      const trafficLayer = new window.google.maps.TrafficLayer();
      trafficLayer.setMap(mapRef.current);

      // Add Emergency Resource Markers
      const resources = [
        { lat: 23.1800, lng: 75.7700, title: 'NDRF Base Alpha', color: '#ff0055' },
        { lat: 23.1850, lng: 75.7650, title: 'Medical Camp 1', color: '#00ff55' },
        { lat: 23.1750, lng: 75.7850, title: 'Police Transit Post', color: '#0055ff' },
        { lat: 23.2000, lng: 75.7800, title: 'NDRF Base Beta', color: '#ff0055' },
      ];
      resources.forEach(r => {
          new window.google.maps.Marker({
              position: { lat: r.lat, lng: r.lng },
              map: mapRef.current,
              title: r.title,
              icon: {
                path: window.google.maps.SymbolPath.CIRCLE,
                scale: 6,
                fillColor: r.color,
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#fff',
              }
          });
      });
    }
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;
    const ws = new WebSocket(WS_URL);
    
    ws.onmessage = (event) => {
      const state = JSON.parse(event.data);
      onStateUpdate(state);
      latestNodesRef.current = state.nodes;

      state.nodes.forEach((node: any) => {
        const cap = node.max_capacity || 10000;
        const ratio = Math.min(node.current_crowd_count / cap, 1.0);
        const score = node.safety_score || 100;
        
        // Pulsing alert for dangerous nodes (score < 30)
        const isDangerous = score < 30;
        const color = isDangerous ? '#ff0055' : (score < 60 ? '#ffaa00' : '#00d4ff');
        const fillOpacity = 0.2 + (ratio * 0.6);
        const radius = 100 + (ratio * 150); // M radius
        
        if (!nodesRef.current[node.id]) {
          nodesRef.current[node.id] = new window.google.maps.Circle({
            strokeColor: color,
            strokeOpacity: 0.8,
            strokeWeight: isDangerous ? 4 : 2,
            fillColor: color,
            fillOpacity: fillOpacity,
            map: mapRef.current,
            center: { lat: node.latitude, lng: node.longitude },
            radius: radius,
          });
          
          // Tooltip on hover
          const info = new window.google.maps.InfoWindow({
             content: `<div style="color:black;font-family:monospace;padding:5px;"><b>${node.name}</b><br/>Safety: ${Math.round(score)}%<br/>Weather: ${node.weather_condition || 'Clear'}</div>`
          });
          tooltipsRef.current[node.id] = info;
          
          nodesRef.current[node.id].addListener('mouseover', () => {
             info.setPosition({ lat: node.latitude, lng: node.longitude });
             info.open(mapRef.current);
          });
          nodesRef.current[node.id].addListener('mouseout', () => {
             info.close();
          });
          
        } else {
          // Update existing
          nodesRef.current[node.id].setOptions({
            fillColor: color,
            strokeColor: color,
            strokeWeight: isDangerous ? 4 : 2,
            fillOpacity: fillOpacity,
            radius: radius
          });
        }
      });
      
      // Draw background edges (dimmed)
      if (Object.keys(edgesRef.current).length === 0 && state.edges.length > 0 && state.nodes.length > 0) {
         state.edges.forEach((e: any) => {
            const source = state.nodes.find((n:any) => n.id === e.source_id);
            const target = state.nodes.find((n:any) => n.id === e.target_id);
            if (source && target) {
               const path = [
                  { lat: source.latitude, lng: source.longitude },
                  { lat: target.latitude, lng: target.longitude }
               ];
               const poly = new window.google.maps.Polyline({
                  path: path,
                  geodesic: true,
                  strokeColor: '#222222',
                  strokeOpacity: 0.3,
                  strokeWeight: 1,
                  map: mapRef.current
               });
               edgesRef.current[`${e.source_id}-${e.target_id}`] = poly;
               edgesRef.current[`${e.target_id}-${e.source_id}`] = poly;
            }
         });
      }
    };

    return () => ws.close();
  }, []);

  // Update active route styling directly with DirectionsService and Animations
  useEffect(() => {
    if (activeRouteLineRef.current) {
        activeRouteLineRef.current.setMap(null);
        activeRouteLineRef.current = null;
    }
    if (animationTimerRef.current) {
        window.clearInterval(animationTimerRef.current);
    }

    if (activeRoute.length > 0 && latestNodesRef.current.length > 0) {
       const waypoints = activeRoute.map(id => {
           const n = latestNodesRef.current.find((n:any) => n.id === id);
           return n ? { location: new window.google.maps.LatLng(n.latitude, n.longitude), stopover: true } : null;
       }).filter(w => w !== null) as google.maps.DirectionsWaypoint[];

       if (waypoints.length < 2) return;

       const origin = waypoints.shift()?.location;
       const destination = waypoints.pop()?.location;

       if (!origin || !destination) return;

       const directionsService = new window.google.maps.DirectionsService();
       directionsService.route({
           origin: origin as google.maps.LatLng,
           destination: destination as google.maps.LatLng,
           waypoints: waypoints,
           travelMode: window.google.maps.TravelMode.WALKING
       }, (result, status) => {
           if (status === 'OK' && result) {
               const path = result.routes[0].overview_path;
               const leg = result.routes[0].legs[0];
               
               if (onRouteDetailsUpdate) {
                   onRouteDetailsUpdate({ distance: leg.distance?.text, duration: leg.duration?.text });
               }

               const lineSymbol = {
                   path: window.google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                   scale: 4,
                   strokeColor: '#00d4ff',
                   fillColor: '#00d4ff',
                   fillOpacity: 1
               };

               const polyline = new window.google.maps.Polyline({
                   path: path,
                   strokeColor: '#00d4ff',
                   strokeOpacity: 0.8,
                   strokeWeight: 5,
                   icons: [{
                       icon: lineSymbol,
                       offset: '0%'
                   }],
                   map: mapRef.current
               });

               activeRouteLineRef.current = polyline;

               // Animate Flow Arrow (Slower, stops at 100%)
               let count = 0;
               animationTimerRef.current = window.setInterval(() => {
                   count += 1;
                   if (count > 200) {
                       if (animationTimerRef.current) {
                           window.clearInterval(animationTimerRef.current);
                       }
                       return;
                   }
                   const icons = polyline.get('icons');
                   if (icons && icons[0]) {
                       icons[0].offset = (count / 2) + '%';
                       polyline.set('icons', icons);
                   }
               }, 40);
           }
       });
    }
  }, [activeRoute]);

  return <div ref={ref} style={{ width: '100%', height: '100%' }} />;
}

export default function Map({ onStateUpdate, activeRoute, onRouteDetailsUpdate }: InnerMapProps) {
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '';
  return (
    <Wrapper apiKey={apiKey}>
      <InnerMap onStateUpdate={onStateUpdate} activeRoute={activeRoute} onRouteDetailsUpdate={onRouteDetailsUpdate} />
    </Wrapper>
  );
}
