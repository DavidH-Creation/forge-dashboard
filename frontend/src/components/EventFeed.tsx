import { useDashboardStore } from '../store/dashboard';

const COMPONENT_COLORS: Record<string, string> = {
  Crucible: '#74c0fc',
  Cartographer: '#b197fc',
  Crossfire: '#ffa94d',
  Bulwark: '#69db7c',
};

interface EventFeedProps {
  limit?: number;
}

export function EventFeed({ limit = 20 }: EventFeedProps) {
  const events = useDashboardStore((s) => s.recentEvents);
  const shown = events.slice(0, limit);

  if (shown.length === 0) {
    return (
      <div className="event-feed event-feed--empty">
        <p>No recent events</p>
      </div>
    );
  }

  return (
    <div className="event-feed">
      <h3 className="event-feed__title">Recent Events</h3>
      <ul className="event-feed__list">
        {shown.map((ev, i) => {
          const color = COMPONENT_COLORS[ev.component] ?? '#868e96';
          return (
            <li key={`${ev.run_id}-${ev.timestamp}-${i}`} className="event-feed__item">
              <span
                className="event-feed__component"
                style={{ color }}
              >
                {ev.component}
              </span>
              <span className="event-feed__type">{ev.event_type}</span>
              <span className="event-feed__run">{ev.run_id?.slice(0, 8)}</span>
              <span className="event-feed__time">
                {new Date(ev.timestamp).toLocaleTimeString()}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
