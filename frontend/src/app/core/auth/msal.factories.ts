import { MsalInterceptorConfiguration } from '@azure/msal-angular';
import {
  BrowserCacheLocation,
  InteractionType,
  IPublicClientApplication,
  LogLevel,
  PublicClientApplication,
} from '@azure/msal-browser';

import { environment } from '../../../environments/environment';
import { authConfigured } from './auth-mode';

export function msalInstanceFactory(): IPublicClientApplication {
  return new PublicClientApplication({
    auth: {
      clientId: environment.auth.clientId,
      authority: `https://login.microsoftonline.com/${environment.auth.tenantId}`,
      redirectUri: environment.auth.redirectUri,
      postLogoutRedirectUri: '/login',
    },
    cache: {
      cacheLocation: BrowserCacheLocation.LocalStorage,
      storeAuthStateInCookie: false,
    },
    system: {
      loggerOptions: {
        loggerCallback: () => {},
        logLevel: LogLevel.Warning,
        piiLoggingEnabled: false,
      },
    },
  });
}

export function msalInterceptorConfigFactory(): MsalInterceptorConfiguration {
  const protectedResourceMap = new Map<string, Array<string>>();

  // Mapa vazio quando não configurado: o interceptor nunca tenta adquirir
  // token nem redirecionar para login em nenhuma chamada à API.
  if (authConfigured) {
    protectedResourceMap.set(environment.apiUrl, environment.auth.scopes);
  }

  return {
    interactionType: InteractionType.Redirect,
    protectedResourceMap,
  };
}
