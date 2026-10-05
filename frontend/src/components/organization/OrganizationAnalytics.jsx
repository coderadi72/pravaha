import { useEffect, useId, useRef, useState } from 'react';
import { Activity, ArrowUpRight, CircleAlert, ClipboardCheck, FolderKanban, MapPin, RefreshCw, ShieldCheck, TrendingUp, Users } from 'lucide-react';
import { organizationApi } from '../../api/organization.js';
import { useUiPreferences } from '../../ui/useUiPreferences.js';
import '../../styles/organization-analytics.css';

const tones = ['primary', 'info', 'muted', 'border'];
const alertLabels = {
  DELAY: 'Delayed activities', SIGNIFICANT_VARIANCE: 'Schedule variance', APPROACHING_FINISH: 'Approaching planned finish',
  STALE: 'Stale execution evidence', REPEATED_INCOMPLETE: 'Incomplete field reports', DATA_QUALITY: 'Schedule data quality',
  UNMATCHED: 'Unmatched field updates', PENDING_REVIEW: 'PM review required', SCHEDULE_VERSION_CHANGE: 'Schedule version changed',
  LINKAGE_QUALITY: 'Schedule link quality', DEPENDENCY_CHAIN: 'Dependency exposure', DEPENDENCY_EXPOSURE: 'Dependency exposure', NEGATIVE_FLOAT: 'Negative schedule float',
};
const healthLabels = { DELAYED: 'Delayed', AT_RISK: 'At risk', UNKNOWN: 'Limited evidence', NO_DELAY_SIGNAL: 'No delay signal' };
const projectImages = {
  'PRJ-001': { src: '/projects/greenfield-refinery.png', alt: 'Greenfield Refinery project', position: 'center 58%' },
  'PRJ-002': { src: '/projects/coastal-highway.png', alt: 'Coastal Highway project', position: 'center 54%' },
  'PRJ-003': { src: '/projects/thermal-power-plant.png', alt: 'Thermal Power Plant project', position: 'center 55%' },
  'PRJ-004': { src: '/projects/metro-rail-extension.png', alt: 'Metro Rail Extension project', position: 'center 55%' },
};

function Panel({ title, subtitle, action, children, className = '' }) {
  return <section className={`oa-card ${className}`}><header className="oa-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{action}</header>{children}</section>;
}

function ProgressBar({ value, label }) {
  return <div className="oa-progress" role="meter" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={value ?? undefined} aria-valuetext={value == null ? '-' : `${value}%`}><span style={{ width: `${value ?? 0}%` }} /></div>;
}

function BarChart({ items, title, t, onSelect, unit = 'projects' }) {
  const [active, setActive] = useState(null);
  const max = Math.max(1, ...items.map(item => item.value));
  const current = items[active ?? 0];
  return <div className="oa-bar-chart-wrap">
    <div className="oa-bar-chart" role="img" aria-label={`${title}: ${items.map(item => `${t(item.label)} ${item.value}`).join(', ')}`}>
      {items.map((item, index) => <button type="button" className={`oa-bar-column${active === index ? ' is-active' : ''}`} key={item.label} aria-label={`${t(item.label)}: ${item.value} ${t(unit)}`} onMouseEnter={() => setActive(index)} onFocus={() => setActive(index)} onClick={() => onSelect?.(item.label)}>
        <span className="oa-bar-value">{item.value.toLocaleString()}</span><span className="oa-bar" style={{ height: `${Math.max(4, item.value / max * 100)}%` }} /><span className="oa-bar-label">{t(item.label)}</span>
      </button>)}
    </div>
    {current && <p className="oa-bar-readout" aria-live="polite"><strong>{t(current.label)}</strong><span>{current.value.toLocaleString()} {t(unit)}</span>{max ? <span>{Math.round(current.value / items.reduce((sum, item) => sum + item.value, 0) * 100) || 0}%</span> : null}</p>}
  </div>;
}

