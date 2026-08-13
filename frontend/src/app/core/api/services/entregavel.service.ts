import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { EntregavelGerarRequest, JobGeracaoRead, TipoEntregavel } from '../models/entregavel.model';

@Injectable({ providedIn: 'root' })
export class EntregavelApiService {
  private readonly baseUrl = `${environment.apiUrl}/entregaveis`;

  constructor(private readonly http: HttpClient) {}

  gerar(tipo: TipoEntregavel, processoId: string): Observable<JobGeracaoRead> {
    const corpo: EntregavelGerarRequest = { processo_id: processoId };
    return this.http.post<JobGeracaoRead>(`${this.baseUrl}/gerar/${tipo}`, corpo);
  }

  obterStatusJob(jobId: string): Observable<JobGeracaoRead> {
    return this.http.get<JobGeracaoRead>(`${this.baseUrl}/jobs/${jobId}`);
  }
}
