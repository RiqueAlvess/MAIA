import { environment } from '../../../environments/environment';

/**
 * Autenticação via Entra ID só é exigida quando clientId e tenantId reais
 * foram configurados em environment.ts/environment.prod.ts. Sem eles, a
 * aplicação roda em modo desenvolvimento (sem login, sem token nas
 * chamadas à API) — o backend aplica a mesma regra em app/core/security.py.
 */
export const authConfigured = !!(environment.auth.clientId && environment.auth.tenantId);
