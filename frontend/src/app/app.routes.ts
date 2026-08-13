import { Routes } from '@angular/router';
import { MsalGuard } from '@azure/msal-angular';

export const appRoutes: Routes = [
  {
    path: '',
    canActivate: [MsalGuard],
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
        path: 'processos/:processoId/entregaveis',
        loadComponent: () =>
          import('./features/entregaveis/entregaveis-panel.component').then((m) => m.EntregaveisPanelComponent),
      },
    ],
  },
];
