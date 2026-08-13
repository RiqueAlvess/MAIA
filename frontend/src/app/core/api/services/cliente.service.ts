import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { ClienteCreate, ClienteRead } from '../models/cliente.model';

@Injectable({ providedIn: 'root' })
export class ClienteApiService {
  private readonly baseUrl = `${environment.apiUrl}/clientes`;

  constructor(private readonly http: HttpClient) {}

  listar(): Observable<ClienteRead[]> {
    return this.http.get<ClienteRead[]>(this.baseUrl);
  }

  obter(clienteId: string): Observable<ClienteRead> {
    return this.http.get<ClienteRead>(`${this.baseUrl}/${clienteId}`);
  }

  criar(dados: ClienteCreate): Observable<ClienteRead> {
    return this.http.post<ClienteRead>(this.baseUrl, dados);
  }

  atualizarDestinatarios(clienteId: string, destinatariosRelatorio: string): Observable<ClienteRead> {
    return this.http.patch<ClienteRead>(`${this.baseUrl}/${clienteId}/destinatarios`, {
      destinatarios_relatorio: destinatariosRelatorio,
    });
  }
}
