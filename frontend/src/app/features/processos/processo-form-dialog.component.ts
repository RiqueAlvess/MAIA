import { CommonModule } from '@angular/common';
import { Component, Inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

import { ProcessoRead } from '../../core/api/models/processo.model';
import { ProcessoApiService } from '../../core/api/services/processo.service';

export interface ProcessoFormDialogData {
  clienteId: string;
}

@Component({
  selector: 'maia-processo-form-dialog',
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
  templateUrl: './processo-form-dialog.component.html',
  styleUrl: './processo-form-dialog.component.scss',
})
export class ProcessoFormDialogComponent {
  nome = '';
  salvando = signal(false);
  erro = signal<string | null>(null);

  constructor(
    private readonly processoApi: ProcessoApiService,
    private readonly dialogRef: MatDialogRef<ProcessoFormDialogComponent, ProcessoRead>,
    @Inject(MAT_DIALOG_DATA) private readonly data: ProcessoFormDialogData,
  ) {}

  get formInvalido(): boolean {
    return !this.nome.trim();
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
    this.processoApi.criar({ cliente_id: this.data.clienteId, nome: this.nome.trim() }).subscribe({
      next: (processo) => this.dialogRef.close(processo),
      error: () => {
        this.erro.set('Não foi possível criar o processo. Tente novamente.');
        this.salvando.set(false);
      },
    });
  }
}
