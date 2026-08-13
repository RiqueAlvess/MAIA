import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

import { ClienteRead } from '../../core/api/models/cliente.model';
import { ClienteApiService } from '../../core/api/services/cliente.service';
import { PageHeaderService } from '../../core/layout/page-header.service';
import { DIALOG_WIDTH } from '../../shared/dialog-config';
import { ClienteFormDialogComponent } from './cliente-form-dialog.component';

@Component({
  selector: 'maia-clientes-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
  ],
  templateUrl: './clientes-list.component.html',
  styleUrl: './clientes-list.component.scss',
})
export class ClientesListComponent implements OnInit {
  clientes = signal<ClienteRead[]>([]);
  carregando = signal(true);
  busca = signal('');

  constructor(
    private readonly clienteApi: ClienteApiService,
    private readonly dialog: MatDialog,
    private readonly pageHeader: PageHeaderService,
  ) {}

  ngOnInit(): void {
    this.pageHeader.set([{ label: 'Clientes' }]);
    this.carregar();
  }

  carregar(): void {
    this.carregando.set(true);
    this.clienteApi.listar().subscribe((clientes) => {
      this.clientes.set(clientes);
      this.carregando.set(false);
    });
  }

  clientesFiltrados(): ClienteRead[] {
    const termo = this.busca().trim().toLowerCase();
    if (!termo) {
      return this.clientes();
    }
    return this.clientes().filter((cliente) => cliente.nome.toLowerCase().includes(termo));
  }

  iniciais(nome: string): string {
    return nome.charAt(0).toUpperCase();
  }

  abrirFormulario(): void {
    const dialogRef = this.dialog.open(ClienteFormDialogComponent, {
      autoFocus: 'first-tabbable',
      width: DIALOG_WIDTH,
    });
    dialogRef.afterClosed().subscribe((clienteCriado) => {
      if (clienteCriado) {
        this.clientes.update((atual) => [clienteCriado, ...atual]);
      }
    });
  }
}
