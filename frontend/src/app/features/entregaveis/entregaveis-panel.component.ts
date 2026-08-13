import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { Subscription, interval, switchMap, takeWhile } from 'rxjs';

import { EntregavelApiService } from '../../core/api/services/entregavel.service';
import { JobGeracaoRead, StatusJob, TIPOS_ENTREGAVEL, TipoEntregavel } from '../../core/api/models/entregavel.model';

const INTERVALO_CONSULTA_MS = 3000;
const STATUS_EM_ANDAMENTO: StatusJob[] = ['pendente', 'processando'];

@Component({
  selector: 'maia-entregaveis-panel',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatCardModule, MatChipsModule, MatProgressBarModule],
  templateUrl: './entregaveis-panel.component.html',
})
export class EntregaveisPanelComponent implements OnInit, OnDestroy {
  tipos = TIPOS_ENTREGAVEL;
  processoId = '';
  jobsPorTipo = new Map<TipoEntregavel, JobGeracaoRead>();

  private assinaturas = new Map<TipoEntregavel, Subscription>();

  constructor(
    private readonly route: ActivatedRoute,
    private readonly entregavelApi: EntregavelApiService,
  ) {}

  ngOnInit(): void {
    this.processoId = this.route.snapshot.paramMap.get('processoId') ?? '';
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
