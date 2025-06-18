import { onRequest } from 'firebase-functions/v2/https';

export const sveltekit = onRequest({}, async (req, res) => {
  const { default: handler } = await import('../.svelte-kit/output/server/index.js');
  return handler(req, res);
});
