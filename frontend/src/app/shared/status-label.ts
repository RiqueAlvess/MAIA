const ROTULOS_CONHECIDOS: Record<string, string> = {
  nao_iniciado: 'Não iniciado',
  em_andamento: 'Em andamento',
  concluido: 'Concluído',
  pendente: 'Pendente',
  bloqueado: 'Bloqueado',
};

export function formatarStatus(status: string): string {
  const conhecido = ROTULOS_CONHECIDOS[status.toLowerCase()];
  if (conhecido) {
    return conhecido;
  }
  return status
    .split('_')
    .filter(Boolean)
    .map((parte) => parte.charAt(0).toUpperCase() + parte.slice(1))
    .join(' ');
}

export function statusChipClass(status: string): string {
  const valor = status.toLowerCase();
  if (valor.includes('conclu')) {
    return 'status-chip--success';
  }
  if (valor.includes('andamento') || valor.includes('progresso') || valor.includes('processando')) {
    return 'status-chip--info';
  }
  if (valor.includes('bloque') || valor.includes('erro')) {
    return 'status-chip--danger';
  }
  if (valor.includes('pendente') || valor.includes('aguard')) {
    return 'status-chip--warning';
  }
  return 'status-chip--neutral';
}