function CompletionChart({ data, t, locale }) {
  const id = useId();
  const [active, setActive] = useState(null);
  const chartRef = useRef(null);
  const [width, setWidth] = useState(740);
  const points = data.points;
  useEffect(() => {
    if (!chartRef.current) return;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(240, entry.contentRect.width)));
    observer.observe(chartRef.current);
    return () => observer.disconnect();
  }, [points.length]);
  const formatDate = (date) => new Date(`${date}T00:00:00`).toLocaleDateString(locale, { day: 'numeric', month: 'short', year: '2-digit' });
  if (!points.length) return <div className="oa-empty oa-chart-empty"><TrendingUp size={28} /><strong>{t('Schedule dates unavailable')}</strong><p>{t('Import a dated schedule to compare planned and confirmed completions.')}</p></div>;
  const min = Date.parse(points[0].date), max = Date.parse(points.at(-1).date);
  const x = (p) => 46 + (max === min ? .5 : (Date.parse(p.date) - min) / (max - min)) * (width - 62);
  const y = (value) => 218 - value * 1.9;
  const current = points[active ?? points.findLastIndex(p => p.actual != null)];
  return <>
    <div className="oa-chart-legend"><span><i className="oa-dot is-info" />{t('Planned')}</span><span><i className="oa-dot is-primary" />{t('Actual')}</span><small>{t('Cumulative activity completion')}</small></div>
    <div className="oa-chart" ref={chartRef}><svg viewBox={`0 0 ${width} 255`} role="img" aria-labelledby={`${id}-title ${id}-desc`}>
      <title id={`${id}-title`}>{t('Project Progress Overview')}</title><desc id={`${id}-desc`}>{t('Percentage of all scheduled activities with planned or confirmed finish dates. Future actuals are not forecast.')}</desc>
      {[0, 25, 50, 75, 100].map(value => <g key={value}><line x1="46" x2={width - 16} y1={y(value)} y2={y(value)} className="oa-grid-line" /><text x="36" y={y(value) + 4} textAnchor="end">{value}%</text></g>)}
      {points.map((p, index) => <g key={p.date}>
        {(index === 0 || index === Math.floor(points.length / 2) || index === points.length - 1) && <text x={x(p)} y="246" textAnchor={index === 0 ? 'start' : index === points.length - 1 ? 'end' : 'middle'}>{formatDate(p.date)}</text>}
        <rect x={x(p) - 13} y={y(p.planned)} width="10" height={218 - y(p.planned)} className="oa-bar-plot is-planned" />
        {p.actual != null && <rect x={x(p) + 3} y={y(p.actual)} width="10" height={218 - y(p.actual)} className="oa-bar-plot is-actual" />}
        <rect x={x(p) - 10} y="20" width="20" height="205" fill="transparent" tabIndex={0} role="button" aria-label={`${formatDate(p.date)}: ${t('Planned')} ${p.planned}%, ${t('Actual')} ${p.actual == null ? t('Not available') : `${p.actual}%`}`} onMouseEnter={() => setActive(index)} onFocus={() => setActive(index)} onClick={() => setActive(index)} onKeyDown={e => { if (e.key === 'ArrowRight') { e.preventDefault(); setActive(Math.min(points.length - 1, index + 1)); e.currentTarget.parentElement.nextElementSibling?.querySelector('rect')?.focus(); } if (e.key === 'ArrowLeft') { e.preventDefault(); setActive(Math.max(0, index - 1)); e.currentTarget.parentElement.previousElementSibling?.querySelector('rect')?.focus(); } }} />
      </g>)}
    </svg></div>
    <div className="oa-chart-readout" aria-live="polite"><strong>{formatDate(current.date)}</strong><span>{t('Planned')} <b>{current.planned}%</b></span><span>{t('Actual')} <b>{current.actual == null ? '—' : `${current.actual}%`}</b></span></div>
    <p className="oa-note">{t('Dated schedule coverage')}: {data.scheduled}/{data.total} · {t('Confirmed finish dates')}: {data.datedActuals}. {t('Current schedule snapshot; not historical weighted progress.')}</p>
  </>;
}

