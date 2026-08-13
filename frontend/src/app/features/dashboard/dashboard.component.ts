import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { authConfigured } from '../../core/auth/auth-mode';
import { ClienteRead } from '../../core/api/models/cliente.model';
import { TIPOS_ENTREGAVEL } from '../../core/api/models/entregavel.model';
import { ClienteApiService } from '../../core/api/services/cliente.service';
import { PageHeaderService } from '../../core/layout/page-header.service';

@Component({
  selector: 'maia-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatIconModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  readonly authConfigured = authConfigured;
  readonly tiposEntregavelCount = TIPOS_ENTREGAVEL.length;

  clientes = signal<ClienteRead[]>([]);
  carregando = signal(true);

  constructor(
    private readonly clienteApi: ClienteApiService,
    private readonly pageHeader: PageHeaderService,
  ) {}

  ngOnInit(): void {
    this.pageHeader.set([{ label: 'Dashboard' }]);
    this.clienteApi.listar().subscribe((clientes) => {
      this.clientes.set(clientes);
      this.carregando.set(false);
    });
  }

  clientesRecentes(): ClienteRead[] {
    return [...this.clientes()]
      .sort((a, b) => new Date(b.criado_em).getTime() - new Date(a.criado_em).getTime())
      .slice(0, 6);
  }

  iniciais(nome: string): string {
    return nome.charAt(0).toUpperCase();
  }
}
