export interface ProcessoCreate {
  cliente_id: string;
  nome: string;
}

export interface ProcessoRead {
  id: string;
  cliente_id: string;
  nome: string;
  status_as_is: string;
  status_to_be: string;
  criado_em: string;
}
