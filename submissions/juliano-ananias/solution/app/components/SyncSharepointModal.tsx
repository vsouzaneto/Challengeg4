'use client';

import React, { useState, useEffect } from 'react';
import { G4Logo, CheckCircleIcon, CloseIcon, RefreshIcon } from './Icons';

interface SyncModalProps {
  onClose: () => void;
  updatedCount: number;
}

export default function SyncSharepointModal({ onClose, updatedCount }: SyncModalProps) {
  const [syncStep, setSyncStep] = useState(0);

  useEffect(() => {
    const timer1 = setTimeout(() => setSyncStep(1), 700);
    const timer2 = setTimeout(() => setSyncStep(2), 1600);
    const timer3 = setTimeout(() => setSyncStep(3), 2400);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 backdrop-blur-sm p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden text-slate-800 animate-in fade-in zoom-in-95 duration-200">
        <div className="p-5 bg-slate-950 text-white flex justify-between items-center border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <G4Logo className="w-7 h-7 text-xs" />
            <h3 className="text-sm font-bold">G4 CRM & SharePoint Sync</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white rounded-lg transition"
          >
            <CloseIcon className="w-4 h-4" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                  syncStep >= 1 ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-500'
                }`}
              >
                {syncStep >= 1 ? '✓' : '1'}
              </div>
              <span className="text-xs font-medium text-slate-700">
                Conectando ao catálogo de listas SharePoint...
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                  syncStep >= 2 ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-500'
                }`}
              >
                {syncStep >= 2 ? '✓' : '2'}
              </div>
              <span className="text-xs font-medium text-slate-700">
                Sincronizando {updatedCount > 0 ? updatedCount : '2.089'} registros de pipeline e apontamentos...
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                  syncStep >= 3 ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-500'
                }`}
              >
                {syncStep >= 3 ? '✓' : '3'}
              </div>
              <span className="text-xs font-medium text-slate-700">
                Recálculo de Lead Scores e Filas RevOps finalizado!
              </span>
            </div>
          </div>

          {syncStep >= 3 && (
            <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-800 text-xs font-medium flex items-center gap-2 animate-in fade-in">
              <CheckCircleIcon className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <span>Base sincronizada com sucesso com o CRM corporativo.</span>
            </div>
          )}
        </div>

        <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            disabled={syncStep < 3}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl transition disabled:opacity-50"
          >
            {syncStep < 3 ? 'Sincronizando...' : 'Concluído'}
          </button>
        </div>
      </div>
    </div>
  );
}
