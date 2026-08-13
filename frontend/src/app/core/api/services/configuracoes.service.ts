import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { StatusIntegracoesRead } from '../models/relatorio.model';

@Injectable({ providedIn: 'root' })
export class ConfiguracoesApiService {
  private readonly baseUrl = `${environment.apiUrl}/configuracoes`;

  constructor(private readonly http: HttpClient) {}

  obterStatus(): Observable<StatusIntegracoesRead> {
    return this.http.get<StatusIntegracoesRead>(`${this.baseUrl}/status`);
  }
}
