import React from 'react';
import { FileText, AlignLeft, CheckCircle2, ListOrdered } from 'lucide-react';
import type { JiraContext } from '../types/types';

interface JiraTicketDetailsProps {
    data: JiraContext | null;
}

const JiraTicketDetails: React.FC<JiraTicketDetailsProps> = ({ data }) => {
    if (!data) {
        return (
            <div className="glass p-6 rounded-2xl shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-500 h-[500px] flex flex-col items-center justify-center text-center">
                <div className="p-4 bg-primary/10 rounded-full mb-4">
                    <FileText className="w-10 h-10 text-primary animate-pulse" />
                </div>
                <h2 className="text-xl font-semibold text-white mb-2">Jira Description Standby</h2>
                <p className="text-slate-400 text-sm max-w-[250px]">
                    Waiting for Jira Ticket ID to fetch and display ticket details...
                </p>
            </div>
        );
    }

    return (
        <div className="glass p-6 rounded-2xl shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-500 h-[500px] overflow-y-auto custom-scrollbar">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-primary/10 rounded-lg">
                    <FileText className="w-6 h-6 text-primary" />
                </div>
                <h2 className="text-xl font-bold text-white">{data.summary}</h2>
            </div>

            <div className="space-y-6">
                <section>
                    <div className="flex items-center gap-2 mb-2 text-slate-300 font-semibold">
                        <AlignLeft className="w-4 h-4" />
                        <h3>Description</h3>
                    </div>
                    <div className="text-slate-400 bg-white/5 p-4 rounded-xl border border-white/10 text-sm leading-relaxed whitespace-pre-wrap box-text">
                        {data.description || "No description provided."}
                    </div>
                </section>

                {data.acceptance_criteria.length > 0 && (
                    <section>
                        <div className="flex items-center gap-2 mb-2 text-slate-300 font-semibold">
                            <CheckCircle2 className="w-4 h-4 text-green-500" />
                            <h3>Acceptance Criteria</h3>
                        </div>
                        <ul className="space-y-2">
                            {data.acceptance_criteria.map((item, index) => (
                                <li key={index} className="flex gap-3 text-sm text-slate-400 bg-white/5 p-3 rounded-lg border border-white/5 box-text">
                                    <span className="text-primary font-bold">•</span>
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </section>
                )}

                {data.steps.length > 0 && (
                    <section>
                        <div className="flex items-center gap-2 mb-2 text-slate-300 font-semibold">
                            <ListOrdered className="w-4 h-4 text-blue-500" />
                            <h3>Steps to Reproduce</h3>
                        </div>
                        <div className="space-y-2">
                            {data.steps.map((step, index) => (
                                <div key={index} className="flex gap-4 text-sm text-slate-400 bg-white/5 p-3 rounded-lg border border-white/5 box-text">
                                    <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-primary/20 rounded-full text-primary text-xs font-bold">
                                        {index + 1}
                                    </span>
                                    <span className="pt-0.5">{step}</span>
                                </div>
                            ))}
                        </div>
                    </section>
                )}
            </div>
        </div>
    );
};

export default JiraTicketDetails;
