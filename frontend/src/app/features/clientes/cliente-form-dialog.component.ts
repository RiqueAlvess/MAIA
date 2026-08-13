import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

import { ClienteRead } from '../../core/api/models/cliente.model';
import { ClienteApiService } from '../../core/api/services/cliente.service';

@Component({
  selector: 'maia-cliente-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
  ],
  templateUrl: './cliente-form-dialog.component.html',
  styleUrl: './cliente-form-dialog.component.scss',
})
export class ClienteFormDialogComponent {
  nome = '';
  pastaSharepointId = '';
  salvando = signal(false);
  erro = signal<string | null>(null);

  constructor(
    private readonly clienteApi: ClienteApiService,
    private readonly dialogRef: MatDialogRef<ClienteFormDialogComponent, ClienteRead>,
  ) {}

  get formInvalido(): boolean {
    return !this.nome.trim() || !this.pastaSharepointId.trim();
  }

  cancelar(): void {
    this.dialogRef.close();
  }

  salvar(): void {
    if (this.formInvalido) {
      return;
    }
    this.salvando.set(true);
    this.erro.set(null);
    this.clienteApi.criar({ nome: this.nome.trim(), pasta_sharepoint_id: this.pastaSharepointId.trim() }).subscribe({
      next: (cliente) => this.dialogRef.close(cliente),
      error: () => {
        this.erro.set('Não foi possível criar o cliente. Tente novamente.');
        this.salvando.set(false);
      },
    });
  }
}