function Ring({ items, title, t, focusLabel }) {
  const total = items.reduce((sum, item) => sum + item.value, 0);
  const focus = items.find(item => item.label === focusLabel)?.value ?? 0;
  return <><div className="oa-ring-wrap"><svg viewBox="0 0 160 160" role="img" aria-label={`${title}: ${items.map(item => `${t(item.label)} ${item.value}`).join(', ')}`}>
    <circle cx="80" cy="80" r="60" className="oa-ring-track" />
    {items.map((item, index) => { const size = total ? item.value / total * 100 : 0; const start = total ? items.slice(0, index).reduce((sum, segment) => sum + segment.value, 0) / total * 100 : 0; return <circle key={item.label} cx="80" cy="80" r="60" pathLength="100" className={`oa-ring-segment is-${tones[index]}`} strokeDasharray={`${size} ${100 - size}`} strokeDashoffset={-start} transform="rotate(-90 80 80)"><title>{t(item.label)}: {item.value}</title></circle>; })}
  </svg><div className="oa-ring-center"><strong>{focusLabel ? total ? `${Math.round(focus / total * 100)}%` : '—' : total}</strong><span>{t(focusLabel || 'Total activities')}</span></div></div>
    <ul className="oa-ring-legend">{items.map((item, i) => <li key={item.label}><span><i className={`oa-dot is-${tones[i]}`} />{t(item.label)}</span><strong>{item.value.toLocaleString()}</strong></li>)}</ul>
    {!total && <p className="oa-note">{t('No records available yet.')}</p>}
  </>;
}

