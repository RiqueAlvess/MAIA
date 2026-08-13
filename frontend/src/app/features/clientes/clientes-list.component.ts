import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';

import { ClienteApiService } from '../../core/api/services/cliente.service';
import { ClienteRead } from '../../core/api/models/cliente.model';

@Component({
  selector: 'maia-clientes-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatTableModule,
  ],
  templateUrl: './clientes-list.component.html',
})
export class ClientesListComponent implements OnInit {
  clientes = signal<ClienteRead[]>([]);
  colunas = ['nome', 'pasta_sharepoint_id', 'criado_em', 'acoes'];

  novoNome = '';
  novaPastaSharepointId = '';
  salvando = false;
  erro: string | null = null;

  constructor(private readonly clienteApi: ClienteApiService) {}

  ngOnInit(): void {
    this.carregar();
  }

  carregar(): void {
    this.clienteApi.listar().subscribe((clientes) => this.clientes.set(clientes));
  }

  criar(): void {
    if (!this.novoNome.trim() || !this.novaPastaSharepointId.trim()) {
      return;
    }
    this.salvando = true;
    this.erro = null;
    this.clienteApi
      .criar({ nome: this.novoNome.trim(), pasta_sharepoint_id: this.novaPastaSharepointId.trim() })
      .subscribe({
        next: () => {
          this.novoNome = '';
          this.novaPastaSharepointId = '';
          this.salvando = false;
          this.carregar();
        },
        error: () => {
          this.erro = 'Não foi possível criar o cliente.';
          this.salvando = false;
        },
      });
  }
}
