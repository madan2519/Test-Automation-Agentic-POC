import React, { useState } from 'react';
import { Play, CheckCircle2, XCircle, Clock, FlaskConical, ChevronDown, ChevronUp, FileCode, AlertTriangle, Filter } from 'lucide-react';
import type { ExecutionResult, TestCaseResult } from '../types/types';

interface ExecutionResultsProps {
  results: ExecutionResult | null;
}

type FilterType = 'all' | 'passed' | 'failed';

const statusConfig: Record<string, { icon: React.ReactNode; color: string; bg: string; label: string }> = {
  passed: {
    icon: <CheckCircle2 className="w-4 h-4" />,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/15 border-emerald-500/25',
    label: 'Passed',
  },
  failed: {
    icon: <XCircle className="w-4 h-4" />,
    color: 'text-red-400',
    bg: 'bg-red-500/15 border-red-500/25',
    label: 'Failed',
  },
  error: {
    icon: <AlertTriangle className="w-4 h-4" />,
    color: 'text-amber-400',
    bg: 'bg-amber-500/15 border-amber-500/25',
    label: 'Error',
  },
  skipped: {
    icon: <Clock className="w-4 h-4" />,
    color: 'text-slate-400',
    bg: 'bg-slate-500/15 border-slate-500/25',
    label: 'Skipped',
  },
};

