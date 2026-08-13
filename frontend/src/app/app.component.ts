import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MsalBroadcastService, MsalService } from '@azure/msal-angular';
import { InteractionStatus } from '@azure/msal-browser';
import { filter } from 'rxjs';

@Component({
  selector: 'maia-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, MatToolbarModule, MatButtonModule, MatIconModule],
  template: `
    <mat-toolbar color="primary">
      <span>MAIA — Mapeamento Assistido por IA</span>
      <span class="maia-toolbar-spacer"></span>
      @if (contaAtiva) {
        <span>{{ contaAtiva.name || contaAtiva.username }}</span>
        <button mat-button (click)="sair()">Sair</button>
      }
    </mat-toolbar>
    <router-outlet></router-outlet>
  `,
})
export class AppComponent implements OnInit {
  contaAtiva: import('@azure/msal-browser').AccountInfo | null = null;

  constructor(
    private readonly msalService: MsalService,
    private readonly msalBroadcastService: MsalBroadcastService,
  ) {}

  ngOnInit(): void {
    this.msalBroadcastService.inProgress$
      .pipe(filter((status) => status === InteractionStatus.None))
      .subscribe(() => {
        this.contaAtiva = this.msalService.instance.getActiveAccount();
      });
  }

  sair(): void {
    this.msalService.logoutRedirect();
  }
}
