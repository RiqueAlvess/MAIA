import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MsalBroadcastService, MsalService } from '@azure/msal-angular';
import { InteractionStatus } from '@azure/msal-browser';
import { filter, take } from 'rxjs';

import { environment } from '../../../environments/environment';
import { authConfigured } from '../../core/auth/auth-mode';

@Component({
  selector: 'maia-login',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatIconModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent implements OnInit {
  private readonly msalService = inject(MsalService);
  private readonly msalBroadcastService = inject(MsalBroadcastService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  readonly authConfigured = authConfigured;
  readonly verificando = signal(authConfigured);
  readonly entrando = signal(false);
  readonly erro = signal<string | null>(null);

  ngOnInit(): void {
    if (!this.authConfigured) {
      return;
    }

    this.msalBroadcastService.inProgress$
      .pipe(
        filter((status) => status === InteractionStatus.None),
        take(1),
      )
      .subscribe(() => {
        this.verificando.set(false);
        if (this.msalService.instance.getActiveAccount()) {
          this.irParaDestino();
        }
      });
  }

  entrarComMicrosoft(): void {
    this.entrando.set(true);
    this.erro.set(null);
    this.msalService.loginRedirect({ scopes: ['User.Read', ...environment.auth.scopes] }).subscribe({
      error: () => {
        this.entrando.set(false);
        this.erro.set('Não foi possível iniciar o login com a Microsoft. Tente novamente.');
      },
    });
  }

  continuarSemLogin(): void {
    this.irParaDestino();
  }

  private irParaDestino(): void {
    const destino = this.route.snapshot.queryParamMap.get('redirectTo') || '/dashboard';
    this.router.navigateByUrl(destino);
  }
}
