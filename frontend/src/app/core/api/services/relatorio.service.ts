import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { TipoEntregavel } from '../models/entregavel.model';
import { EntregavelHistoricoRead, RelatorioEmailRequest } from '../models/relatorio.model';

@Injectable({ providedIn: 'root' })
export class RelatorioApiService {
  private readonly baseUrl = `${environment.apiUrl}/relatorios`;

  constructor(private readonly http: HttpClient) {}

  listarHistorico(filtros?: { clienteId?: string; tipo?: TipoEntregavel }): Observable<EntregavelHistoricoRead[]> {
    let params = new HttpParams();
    if (filtros?.clienteId) {
      params = params.set('cliente_id', filtros.clienteId);
    }
    if (filtros?.tipo) {
      params = params.set('tipo', filtros.tipo);
    }
    return this.http.get<EntregavelHistoricoRead[]>(`${this.baseUrl}/entregaveis`, { params });
  }

  enviarEmail(dados: RelatorioEmailRequest): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/enviar-email`, dados);
  }
}
