import React, { useState } from 'react';
import { Send } from 'lucide-react';

interface JiraInputProps {
  onSubmit: (data: any) => void;
  isLoading: boolean;
}

const JiraInput: React.FC<JiraInputProps> = ({ onSubmit, isLoading }) => {
  const [jiraId, setJiraId] = useState('');
  const [platform, setPlatform] = useState('WEB');
  const [language, setLanguage] = useState('Python');
  const [framework, setFramework] = useState('Playwright');
  const [browser, setBrowser] = useState('Chrome');
  const [device, setDevice] = useState('');

  const handlePlatformChange = (val: string) => {
    setPlatform(val);
    if (val === 'WEB') {
      setBrowser('Chrome');
      setDevice('');
    } else if (val === 'ANDROID') {
      setBrowser('');
      setDevice('PIXEL 5');
    } else if (val === 'IOS') {
      setBrowser('');
      setDevice('iPhone 13');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      jira_id: jiraId,
      platform,
      language,
      framework,
      browser: browser || undefined,
      device: device || undefined,
      environment: 'qa'
    });
  };

  return (
    <div className="glass p-6 rounded-2xl shadow-xl h-[470px] overflow-y-auto custom-scrollbar">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Send className="w-5 h-5 text-primary" />
        New Automation Request
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Jira Ticket ID</label>
            <input
              type="text"
              value={jiraId}
              onChange={(e) => setJiraId(e.target.value)}
              placeholder="e.g. PLAT-123"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50 box-text"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Platform</label>
            <select
              value={platform}
              onChange={(e) => handlePlatformChange(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 cursor-pointer"
            >
              <option value="WEB">WEB</option>
              <option value="ANDROID">ANDROID</option>
              <option value="IOS">IOS</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {platform === 'WEB' && (
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Browser</label>
              <select
                value={browser}
                onChange={(e) => setBrowser(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 cursor-pointer animate-in fade-in slide-in-from-top-1"
              >
                <option value="Chrome">Chrome</option>
                <option value="Edge">Edge</option>
              </select>
            </div>
          )}

          {(platform === 'ANDROID' || platform === 'IOS') && (
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Device</label>
              <select
                value={device}
                onChange={(e) => setDevice(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 cursor-pointer animate-in fade-in slide-in-from-top-1"
              >
                {platform === 'ANDROID' ? (
                  <option value="PIXEL 5">PIXEL 5</option>
                ) : (
                  <>
                    <option value="iPhone 13">iPhone 13</option>
                    <option value="iPhone 12">iPhone 12</option>
                  </>
                )}
              </select>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 cursor-pointer"
            >
              <option value="Python">Python</option>
              <option value="Java">Java</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">Framework</label>
          <select
            value={framework}
            onChange={(e) => setFramework(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 cursor-pointer"
          >
            <option value="Playwright">Playwright</option>
            <option value="Selenium">Selenium</option>
            <option value="Appium">Appium</option>
            <option value="Robot Framework">Robot</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-primary to-secondary text-white font-semibold py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 mt-2 shadow-lg shadow-primary/20"
        >
          {isLoading ? 'Starting Agents...' : 'Run Automation'}
        </button>
      </form>
    </div>
  );
};

export default JiraInput;
