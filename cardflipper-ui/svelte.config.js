import adapter from '@sveltejs/adapter-node';
import preprocess from 'svelte-preprocess';

const config = {
  preprocess: preprocess(),
  kit: {
    adapter: adapter({
      out: 'build' // <- must match what Firebase is trying to use
    })
  }
};

export default config;