export const environment = {
  production: true,
  apiUrl: '/api/v1',
  auth: {
    clientId: '',
    tenantId: '',
    redirectUri: window.location.origin,
    scopes: ['api://maia-api/access_as_user'],
  },
};
