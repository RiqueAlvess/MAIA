import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';

import { ClienteRead } from '../../core/api/models/cliente.model';
import { ProcessoRead } from '../../core/api/models/processo.model';
import { ClienteApiService } from '../../core/api/services/cliente.service';
import { ProcessoApiService } from '../../core/api/services/processo.service';
import { PageHeaderService } from '../../core/layout/page-header.service';
import { DIALOG_WIDTH } from '../../shared/dialog-config';
import { formatarStatus, statusChipClass } from '../../shared/status-label';
import { ProcessoFormDialogComponent } from './processo-form-dialog.component';

@Component({
  selector: 'maia-processos-list',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatDialogModule, MatIconModule],
  templateUrl: './processos-list.component.html',
  styleUrl: './processos-list.component.scss',
})
export class ProcessosListComponent implements OnInit {
  readonly formatarStatus = formatarStatus;
  readonly statusChipClass = statusChipClass;

  clienteId = '';
  cliente = signal<ClienteRead | null>(null);
  processos = signal<ProcessoRead[]>([]);
  carregando = signal(true);

  constructor(
    private readonly route: ActivatedRoute,
    private readonly clienteApi: ClienteApiService,
    private readonly processoApi: ProcessoApiService,
    private readonly dialog: MatDialog,
    private readonly pageHeader: PageHeaderService,
  ) {}

  ngOnInit(): void {
    this.clienteId = this.route.snapshot.paramMap.get('clienteId') ?? '';
    if (!this.clienteId) {
      return;
    }

    this.clienteApi.obter(this.clienteId).subscribe((cliente) => {
      this.cliente.set(cliente);
      this.pageHeader.set([{ label: 'Clientes', link: ['/clientes'] }, { label: cliente.nome }]);
    });

    this.carregar();
  }

  carregar(): void {
    this.carregando.set(true);
    this.processoApi.listarPorCliente(this.clienteId).subscribe((processos) => {
      this.processos.set(processos);
      this.carregando.set(false);
    });
  }

  abrirFormulario(): void {
    const dialogRef = this.dialog.open(ProcessoFormDialogComponent, {
      autoFocus: 'first-tabbable',
      width: DIALOG_WIDTH,
      data: { clienteId: this.clienteId },
    });
    dialogRef.afterClosed().subscribe((processoCriado) => {
      if (processoCriado) {
        this.processos.update((atual) => [processoCriado, ...atual]);
      }
    });
  }
}
