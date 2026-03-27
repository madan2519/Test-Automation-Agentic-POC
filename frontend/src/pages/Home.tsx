import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { wsService } from '../services/websocketService';
import JiraInput from '../components/JiraInput';
import AgentLogs from '../components/AgentLogs';
import ExecutionResults from '../components/ExecutionResults';
import JiraTicketDetails from '../components/JiraTicketDetails';
import { Bot, Sparkles } from 'lucide-react';
import type { AgentLog, ExecutionResult, AutomationRequest, JiraContext } from '../types/types';

const Home: React.FC = () => {
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [results, setResults] = useState<ExecutionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [jiraData, setJiraData] = useState<JiraContext | null>(null);
  const [connected, setConnected] = useState(false);
  const [currentJiraId, setCurrentJiraId] = useState<string | null>(null);

  // Use refs to access latest state in stable listeners
  const loadingRef = useRef(loading);
  const jiraIdRef = useRef(currentJiraId);

  useEffect(() => {
    loadingRef.current = loading;
    jiraIdRef.current = currentJiraId;
  }, [loading, currentJiraId]);

  const syncState = async (jiraId: string) => {
    try {
      console.log(`Syncing state for ${jiraId}...`);
      const resp = await axios.get(`http://localhost:8000/automation-status/${jiraId}`);
      const { logs: cachedLogs, result: cachedResult } = resp.data;

      if (cachedLogs && cachedLogs.length > 0) {
        const reversed = [...cachedLogs].reverse();
        setLogs(reversed.map((l: any) => ({
          ...l,
          timestamp: l.timestamp || new Date().toLocaleTimeString()
        })));

        const lastWithData = cachedLogs.find((l: any) => l.jira_data);
        if (lastWithData) setJiraData(lastWithData.jira_data);
      }

      if (cachedResult) {
        // The cached result could be from execution_finished (flat fields + jira_id)
        // or workflow_finished (nested execution_results)
        const execData = cachedResult.execution_results || cachedResult;
        // Strip non-ExecutionResult fields that were added for caching
        const { jira_id: _jid, status: _st, jira_data: cachedJira, ...cleanResult } = execData;
        if (cleanResult.tests_run !== undefined) {
          setResults(cleanResult);
        }
        if (cachedJira) {
          setJiraData(cachedJira);
        }
        setLoading(false);
      }
    } catch (err) {
      console.error('Failed to sync state:', err);
    }
  };

  // Polling fallback: while loading, poll for results every 5s
  useEffect(() => {
    if (!loading || !currentJiraId) return;

    const interval = setInterval(() => {
      syncState(currentJiraId);
    }, 5000);

    return () => clearInterval(interval);
  }, [loading, currentJiraId]);

  useEffect(() => {
    // Connect only once on mount
    wsService.connect('ws://127.0.0.1:8000/ws');

    wsService.on('connected', () => {
      console.log('WS event: connected');
      setConnected(true);
      if (loadingRef.current && jiraIdRef.current) {
        syncState(jiraIdRef.current);
      }
    });

    wsService.on('disconnected', () => {
      console.log('WS event: disconnected');
      setConnected(false);
    });

    wsService.on('agent_update', (data) => {
      const newLog: AgentLog = {
        ...data,
        timestamp: new Date().toLocaleTimeString(),
      };
      setLogs((prev) => [newLog, ...prev]);

      if (data.jira_data) {
        setJiraData(data.jira_data);
      }
    });

    wsService.on('execution_finished', (data) => {
      setResults(data);
      setLoading(false);
    });

    wsService.on('workflow_finished', (data) => {
      if (data.execution_results) setResults(data.execution_results);
      if (data.jira_data) setJiraData(data.jira_data);
      setLoading(false);
    });

    return () => {
      wsService.clearListeners();
    };
  }, []); // Run only once

  const handleStartAutomation = async (data: AutomationRequest) => {
    setCurrentJiraId(data.jira_id);
    setLogs([{ timestamp: new Date().toLocaleTimeString(), node: 'System', msg: 'Initiating request...', jira_id: data.jira_id }]);
    setResults(null);
    setJiraData(null);
    setLoading(true);
    try {
      await axios.post('http://localhost:8000/start-automation', data);
    } catch (error) {
      console.error('Error starting automation:', error);
      setLoading(false);
      alert('Failed to connect to backend.');
    }
  };

  return (
    <div className="min-h-screen p-8 max-w-7xl mx-auto">
      <header className="mb-12 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-extrabold flex items-center gap-3">
            <Bot className="w-10 h-10 text-primary" />
            <span className="gradient-text">AgenticQA</span>
          </h1>
          <p className="text-slate-400 mt-2">Autonomous Multi-Agent AI Automation Platform</p>
        </div>
        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full border ${connected ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-red-500/10 border-red-500/20 text-red-500'}`}>
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-sm font-medium">{connected ? 'Live Connection Active' : 'Backend Offline'}</span>
          </div>
          <div className="flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-full border border-primary/20">
            <Sparkles className="w-4 h-4 text-primary animate-pulse" />
            <span className="text-sm font-medium text-primary">AI Orchestration Active</span>
          </div>
        </div>
      </header>

      <div className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-4 transition-all duration-300">
            <JiraInput onSubmit={handleStartAutomation} isLoading={loading} />
          </div>
          <div className="lg:col-span-8">
            <AgentLogs logs={logs} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-7">
            <ExecutionResults results={results} />
          </div>
          <div className="lg:col-span-12 xl:col-span-5">
            <JiraTicketDetails data={jiraData} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
