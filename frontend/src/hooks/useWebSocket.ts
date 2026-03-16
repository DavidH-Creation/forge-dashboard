import { useEffect, useRef } from 'react';
import { useDashboardStore } from '../store/dashboard';

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const addEvent = useDashboardStore((s) => s.addEvent);
  const setConnected = useDashboardStore((s) => s.setWsConnected);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(
      `${protocol}//${window.location.host}/ws/events`,
    );
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      ws.send(
        JSON.stringify({
          type: 'replay',
          since: new Date(Date.now() - 86400000).toISOString(),
        }),
      );
    };

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type !== 'replay_complete') addEvent(data);
    };

    ws.onclose = () => setConnected(false);

    return () => ws.close();
  }, [addEvent, setConnected]);
}
