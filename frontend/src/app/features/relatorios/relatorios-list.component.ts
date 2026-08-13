import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';

import { ClienteRead } from '../../core/api/models/cliente.model';
import { TIPOS_ENTREGAVEL, TipoEntregavel } from '../../core/api/models/entregavel.model';
import { EntregavelHistoricoRead } from '../../core/api/models/relatorio.model';
import { ClienteApiService } from '../../core/api/services/cliente.service';
import { RelatorioApiService } from '../../core/api/services/relatorio.service';
import { PageHeaderService } from '../../core/layout/page-header.service';
import { DIALOG_WIDTH } from '../../shared/dialog-config';
import { formatarStatus, statusChipClass } from '../../shared/status-label';
import { EnviarRelatorioDialogComponent } from './enviar-relatorio-dialog.component';

@Component({
  selector: 'maia-relatorios-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatSelectModule,
  ],
  templateUrl: './relatorios-list.component.html',
  styleUrl: './relatorios-list.component.scss',
})
export class RelatoriosListComponent implements OnInit {
  readonly formatarStatus = formatarStatus;
  readonly statusChipClass = statusChipClass;
  readonly tipos = TIPOS_ENTREGAVEL;

  clientes = signal<ClienteRead[]>([]);
  historico = signal<EntregavelHistoricoRead[]>([]);
  carregando = signal(true);

  clienteIdFiltro: string | null = null;
  tipoFiltro: TipoEntregavel | null = null;

  constructor(
    private readonly clienteApi: ClienteApiService,
    private readonly relatorioApi: RelatorioApiService,
    private readonly dialog: MatDialog,
    private readonly pageHeader: PageHeaderService,
  ) {}

  ngOnInit(): void {
    this.pageHeader.set([{ label: 'Relatórios' }]);
    this.clienteApi.listar().subscribe((clientes) => this.clientes.set(clientes));
    this.carregar();
  }

  carregar(): void {
    this.carregando.set(true);
    this.relatorioApi
      .listarHistorico({ clienteId: this.clienteIdFiltro ?? undefined, tipo: this.tipoFiltro ?? undefined })
      .subscribe((historico) => {
        this.historico.set(historico);
        this.carregando.set(false);
      });
  }

  rotuloTipo(tipo: TipoEntregavel): string {
    return this.tipos.find((item) => item.tipo === tipo)?.rotulo ?? tipo;
  }

  clienteSelecionado(): ClienteRead | undefined {
    return this.clientes().find((cliente) => cliente.id === this.clienteIdFiltro);
  }

  abrirEnvioEmail(): void {
    const cliente = this.clienteSelecionado();
    if (!cliente) {
      return;
    }
    this.dialog.open(EnviarRelatorioDialogComponent, {
      width: DIALOG_WIDTH,
      data: { clienteId: cliente.id, clienteNome: cliente.nome },
    });
  }
}
