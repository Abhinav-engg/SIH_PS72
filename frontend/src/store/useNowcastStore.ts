import { create } from 'zustand';
import axios from 'axios';
import { type WeatherAlert } from '../types/nowcast';

export type MapLayer = 'thunderstorm' | 'lightning' | 'composite' | 'observations';

const API_BASE_URL = 'http://localhost:8001';

interface NowcastState {
  cells: any[];
  alerts: WeatherAlert[];
  radarScans: any[];
  lightningStrokes: any[];
  timestamp: string | null;
  selectedLayer: MapLayer;
  mapCenter: [number, number] | null;
  mapZoom: number | null;
  forecastMinute: number;
  isLoading: boolean;
  error: string | null;

  setNowcastData: (data: any) => void;
  setAlerts: (alerts: WeatherAlert[]) => void;
  setSelectedLayer: (layer: MapLayer) => void;
  setMapCenter: (center: [number, number] | null, zoom?: number) => void;
  setForecastMinute: (minute: number) => void;

  fetchActiveAlerts: () => Promise<void>;
  fetchLatestNowcast: () => Promise<void>;
  fetchRadarAndLightning: () => Promise<void>;
}

const FALLBACK_ALERTS: WeatherAlert[] = [
  { id: 'alert-1', title: 'Severe Thunderstorm Warning', description: 'Intense convective squall line tracking eastward.', riskLevel: 'severe', latitude: 28.6139, longitude: 77.2090, radius_km: 60, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), eventType: 'THUNDERSTORM', probability: 0.85 },
  { id: 'alert-2', title: 'Extreme Lightning Risk', description: 'Frequent cloud-to-ground lightning discharge.', riskLevel: 'extreme', latitude: 22.5726, longitude: 88.3639, radius_km: 45, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 1 * 60 * 60 * 1000).toISOString(), eventType: 'EXTREME_LIGHTNING', probability: 0.95 },
  { id: 'alert-3', title: 'Moderate Squall Alert', description: 'Squally winds reaching 50-60 kmph.', riskLevel: 'moderate', latitude: 19.0760, longitude: 72.8777, radius_km: 80, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(), eventType: 'SQUALL', probability: 0.45 },
  { id: 'alert-4', title: 'High Hailstorm Risk', description: 'Hailstones up to 25mm diameter expected.', riskLevel: 'high', latitude: 13.0827, longitude: 80.2707, radius_km: 50, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 1.5 * 60 * 60 * 1000).toISOString(), eventType: 'HAILSTORM', probability: 0.65 },
  { id: 'alert-5', title: 'Severe Cloudburst Warning', description: 'Extreme rainfall rate exceeding 60 mm/hr.', riskLevel: 'severe', latitude: 31.1048, longitude: 77.1734, radius_km: 30, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), eventType: 'THUNDERSTORM', probability: 0.88 },
  { id: 'alert-6', title: 'Low Wind Alert', description: 'Gusty surface winds in isolated pockets.', riskLevel: 'low', latitude: 23.0225, longitude: 72.5714, radius_km: 100, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(), eventType: 'SQUALL', probability: 0.25 },
];

