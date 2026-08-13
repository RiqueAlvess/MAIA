export type TipoEntregavel =
  | 'word_as_is'
  | 'excel_gaps'
  | 'to_be'
  | 'raci'
  | 'dashboard'
  | 'status_semanal'
  | 'pauta';

export type StatusJob = 'pendente' | 'processando' | 'concluido' | 'erro';

export const TIPOS_ENTREGAVEL: { tipo: TipoEntregavel; rotulo: string }[] = [
  { tipo: 'word_as_is', rotulo: 'AS IS' },
  { tipo: 'excel_gaps', rotulo: 'Gaps' },
  { tipo: 'to_be', rotulo: 'TO BE' },
  { tipo: 'raci', rotulo: 'Matriz RACI' },
  { tipo: 'dashboard', rotulo: 'Dashboard de Maturidade' },
  { tipo: 'status_semanal', rotulo: 'Status Semanal' },
  { tipo: 'pauta', rotulo: 'Pauta de Reunião' },
];

export interface EntregavelGerarRequest {
  processo_id: string;
}

export interface EntregavelRead {
  id: string;
  processo_id: string;
  tipo: TipoEntregavel;
  gerado_em: string | null;
}

export interface JobGeracaoRead {
  id: string;
  entregavel_id: string;
  status: StatusJob;
  log: string;
  criado_em: string;
  atualizado_em: string;
}
