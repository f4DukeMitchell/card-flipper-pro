
<select style="background: black; color: #33ff33; border: 1px solid #33ff33; font-family: monospace;">
  <option>Moderate</option>
  <option>Aggressive</option>
  <option>Tame</option>
</select>


<script lang="ts">
  interface CardItem {
    Title: string;
    Price: number;
    "Profit ($)": number;
    Confidence: number;
    "Time Left (min)": number;
    Seller: string;
    Condition: string;
    "Bid Status": string;
    "eBay Link": string;
    "Current Bid": number;
    "Max Bid": number;
    "Projected P/L": number;
  }

  let items: CardItem[] = [];
  let loading = true;

  const fetchData = async () => {
    try {
      const res = await fetch('/api/scan');
      if (!res.ok) throw new Error(`API Error: ${res.status}`);
      const data = await res.json();
      items = data.items || data;
    } catch (err) {
      console.error("❌ Failed to fetch scan data:", err);
    } finally {
      loading = false;
    }
  };

  import { onMount } from 'svelte';
  onMount(() => {
    fetchData();
  });
</script>

<style>
  :global(body) {
    margin: 0;
    background-color: black;
    color: #33ff33;
    font-family: 'Share Tech Mono', monospace;
  }

  h1 {
    margin: 1rem;
    font-size: 1.8rem;
    display: flex;
    align-items: center;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background-color: black;
  }

  th, td {
    border: 1px solid #33ff33;
    padding: 6px;
    text-align: left;
    font-size: 0.95rem;
  }

  a {
    color: #33ccff;
    text-decoration: none;
  }

  p {
    font-family: 'Share Tech Mono', monospace;
  }
:global(body::before) {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    background: repeating-linear-gradient(
        to bottom,
        rgba(0, 0, 0, 0.1) 0px,
        rgba(0, 0, 0, 0.1) 1px,
        transparent 2px,
        transparent 4px
    );
    z-index: 9999;
    animation: flicker 0.2s infinite;
    }

    @keyframes flicker {
    0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
        opacity: 0.15;
    }
    20%, 22%, 24%, 55% {
        opacity: 0.05;
    }
}

</style>

<h1>🟢 CardFlipper Pro</h1>

{#if loading}
  <p>Loading...</p>
{:else if items.length === 0}
  <p>⚠️ No items returned.</p>
{:else}
  <table border="1">
    <thead>
      <tr>
        <th>Title</th>
        <th>Price</th>
        <th>Profit</th>
        <th>Confidence</th>
        <th>Time Left</th>
        <th>Seller</th>
        <th>Condition</th>
        <th>Bid Status</th>
        <th>Link</th>
        <th>Current Bid</th>
        <th>Max Bid</th>
        <th>Projected P/L</th>
      </tr>
    </thead>
    <tbody>
      {#each items as item}
        <tr>
          <td>{item.Title}</td>
          <td>${item.Price}</td>
          <td style="color: {item["Profit ($)"] >= 0 ? '#33ff33' : '#ff3333'};">${item["Profit ($)"]}</td>
          <td>{item.Confidence}</td>
          <td>{item["Time Left (min)"]}m</td>
          <td>{item.Seller}</td>
          <td>{item.Condition}</td>
          <td>{item["Bid Status"]}</td>
          <td><a href={item["eBay Link"]} target="_blank">🔗</a></td>
          <td>${item["Current Bid"]}</td>
          <td>${item["Max Bid"]}</td>
          <td style="color: {item["Profit ($)"] >= 0 ? '#33ff33' : '#ff3333'};">${item["Profit ($)"]}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}