const TestCaseRow: React.FC<{ tc: TestCaseResult; index: number }> = ({ tc, index }) => {
  const [expanded, setExpanded] = useState(false);
  const cfg = statusConfig[tc.status] || statusConfig.error;

  return (
    <>
      <tr
        className="border-b border-white/5 hover:bg-white/[0.03] transition-colors cursor-pointer"
        onClick={() => tc.error_message && setExpanded(!expanded)}
      >
        <td className="py-3 px-4 text-slate-500 text-sm font-mono">{index}</td>
        <td className="py-3 px-4 text-slate-200 text-sm font-medium box-text">{tc.name}</td>
        <td className="py-3 px-4">
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${cfg.bg} ${cfg.color}`}>
            {cfg.icon}
            {cfg.label}
          </span>
        </td>
        <td className="py-3 px-4 text-slate-400 text-sm font-mono">{tc.duration}</td>
        <td className="py-3 px-4">
          {tc.error_message ? (
            <button className="text-red-400/70 hover:text-red-400 transition-colors flex items-center gap-1 text-xs">
              {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              {expanded ? 'Hide' : 'Details'}
            </button>
          ) : (
            <span className="text-slate-600 text-xs">—</span>
          )}
        </td>
      </tr>
      {expanded && tc.error_message && (
        <tr className="border-b border-white/5">
          <td colSpan={5} className="px-4 py-3">
            <pre className="text-xs text-red-300/80 bg-red-500/5 border border-red-500/10 p-3 rounded-lg overflow-x-auto font-mono whitespace-pre-wrap max-h-[150px] overflow-y-auto custom-scrollbar">
              {tc.error_message}
            </pre>
          </td>
        </tr>
      )}
    </>
  );
};

const ExecutionResults: React.FC<ExecutionResultsProps> = ({ results }) => {
  const [filter, setFilter] = useState<FilterType>('all');
  const [showLogs, setShowLogs] = useState(false);

  console.log('ExecutionResults rendering with data:', results);

  if (!results) {
    return (
      <div className="glass p-6 rounded-2xl shadow-xl flex flex-col items-center justify-center text-center animate-in fade-in duration-500 h-[500px]">
        <div className="p-4 bg-primary/10 rounded-full mb-4">
          <Play className="w-10 h-10 text-primary animate-pulse" />
        </div>
        <h2 className="text-xl font-semibold text-white mb-2">Execution Results Standby</h2>
        <p className="text-slate-400 text-sm max-w-[250px]">
          No execution data available. Start an automation request to see results here.
        </p>
      </div>
    );
  }

  const overallPassed = results.failed === 0;
  const testCases = results.test_cases || [];

  const filteredCases = testCases.filter((tc) => {
    if (filter === 'all') return true;
    if (filter === 'passed') return tc.status === 'passed';
    return tc.status === 'failed' || tc.status === 'error';
  });

  return (
    <div className="glass p-6 rounded-2xl shadow-xl animate-in zoom-in duration-500 h-[500px] flex flex-col">
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-6">
        {/* Overall Status Banner */}
        <div
          className={`flex items-center justify-between p-4 rounded-xl border ${overallPassed
            ? 'bg-emerald-500/10 border-emerald-500/20'
            : 'bg-red-500/10 border-red-500/20'
            }`}
        >
          <div className="flex items-center gap-3">
            {overallPassed ? (
              <CheckCircle2 className="w-7 h-7 text-emerald-400" />
            ) : (
              <XCircle className="w-7 h-7 text-red-400" />
            )}
            <div>
              <h2 className={`text-xl font-bold ${overallPassed ? 'text-emerald-400' : 'text-red-400'}`}>
                {overallPassed ? 'ALL TESTS PASSED' : 'TESTS FAILED'}
              </h2>
              <p className="text-sm text-slate-400 mt-0.5">
                {results.tests_run} test{results.tests_run !== 1 ? 's' : ''} executed in {results.execution_time}
              </p>
            </div>
          </div>
          <div className={`text-3xl font-extrabold ${overallPassed ? 'text-emerald-400' : 'text-red-400'}`}>
            {results.passed}/{results.tests_run}
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-4 rounded-xl bg-white/5 border border-white/10">
            <div className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-1">Total</div>
            <div className="text-2xl font-bold text-slate-200 flex items-center gap-2">
              <FlaskConical className="w-5 h-5 text-blue-400" /> {results.tests_run}
            </div>
          </div>
          <div className="p-4 rounded-xl bg-white/5 border border-white/10">
            <div className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-1">Passed</div>
            <div className="text-2xl font-bold text-emerald-400 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5" /> {results.passed}
            </div>
          </div>
          <div className="p-4 rounded-xl bg-white/5 border border-white/10">
            <div className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-1">Failed</div>
            <div className="text-2xl font-bold text-red-400 flex items-center gap-2">
              <XCircle className="w-5 h-5" /> {results.failed}
            </div>
          </div>
          <div className="p-4 rounded-xl bg-white/5 border border-white/10">
            <div className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-1">Duration</div>
            <div className="text-2xl font-bold text-blue-400 flex items-center gap-2">
              <Clock className="w-5 h-5" /> {results.execution_time}
            </div>
          </div>
        </div>

        {/* Filter Pills + Test Cases Table */}
        <div>
          <div className="flex flex-col gap-3 mb-4">
            <h3 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
              <FlaskConical className="w-5 h-5 text-primary" />
              Test Case Results
            </h3>
            <div className="flex flex-wrap items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-slate-500 mr-1" />
              {(['all', 'passed', 'failed'] as FilterType[]).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${filter === f
                    ? f === 'passed'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : f === 'failed'
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                        : 'bg-primary/20 text-primary border border-primary/30'
                    : 'text-slate-500 hover:text-slate-300 border border-transparent hover:border-white/10'
                    }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-white/10 overflow-x-auto custom-scrollbar">
            <table className="w-full text-left min-w-[300px]">
              <thead>
                <tr className="bg-white/[0.03] border-b border-white/10">
                  <th className="py-2.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider w-12">#</th>
                  <th className="py-2.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Test Case</th>
                  <th className="py-2.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider w-28">Status</th>
                  <th className="py-2.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider w-24">Duration</th>
                  <th className="py-2.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider w-20">Error</th>
                </tr>
              </thead>
              <tbody>
                {filteredCases && filteredCases.length > 0 ? (
                  filteredCases.map((tc, i) => (
                    <TestCaseRow key={i} tc={tc} index={i + 1} />
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-500 text-sm italic">
                      No test cases match the current filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Expandable Logs Section */}
        <div>
          <button
            onClick={() => setShowLogs(!showLogs)}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            <FileCode className="w-4 h-4" />
            Full Execution Logs
            {showLogs ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {showLogs && (
            <pre className="mt-3 p-4 rounded-xl bg-black/40 border border-white/5 font-mono text-xs text-slate-400 overflow-x-auto max-h-[250px] overflow-y-auto custom-scrollbar whitespace-pre-wrap">
              {results.logs}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExecutionResults;
