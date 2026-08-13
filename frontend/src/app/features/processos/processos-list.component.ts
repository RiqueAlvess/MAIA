import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';

import { ProcessoApiService } from '../../core/api/services/processo.service';
import { ProcessoRead } from '../../core/api/models/processo.model';

@Component({
  selector: 'maia-processos-list',
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
  templateUrl: './processos-list.component.html',
})
export class ProcessosListComponent implements OnInit {
  processos = signal<ProcessoRead[]>([]);
  colunas = ['nome', 'status_as_is', 'status_to_be', 'acoes'];

  clienteId = '';
  novoNome = '';
  salvando = false;
  erro: string | null = null;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly processoApi: ProcessoApiService,
  ) {}

  ngOnInit(): void {
    this.clienteId = this.route.snapshot.paramMap.get('clienteId') ?? '';
    this.carregar();
  }

  carregar(): void {
    if (!this.clienteId) {
      return;
    }
    this.processoApi.listarPorCliente(this.clienteId).subscribe((processos) => this.processos.set(processos));
  }

  criar(): void {
    if (!this.novoNome.trim()) {
      return;
    }
    this.salvando = true;
    this.erro = null;
    this.processoApi.criar({ cliente_id: this.clienteId, nome: this.novoNome.trim() }).subscribe({
      next: () => {
        this.novoNome = '';
        this.salvando = false;
        this.carregar();
      },
      error: () => {
        this.erro = 'Não foi possível criar o processo.';
        this.salvando = false;
      },
    });
  }
}
