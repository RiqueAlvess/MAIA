import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { MsalBroadcastService, MsalService } from '@azure/msal-angular';
import { InteractionStatus } from '@azure/msal-browser';
import { filter, map, take } from 'rxjs';

import { authConfigured } from './auth-mode';

/**
 * Substitui o MsalGuard padrão: em vez de redirecionar direto para a tela de
 * login da Microsoft, manda o usuário não autenticado para /login — nossa
 * própria tela. O redirecionamento para a Microsoft só acontece quando o
 * usuário clica no botão lá, nunca automaticamente.
 */
export const authGuard: CanActivateFn = (_route, state) => {
  if (!authConfigured) {
    return true;
  }

  const msalService = inject(MsalService);
  const msalBroadcastService = inject(MsalBroadcastService);
  const router = inject(Router);

  return msalBroadcastService.inProgress$.pipe(
    filter((status) => status === InteractionStatus.None),
    take(1),
    map(() => {
      if (msalService.instance.getActiveAccount()) {
        return true;
      }
      return router.createUrlTree(['/login'], { queryParams: { redirectTo: state.url } });
    }),
  );
};