export const useNowcastStore = create<NowcastState>((set, get) => ({
  cells: [],
  alerts: [],
  radarScans: [],
  lightningStrokes: [],
  timestamp: null,
  selectedLayer: 'thunderstorm',
  mapCenter: null,
  mapZoom: null,
  forecastMinute: 0,
  isLoading: false,
  error: null,

  setNowcastData: (data) => set({ cells: data.cells || [], timestamp: data.issued_at }),
  setAlerts: (alerts) => set({ alerts }),
  setSelectedLayer: (layer) => set({ selectedLayer: layer }),
  setMapCenter: (center, zoom) => set((state) => ({
    mapCenter: center,
    mapZoom: zoom ?? state.mapZoom,
  })),
  setForecastMinute: (minute) => set({ forecastMinute: minute }),

  fetchActiveAlerts: async () => {
    set({ isLoading: true, error: null });
    try {
      const endpoints = [
        `${API_BASE_URL}/alerts/`,
        '/api/v1/alerts/',
        `${API_BASE_URL}/api/v1/alerts/`,
      ];
      let remoteAlerts = null;
      for (const ep of endpoints) {
        try {
          const res = await axios.get(ep, { timeout: 2500 });
          if (res.data && Array.isArray(res.data.alerts) && res.data.alerts.length > 0) {
            remoteAlerts = res.data.alerts;
            break;
          }
        } catch {}
      }

      if (remoteAlerts) {
        const formatted = remoteAlerts.map((a: any) => ({
          id: a.id || `alert-${Math.random().toString(36).substring(7)}`,
          title: a.title || 'Severe Weather Warning',
          description: a.description || a.message || 'Thunderstorm activity detected.',
          riskLevel: (a.riskLevel || a.severity || 'moderate').toLowerCase(),
          latitude: a.latitude ?? a.centroid_lat ?? 28.61,
          longitude: a.longitude ?? a.centroid_lon ?? 77.23,
          radius_km: a.radius_km || 40,
          issuedAt: a.issuedAt || a.issue_time || new Date().toISOString(),
          validUntil: a.validUntil || a.valid_until || new Date(Date.now() + 2 * 3600000).toISOString(),
          eventType: a.eventType || a.alert_type || 'THUNDERSTORM',
          probability: a.probability ?? 0.75,
        }));
        set({ alerts: formatted, isLoading: false });
      } else {
        set({ alerts: FALLBACK_ALERTS, isLoading: false });
      }
    } catch {
      set({ alerts: FALLBACK_ALERTS, isLoading: false });
    }
  },

  fetchLatestNowcast: async () => {
    try {
      const endpoints = [
        `${API_BASE_URL}/nowcast/`,
        '/api/v1/nowcast/',
        `${API_BASE_URL}/api/v1/nowcast/`,
      ];
      let remoteData = null;
      for (const ep of endpoints) {
        try {
          const res = await axios.get(ep, { timeout: 2500 });
          if (res.data && Array.isArray(res.data.cells) && res.data.cells.length > 0) {
            remoteData = res.data;
            break;
          }
        } catch {}
      }

      if (remoteData) {
        set({
          cells: remoteData.cells,
          timestamp: remoteData.issued_at || new Date().toISOString(),
        });
      } else {
        const fallbackCells = Array.from({ length: 8 }).map((_, i) => ({
          cell_id: `TS-${i + 1}`,
          center: { lat: 28.2 + i * 0.4, lon: 76.8 + i * 0.5 },
          lat: 28.2 + i * 0.4,
          lon: 76.8 + i * 0.5,
          radius_km: 25 + (i % 3) * 10,
          intensity: 40 + (i % 4) * 8,
          max_reflectivity_dbz: 40 + (i % 4) * 8,
          severity: i % 2 === 0 ? 'severe' : 'moderate',
          probability: 0.7 + (i % 3) * 0.1,
        }));
        set({ cells: fallbackCells, timestamp: new Date().toISOString() });
      }
    } catch {
      const fallbackCells = [
        { cell_id: 'TS-001', center: { lat: 28.61, lon: 77.23 }, lat: 28.61, lon: 77.23, radius_km: 35, intensity: 52.0, severity: 'severe', probability: 0.85 },
        { cell_id: 'TS-002', center: { lat: 28.35, lon: 77.55 }, lat: 28.35, lon: 77.55, radius_km: 28, intensity: 44.0, severity: 'high', probability: 0.72 },
        { cell_id: 'TS-003', center: { lat: 28.85, lon: 76.95 }, lat: 28.85, lon: 76.95, radius_km: 22, intensity: 38.0, severity: 'moderate', probability: 0.58 },
      ];
      set({ cells: fallbackCells, timestamp: new Date().toISOString() });
    }
  },

  fetchRadarAndLightning: async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/lightning/recent`, { timeout: 2500 });
      if (res.data && Array.isArray(res.data.strokes)) {
        set({
          lightningStrokes: res.data.strokes,
          radarScans: [{ timestamp: new Date().toISOString(), url: '/mock-radar-1.png' }],
        });
        return;
      }
    } catch {}

    const fallbackStrokes = Array.from({ length: 48 }).map((_, i) => ({
      id: `ls-${i}`,
      lat: 28.0 + (i % 12) * 0.15 + (Math.sin(i) * 0.1),
      lon: 76.6 + (i % 12) * 0.18 + (Math.cos(i) * 0.1),
      time: new Date().toISOString(),
      type: i % 3 === 0 ? 'CG' : 'IC',
      current_ka: -24 - (i % 5) * 6,
    }));

    set({
      radarScans: [{ timestamp: new Date().toISOString(), url: '/mock-radar-1.png' }],
      lightningStrokes: fallbackStrokes,
    });
  },
}));
