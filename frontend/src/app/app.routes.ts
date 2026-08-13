import { Routes } from '@angular/router';
import { MsalGuard } from '@azure/msal-angular';

import { authConfigured } from './core/auth/auth-mode';

export const appRoutes: Routes = [
  {
    path: '',
    canActivate: authConfigured ? [MsalGuard] : [],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
      },
      {
        path: 'clientes',
        loadComponent: () =>
          import('./features/clientes/clientes-list.component').then((m) => m.ClientesListComponent),
      },
      {
        path: 'clientes/:clienteId/processos',
        loadComponent: () =>
          import('./features/processos/processos-list.component').then((m) => m.ProcessosListComponent),
      },
      {
        path: 'processos',
        loadComponent: () =>
          import('./features/processos/processos-global-list.component').then(
            (m) => m.ProcessosGlobalListComponent,
          ),
      },
      {
        path: 'processos/:processoId/entregaveis',
        loadComponent: () =>
          import('./features/entregaveis/entregaveis-panel.component').then((m) => m.EntregaveisPanelComponent),
      },
      {
        path: 'relatorios',
        loadComponent: () =>
          import('./features/relatorios/relatorios-list.component').then((m) => m.RelatoriosListComponent),
      },
      {
        path: 'configuracoes',
        loadComponent: () =>
          import('./features/configuracoes/configuracoes.component').then((m) => m.ConfiguracoesComponent),
      },
    ],
  },
];
