import { useEffect, useRef } from 'react';
import { useDashboardStore } from '../store/dashboard';

const BASE_DELAY_MS = 1000;
const MAX_DELAY_MS = 30000;

export function useWebSocket() {
  const addEvent = useDashboardStore((s) => s.addEvent);
  const setConnected = useDashboardStore((s) => s.setWsConnected);
  const attemptRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const unmountedRef = useRef(false);

  useEffect(() => {
    unmountedRef.current = false;

    function connect() {
      if (unmountedRef.current) return;

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/events`);

      ws.onopen = () => {
        attemptRef.current = 0;
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

      ws.onclose = () => {
        setConnected(false);
        if (!unmountedRef.current) {
          const delay = Math.min(
            BASE_DELAY_MS * Math.pow(2, attemptRef.current),
            MAX_DELAY_MS,
          );
          attemptRef.current += 1;
          timerRef.current = setTimeout(connect, delay);
        }
      };
    }

    connect();

    return () => {
      unmountedRef.current = true;
      if (timerRef.current !== null) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [addEvent, setConnected]);
}
