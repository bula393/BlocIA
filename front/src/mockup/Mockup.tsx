import { useEffect, useState } from 'react';
import { Workspace } from './Workspace';
import { Landing, type LandingAction } from '../pages/Landing';
import './mockup.css';

type View = LandingAction;
const views: LandingAction[] = ['chat', 'profile', 'providers', 'usage', 'login', 'register', 'google'];
const readView = () => {
  const hash = window.location.hash.replace('#/', '');
  return views.includes(hash as View) ? hash as View : null;
};
export function Mockup() {
  const [view, setView] = useState<View | null>(readView);
  useEffect(() => {
    const update = () => { setView(readView()); };
    window.addEventListener('hashchange', update);
    const oldTitle = document.title;
    document.title = 'BloqIA — Un espacio para pensar mejor';
    return () => { window.removeEventListener('hashchange', update); document.title = oldTitle; };
  }, []);
  const open = (next: View) => { window.location.hash = `/${next}`; setView(next); window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior }); };
  const home = () => { window.history.pushState({}, '', window.location.pathname); setView(null); window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior }); };
  return <div className="mockup-app">{view ? <Workspace initialView={view} onHome={home} /> : <Landing open={open} />}</div>;
}
