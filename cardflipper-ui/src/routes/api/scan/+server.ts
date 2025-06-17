import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  const res = await fetch('http://localhost:5000/scan');
  const data = await res.json();

  return new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' }
  });
};
