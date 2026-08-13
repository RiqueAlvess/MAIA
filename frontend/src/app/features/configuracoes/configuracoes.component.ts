import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';

import { ClienteRead } from '../../core/api/models/cliente.model';
import { StatusIntegracoesRead } from '../../core/api/models/relatorio.model';
import { ClienteApiService } from '../../core/api/services/cliente.service';
import { ConfiguracoesApiService } from '../../core/api/services/configuracoes.service';
import { PageHeaderService } from '../../core/layout/page-header.service';

interface LinhaCliente {
  cliente: ClienteRead;
  destinatarios: string;
  salvando: boolean;
}

@Component({
  selector: 'maia-configuracoes',
  standalone: true,
  imports: [CommonModule, FormsModule, MatButtonModule, MatFormFieldModule, MatIconModule, MatInputModule],
  templateUrl: './configuracoes.component.html',
  styleUrl: './configuracoes.component.scss',
})
export class ConfiguracoesComponent implements OnInit {
  status = signal<StatusIntegracoesRead | null>(null);
  linhas = signal<LinhaCliente[]>([]);
  carregando = signal(true);

  constructor(
    private readonly configuracoesApi: ConfiguracoesApiService,
    private readonly clienteApi: ClienteApiService,
    private readonly pageHeader: PageHeaderService,
    private readonly snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.pageHeader.set([{ label: 'Configurações' }]);

    this.configuracoesApi.obterStatus().subscribe((status) => this.status.set(status));

    this.carregando.set(true);
    this.clienteApi.listar().subscribe((clientes) => {
      this.linhas.set(clientes.map((cliente) => ({ cliente, destinatarios: cliente.destinatarios_relatorio, salvando: false })));
      this.carregando.set(false);
    });
  }

  salvar(linha: LinhaCliente): void {
    linha.salvando = true;
    this.clienteApi.atualizarDestinatarios(linha.cliente.id, linha.destinatarios.trim()).subscribe({
      next: (clienteAtualizado) => {
        linha.cliente = clienteAtualizado;
        linha.destinatarios = clienteAtualizado.destinatarios_relatorio;
        linha.salvando = false;
        this.snackBar.open(`Destinatários de ${clienteAtualizado.nome} atualizados.`, 'Fechar', { duration: 3000 });
      },
      error: () => {
        linha.salvando = false;
        this.snackBar.open('Não foi possível salvar. Tente novamente.', 'Fechar', { duration: 4000 });
      },
    });
  }
}
