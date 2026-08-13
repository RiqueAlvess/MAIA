import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

import { ProcessoRead } from '../../core/api/models/processo.model';
import { ProcessoApiService } from '../../core/api/services/processo.service';
import { PageHeaderService } from '../../core/layout/page-header.service';
import { formatarStatus, statusChipClass } from '../../shared/status-label';

@Component({
  selector: 'maia-processos-global-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatButtonModule, MatFormFieldModule, MatIconModule, MatInputModule],
  templateUrl: './processos-global-list.component.html',
  styleUrl: './processos-global-list.component.scss',
})
export class ProcessosGlobalListComponent implements OnInit {
  readonly formatarStatus = formatarStatus;
  readonly statusChipClass = statusChipClass;

  processos = signal<ProcessoRead[]>([]);
  carregando = signal(true);
  busca = signal('');

  constructor(
    private readonly processoApi: ProcessoApiService,
    private readonly pageHeader: PageHeaderService,
  ) {}

  ngOnInit(): void {
    this.pageHeader.set([{ label: 'Processos' }]);
    this.carregando.set(true);
    this.processoApi.listarTodos().subscribe((processos) => {
      this.processos.set(processos);
      this.carregando.set(false);
    });
  }

  processosFiltrados(): ProcessoRead[] {
    const termo = this.busca().trim().toLowerCase();
    if (!termo) {
      return this.processos();
    }
    return this.processos().filter(
      (processo) =>
        processo.nome.toLowerCase().includes(termo) || (processo.cliente_nome ?? '').toLowerCase().includes(termo),
    );
  }
}
