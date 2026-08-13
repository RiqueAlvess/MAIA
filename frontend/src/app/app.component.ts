import { BreakpointObserver } from '@angular/cdk/layout';
import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSidenavModule } from '@angular/material/sidenav';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MsalBroadcastService, MsalService } from '@azure/msal-angular';
import type { AccountInfo } from '@azure/msal-browser';
import { InteractionStatus } from '@azure/msal-browser';
import { filter } from 'rxjs';

import { authConfigured } from './core/auth/auth-mode';
import { Breadcrumb, PageHeaderService } from './core/layout/page-header.service';

@Component({
  selector: 'maia-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatDividerModule,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent implements OnInit {
  private readonly pageHeader = inject(PageHeaderService);

  readonly authConfigured = authConfigured;
  readonly isMobile = signal(false);
  readonly sidenavOpened = signal(true);
  readonly sidenavMode = computed(() => (this.isMobile() ? 'over' : 'side'));
  readonly breadcrumbs = this.pageHeader.breadcrumbs;

  contaAtiva: AccountInfo | null = null;

  readonly navLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: 'space_dashboard' },
    { path: '/clientes', label: 'Clientes', icon: 'groups' },
  ];

  constructor(
    private readonly breakpointObserver: BreakpointObserver,
    private readonly msalService: MsalService,
    private readonly msalBroadcastService: MsalBroadcastService,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    this.breakpointObserver.observe('(max-width: 959px)').subscribe((result) => {
      this.isMobile.set(result.matches);
      this.sidenavOpened.set(!result.matches);
    });

    this.router.events.pipe(filter((event) => event instanceof NavigationEnd)).subscribe(() => {
      if (this.isMobile()) {
        this.sidenavOpened.set(false);
      }
    });

    if (this.authConfigured) {
      this.msalBroadcastService.inProgress$
        .pipe(filter((status) => status === InteractionStatus.None))
        .subscribe(() => {
          this.contaAtiva = this.msalService.instance.getActiveAccount();
        });
    }
  }

  toggleSidenav(): void {
    this.sidenavOpened.update((opened) => !opened);
  }

  sair(): void {
    this.msalService.logoutRedirect();
  }

  trackByBreadcrumb(_index: number, item: Breadcrumb): string {
    return item.label;
  }
}
