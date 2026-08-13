import React, { useState } from 'react';
import { FileText, CheckCircle, AlertCircle, Download, ExternalLink } from 'lucide-react';

export const DocumentChecklist = ({ documents = [], serviceName = '' }) => {
  const [checkedDocs, setCheckedDocs] = useState({});

  const toggleCheck = (index) => {
    setCheckedDocs((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const totalMandatory = documents.filter((d) => d.mandatory).length;
  const checkedMandatory = documents.filter((d, i) => d.mandatory && checkedDocs[i]).length;
  const isReady = checkedMandatory === totalMandatory;

  return (
    <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 font-heading">
            <FileText className="w-5 h-5 text-saffron-400" />
            Required Documents Checklist
          </h3>
          <p className="text-xs text-slate-400">Verify your document readiness before starting application</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${isReady ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
          {checkedMandatory} / {totalMandatory} Mandatory Ready
        </div>
      </div>

      <div className="space-y-3">
        {documents.map((doc, index) => {
          const isChecked = !!checkedDocs[index];
          return (
            <div
              key={index}
              onClick={() => toggleCheck(index)}
              className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-start justify-between gap-3 ${
                isChecked
                  ? 'bg-emerald-500/5 border-emerald-500/30 text-slate-200'
                  : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300'
              }`}
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => toggleCheck(index)}
                  className="mt-1 w-4 h-4 rounded text-saffron-500 focus:ring-saffron-500 border-slate-700 bg-slate-900 cursor-pointer"
                />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-slate-100">{doc.name}</span>
                    {doc.mandatory ? (
                      <span className="text-[10px] uppercase font-bold text-red-400 bg-red-500/10 border border-red-500/20 px-1.5 py-0.5 rounded">
                        Mandatory
                      </span>
                    ) : (
                      <span className="text-[10px] uppercase font-bold text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                        Optional
                      </span>
                    )}
                  </div>
                  {doc.description && (
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed">{doc.description}</p>
                  )}
                </div>
              </div>

              {doc.sample_url && (
                <a
                  href={doc.sample_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="inline-flex items-center gap-1 text-xs text-saffron-400 hover:text-saffron-300 hover:underline bg-saffron-500/10 px-2.5 py-1.5 rounded-lg border border-saffron-500/20 shrink-0"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Sample</span>
                </a>
              )}
            </div>
          );
        })}
      </div>

      {!isReady && (
        <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
          <span>Please collect all mandatory documents to avoid rejection by Tahsildar / Verification Officer.</span>
        </div>
      )}
    </div>
  );
};
