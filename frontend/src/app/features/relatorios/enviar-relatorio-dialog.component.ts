import { CommonModule } from '@angular/common';
import { Component, Inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

import { ClienteApiService } from '../../core/api/services/cliente.service';
import { RelatorioApiService } from '../../core/api/services/relatorio.service';

export interface EnviarRelatorioDialogData {
  clienteId: string;
  clienteNome: string;
}

@Component({
  selector: 'maia-enviar-relatorio-dialog',
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
  templateUrl: './enviar-relatorio-dialog.component.html',
  styleUrl: './enviar-relatorio-dialog.component.scss',
})
export class EnviarRelatorioDialogComponent implements OnInit {
  destinatarios = '';
  enviando = signal(false);
  erro = signal<string | null>(null);

  constructor(
    private readonly clienteApi: ClienteApiService,
    private readonly relatorioApi: RelatorioApiService,
    private readonly dialogRef: MatDialogRef<EnviarRelatorioDialogComponent, boolean>,
    @Inject(MAT_DIALOG_DATA) readonly data: EnviarRelatorioDialogData,
  ) {}

  ngOnInit(): void {
    this.clienteApi.obter(this.data.clienteId).subscribe((cliente) => {
      this.destinatarios = cliente.destinatarios_relatorio;
    });
  }

  get formInvalido(): boolean {
    return !this.destinatarios.trim();
  }

  cancelar(): void {
    this.dialogRef.close();
  }

  enviar(): void {
    if (this.formInvalido) {
      return;
    }
    this.enviando.set(true);
    this.erro.set(null);
    const destinatarios = this.destinatarios
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);

    this.relatorioApi.enviarEmail({ cliente_id: this.data.clienteId, destinatarios }).subscribe({
      next: () => this.dialogRef.close(true),
      error: (erro) => {
        this.erro.set(erro?.error?.detail ?? 'Não foi possível enviar o e-mail.');
        this.enviando.set(false);
      },
    });
  }
}
