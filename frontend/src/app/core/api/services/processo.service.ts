import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { ProcessoCreate, ProcessoRead } from '../models/processo.model';

@Injectable({ providedIn: 'root' })
export class ProcessoApiService {
  private readonly baseUrl = `${environment.apiUrl}/processos`;

  constructor(private readonly http: HttpClient) {}

  listarPorCliente(clienteId: string): Observable<ProcessoRead[]> {
    const params = new HttpParams().set('cliente_id', clienteId);
    return this.http.get<ProcessoRead[]>(this.baseUrl, { params });
  }

  listarTodos(): Observable<ProcessoRead[]> {
    return this.http.get<ProcessoRead[]>(this.baseUrl);
  }

  obter(processoId: string): Observable<ProcessoRead> {
    return this.http.get<ProcessoRead>(`${this.baseUrl}/${processoId}`);
  }

  criar(dados: ProcessoCreate): Observable<ProcessoRead> {
    return this.http.post<ProcessoRead>(this.baseUrl, dados);
  }
}
