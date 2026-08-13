import { StatusJob, TipoEntregavel } from './entregavel.model';

export interface EntregavelHistoricoRead {
  id: string;
  tipo: TipoEntregavel;
  processo_id: string;
  processo_nome: string;
  cliente_id: string;
  cliente_nome: string;
  gerado_em: string | null;
  status: StatusJob | null;
  status_log: string;
}

export interface RelatorioEmailRequest {
  cliente_id: string;
  processo_id?: string | null;
  destinatarios?: string[] | null;
}

export interface StatusIntegracoesRead {
  ambiente: string;
  ai_configurado: boolean;
  graph_configurado: boolean;
  auth_configurado: boolean;
  email_configurado: boolean;
}