export default function OrganizationAnalytics({ workflowData, onNavigate, onOpenProject, onOpenReport }) {
  const { t, locale } = useUiPreferences();
  const [state, setState] = useState({ data: null, error: false });
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let current = true;
    organizationApi.analytics().then(data => { if (current) setState({ data, error: false }); })
      .catch(() => { if (current) setState({ data: null, error: true }); });
    return () => { current = false; };
  }, [workflowData, revision]);
  const retry = () => { setState({ data: null, error: false }); setRevision(v => v + 1); };
  if (state.error) return <section className="oa-card oa-empty" role="alert"><CircleAlert /><h2>{t('Analytics could not be loaded.')}</h2><p>{t('Your organization records are still available in the navigation above.')}</p><button className="pr-button" onClick={retry}><RefreshCw size={14} />{t('Try again')}</button></section>;
  if (!state.data) return <section className="oa-dashboard" aria-busy="true" aria-label={t('Loading organization analytics')}><p role="status">{t('Loading organization analytics')}</p><div className="oa-kpis">{Array.from({ length: 6 }, (_, i) => <div className="oa-card oa-skeleton" key={i} />)}</div></section>;
  const data = state.data, k = data.kpis;
  const formatProgress = value => value == null ? '—' : `${value}%`;
  const summary = [
    ['Total projects', k.projects, 'Organization portfolio', FolderKanban, () => onNavigate('Projects')],
    ['Confirmed progress', formatProgress(k.progress.value), `${k.progress.known}/${k.progress.total} ${t('activities with progress')}`, TrendingUp, () => onNavigate('Reports')],
    ['Delayed activities', k.delayed, 'Confirmed delay signals', CircleAlert, () => onNavigate('Reports')],
    ['Field updates', k.fieldUpdates, 'Current schedule evidence', ClipboardCheck, () => onNavigate('Reports')],
    ['Supervised teams', k.supervisedTeams, `${data.organization.teams} ${t('total teams')}`, Users, () => onNavigate('Teams')],
    ['Workforce', k.workers, `${data.organization.allocatedWorkers} ${t('active allocations')}`, Users, () => onNavigate('Workers')],
  ];
  const time = value => { const d = new Date(value); if (!value || !Number.isFinite(d.getTime())) return t('Timestamp unavailable'); const minutes = Math.round((d.getTime() - Date.parse(data.evaluatedAt)) / 60000); const unit = Math.abs(minutes) < 60 ? 'minute' : Math.abs(minutes) < 1440 ? 'hour' : 'day'; return new Intl.RelativeTimeFormat(locale, { numeric: 'auto' }).format(Math.round(minutes / ({ minute: 1, hour: 60, day: 1440 }[unit])), unit); };
  return <div className="oa-dashboard">
    <div className="oa-context"><span><i className="oa-dot is-primary" />{data.dataLabel}</span><span>{t('As of')} {new Date(data.evaluatedAt).toLocaleString(locale, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}<button type="button" className="oa-icon-button" aria-label={t('Refresh analytics')} onClick={retry}><RefreshCw size={14} /></button></span></div>
    <div className="oa-kpis">{summary.map(([label, value, note, Icon, onClick]) => <button type="button" className="oa-card oa-kpi" key={label} onClick={onClick}><span className="oa-kpi-label">{t(label)}<Icon size={16} /></span><strong>{typeof value === 'number' ? value.toLocaleString(locale) : value}</strong><span className="oa-kpi-note">{t(note)}<ArrowUpRight size={13} /></span></button>)}</div>
    <div className="oa-bar-grid">
      <Panel title={t('Projects by Status')} subtitle={t('Distribution of projects across the organization')}><BarChart items={data.projectStatus} title={t('Projects by Status')} t={t} unit="projects" onSelect={() => onNavigate('Projects')} /></Panel>
      <Panel title={t('Activity Distribution')} subtitle={t('Activities by discipline')}><BarChart items={data.activityDistribution} title={t('Activity Distribution')} t={t} unit="activities" onSelect={() => onNavigate('Reports')} /></Panel>
    </div>
    <div className="oa-primary-grid">
      <Panel title={t('Project Progress Overview')} subtitle={t('Planned vs actual completion across the portfolio')}><CompletionChart data={data.completion} t={t} locale={locale} /></Panel>
      <Panel title={t('Discipline Progress')} subtitle={t('Mean confirmed activity progress')}><div className="oa-disciplines">{data.disciplines.map(item => <div key={item.name}><div className="oa-between"><span>{item.name}</span><strong>{formatProgress(item.value)}</strong></div><ProgressBar value={item.value} label={item.name} /><small>{item.known}/{item.total} {t('activities with progress')}</small></div>)}</div>{!data.disciplines.length && <p className="oa-empty">{t('No scheduled disciplines yet.')}</p>}<p className="oa-note">{t('Unweighted mean of known progress. Missing evidence is excluded, not treated as zero.')}</p></Panel>
    </div>
    <section className="oa-portfolio"><header className="oa-heading"><div><h2>{t('Project Portfolio')}</h2><p>{t('Recorded project status and confirmed execution')}</p></div><button className="oa-link" onClick={() => onNavigate('Projects')}>{t('All projects')}<ArrowUpRight size={15} /></button></header><div className="oa-projects">{data.projects.map(project => { const image = projectImages[project.id]; return <button type="button" className="oa-card oa-project" key={project.id} onClick={() => onOpenProject(project.id)}><div className="oa-project-image">{image && <img src={image.src} alt={image.alt} style={{ objectPosition: image.position }} />}</div><div className="oa-between"><span className="oa-project-code"><FolderKanban size={15} />{project.id}</span><ArrowUpRight size={16} /></div><h3>{project.name}</h3><p className="oa-location"><MapPin size={13} />{project.location || t('Location unavailable')}</p><span className={`oa-badge ${['DELAYED', 'AT_RISK'].includes(project.health) ? 'is-warning' : ''}`}>{t(healthLabels[project.health] || project.health)}</span><div className="oa-between oa-project-value"><span>{t('Confirmed progress')}</span><strong>{formatProgress(project.progress.value)}</strong></div><ProgressBar value={project.progress.value} label={project.name} /><div className="oa-project-footer"><span>{project.activities} {t('activities')}</span><span>{project.progress.known}/{project.progress.total} {t('with evidence')}</span></div><small>{t('Recorded status')}: {t(project.status)}</small></button>; })}</div>{!data.projects.length && <p className="oa-card oa-empty">{t('No projects available. Create a project to begin.')}</p>}</section>
    <div className="oa-bottom-grid">
      <Panel title={t('Recent Field Updates')} subtitle={t('Latest reports on the current schedule')} className="oa-feed-card" action={<Activity size={17} />}><div className="oa-feed">{data.recentUpdates.map(update => <button type="button" className="oa-feed-item" key={update.id} onClick={() => onOpenReport(update.projectId)}><span className="oa-feed-mark"><ClipboardCheck size={15} /></span><div><strong>{update.description}</strong><small>{update.discipline} · {update.projectName}</small><div className="oa-feed-meta"><span className="oa-badge">{t(update.status)}</span><time title={update.submittedAt}>{time(update.submittedAt)}</time></div></div></button>)}</div>{!data.recentUpdates.length && <p className="oa-empty">{t('No field updates recorded yet.')}</p>}</Panel>
      <Panel title={t('Schedule Matching')} subtitle={t('Accepted links and review backlog')}><Ring items={data.matching} title={t('Schedule Matching')} focusLabel="Matched" t={t} /><p className="oa-note">{t('Matched means a reviewed, accepted schedule link.')}</p></Panel>
      <Panel title={t('Activity Status')} subtitle={t('Authoritative execution evidence')}><Ring items={data.activityStatus} title={t('Activity Status')} t={t} /><p className="oa-note">{t('Unknown means confirmed actuals are unavailable.')}</p></Panel>
      <Panel title={t('Key Alerts')} subtitle={t('Existing execution intelligence')}><div className="oa-alerts">{data.alerts.slice(0, 5).map(alert => <button key={alert.type} type="button" onClick={() => onOpenReport(alert.projectId)}><CircleAlert size={16} /><span><strong>{t(alertLabels[alert.type] || alert.type)}</strong><small>{t(alert.severity === 'HIGH' ? 'High priority' : alert.severity === 'MEDIUM' ? 'Requires attention' : 'Review evidence')}</small></span><b>{alert.count}</b></button>)}{!data.alerts.length && <p className="oa-empty">{t('No current execution alerts.')}</p>}</div><button type="button" className="oa-link" onClick={() => onNavigate('Reports')}>{t('View execution report')}<ArrowUpRight size={14} /></button></Panel>
    </div>
    <Panel title={t('Organization attention')} subtitle={t('Ownership, workforce and access')}><div className="oa-organization-strip"><button onClick={() => onNavigate('Registrations')}><ShieldCheck size={17} /><strong>{k.pendingRegistrations}</strong>{t('Pending registrations')}<ArrowUpRight size={14} /></button><button onClick={() => onNavigate('Departments')}><Users size={17} /><strong>{data.organization.departments}</strong>{t('Departments')}<ArrowUpRight size={14} /></button><button onClick={() => onNavigate('People')}><Users size={17} /><strong>{data.organization.employees}</strong>{t('Employees')}<ArrowUpRight size={14} /></button></div>{data.organization.attention.length ? <div className="oa-ownership">{data.organization.attention.map(item => <button key={item.id} onClick={() => onOpenProject(item.id)}><CircleAlert size={14} /><code>{item.id}</code><span>{t(item.reason)}</span><ArrowUpRight size={14} /></button>)}</div> : <p className="oa-note">{t('No recorded attention items.')}</p>}</Panel>
  </div>;
}
