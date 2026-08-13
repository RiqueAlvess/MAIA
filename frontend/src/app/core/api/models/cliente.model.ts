export interface ClienteCreate {
  nome: string;
  pasta_sharepoint_id: string;
}

export interface ClienteRead {
  id: string;
  nome: string;
  pasta_sharepoint_id: string;
  criado_em: string;
}
