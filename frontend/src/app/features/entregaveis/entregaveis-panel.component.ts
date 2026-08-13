import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subscription, interval, switchMap, takeWhile } from 'rxjs';

import { ProcessoRead } from '../../core/api/models/processo.model';
import { EntregavelApiService } from '../../core/api/services/entregavel.service';
import { JobGeracaoRead, StatusJob, TIPOS_ENTREGAVEL, TipoEntregavel } from '../../core/api/models/entregavel.model';
import { ClienteApiService } from '../../core/api/services/cliente.service';
import { ProcessoApiService } from '../../core/api/services/processo.service';
import { PageHeaderService } from '../../core/layout/page-header.service';

const INTERVALO_CONSULTA_MS = 3000;
const STATUS_EM_ANDAMENTO: StatusJob[] = ['pendente', 'processando'];

const ROTULO_STATUS: Record<StatusJob, string> = {
  pendente: 'Na fila',
  processando: 'Gerando…',
  concluido: 'Gerado',
  erro: 'Falhou',
};

@Component({
  selector: 'maia-entregaveis-panel',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './entregaveis-panel.component.html',
  styleUrl: './entregaveis-panel.component.scss',
})
export class EntregaveisPanelComponent implements OnInit, OnDestroy {
  readonly tipos = TIPOS_ENTREGAVEL;
  readonly rotuloStatus = ROTULO_STATUS;

  processoId = '';
  clienteId = '';
  processo: ProcessoRead | null = null;
  jobsPorTipo = new Map<TipoEntregavel, JobGeracaoRead>();

  private assinaturas = new Map<TipoEntregavel, Subscription>();

  constructor(
    private readonly route: ActivatedRoute,
    private readonly entregavelApi: EntregavelApiService,
    private readonly processoApi: ProcessoApiService,
    private readonly clienteApi: ClienteApiService,
    private readonly pageHeader: PageHeaderService,
  ) {}

  ngOnInit(): void {
    this.processoId = this.route.snapshot.paramMap.get('processoId') ?? '';
    if (!this.processoId) {
      return;
    }

    this.processoApi.obter(this.processoId).subscribe((processo) => {
      this.processo = processo;
      this.clienteId = processo.cliente_id;
      this.clienteApi.obter(processo.cliente_id).subscribe((cliente) => {
        this.pageHeader.set([
          { label: 'Clientes', link: ['/clientes'] },
          { label: cliente.nome, link: ['/clientes', cliente.id, 'processos'] },
          { label: processo.nome },
        ]);
      });
    });
  }

  ngOnDestroy(): void {
    this.assinaturas.forEach((assinatura) => assinatura.unsubscribe());
  }

  gerar(tipo: TipoEntregavel): void {
    this.entregavelApi.gerar(tipo, this.processoId).subscribe((job) => {
      this.jobsPorTipo.set(tipo, job);
      this.acompanharJob(tipo, job.id);
    });
  }

  jobDoTipo(tipo: TipoEntregavel): JobGeracaoRead | undefined {
    return this.jobsPorTipo.get(tipo);
  }

  emAndamento(tipo: TipoEntregavel): boolean {
    const job = this.jobsPorTipo.get(tipo);
    return !!job && STATUS_EM_ANDAMENTO.includes(job.status);
  }

  private acompanharJob(tipo: TipoEntregavel, jobId: string): void {
    this.assinaturas.get(tipo)?.unsubscribe();

    const assinatura = interval(INTERVALO_CONSULTA_MS)
      .pipe(
        switchMap(() => this.entregavelApi.obterStatusJob(jobId)),
        takeWhile((job) => STATUS_EM_ANDAMENTO.includes(job.status), true),
      )
      .subscribe((job) => this.jobsPorTipo.set(tipo, job));

    this.assinaturas.set(tipo, assinatura);
  }
}
