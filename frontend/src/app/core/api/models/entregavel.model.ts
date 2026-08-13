export type TipoEntregavel =
  | 'word_as_is'
  | 'excel_gaps'
  | 'to_be'
  | 'raci'
  | 'dashboard'
  | 'status_semanal'
  | 'pauta';

export type StatusJob = 'pendente' | 'processando' | 'concluido' | 'erro';

export interface TipoEntregavelInfo {
  tipo: TipoEntregavel;
  rotulo: string;
  descricao: string;
  icon: string;
}

export const TIPOS_ENTREGAVEL: TipoEntregavelInfo[] = [
  {
    tipo: 'word_as_is',
    rotulo: 'AS IS',
    descricao: 'Mapeamento do processo atual: subprocessos, gaps e maturidade.',
    icon: 'description',
  },
  {
    tipo: 'excel_gaps',
    rotulo: 'Gaps',
    descricao: 'Lacunas identificadas, classificadas por criticidade e categoria.',
    icon: 'flag',
  },
  {
    tipo: 'to_be',
    rotulo: 'TO BE',
    descricao: 'Proposta de estado futuro com recomendações de médio e longo prazo.',
    icon: 'trending_up',
  },
  {
    tipo: 'raci',
    rotulo: 'Matriz RACI',
    descricao: 'Papéis e responsabilidades por atividade do processo.',
    icon: 'groups',
  },
  {
    tipo: 'dashboard',
    rotulo: 'Dashboard de Maturidade',
    descricao: 'Avaliação de qualidade e profundidade documental do processo.',
    icon: 'speed',
  },
  {
    tipo: 'status_semanal',
    rotulo: 'Status Semanal',
    descricao: 'Resumo executivo de avanços, pendências e riscos do projeto.',
    icon: 'event_note',
  },
  {
    tipo: 'pauta',
    rotulo: 'Pauta de Reunião',
    descricao: 'Roteiro para validar o AS IS com o cliente.',
    icon: 'forum',
  },
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
