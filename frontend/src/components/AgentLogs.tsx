import React from 'react';
import { Terminal } from 'lucide-react';
import type { AgentLog } from '../types/types';

interface AgentLogsProps {
  logs: AgentLog[];
}

const AgentLogs: React.FC<AgentLogsProps> = ({ logs }) => {
  return (
    <div className="glass p-6 rounded-2xl shadow-xl h-[470px] flex flex-col">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Terminal className="w-5 h-5 text-secondary" />
        Agent Activity Logs
      </h2>
      <div className="flex-1 overflow-y-scroll space-y-2 pr-2 custom-scrollbar">
        {logs.length === 0 && (
          <div className="text-slate-500 italic text-center mt-10">No activity yet. Standby...</div>
        )}
        {logs.map((log, index) => (
          <div key={index} className="flex gap-3 text-sm animate-in fade-in slide-in-from-left-2 duration-300">
            <span className="text-slate-500 min-w-[60px]">{log.timestamp}</span>
            <span className="text-primary font-mono whitespace-nowrap">[{log.node}]</span>
            <span className="text-slate-300 break-words overflow-hidden">{log.msg}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentLogs;
