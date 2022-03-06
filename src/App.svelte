<script>
	import { onMount } from 'svelte';
	import {Shortcuts} from 'shortcuts';
	import { writable } from 'svelte/store';
	import { diffChars, diffLines, diffWords } from 'diff';
	let inputFile = writable('http://localhost:80/de.csv');
	let text;
	let fragments = [];
	let en = '';
	let de = '';
	let index = 0;
	let user = writable('');
	let diffFrom = '';
	let diffTo = '';
	let showDiff = false;
	
	// onMount(async() => {
	// });

	function removePunctuation(s) {
    return s.replaceAll(/[,!?".„():;]/g, ' ');
	}

	function normalizeSpacing(s) {
    return s.replaceAll(/[ \t\n\r]+/g, ' ').trim();
	}

	let nextTry = () => {
		console.log('next try', index);
		if (fragments[index] !== undefined) {
			en = fragments[index].en;
			de = fragments[index].de;
			$user = '';
			showDiff = false;
		}
	};

	const shortcuts = new Shortcuts ();

	async function loadText(url) {
		const res = await fetch(url);
		if (res.ok) {
			return await res.text();
		} else {
			throw new Error(text);
		}
	}

	inputFile.subscribe(url => {
		loadText(url).then(txt => {
			text = txt;
			const lines = text.split('\n');
			fragments = lines.map(line => {
				let [left, right] = line.trim().split(';');
				return {
					'en': right,
					'de': normalizeSpacing(removePunctuation(left)),
				};
			});
			index = 0;
			nextTry();
		});
	});

	function test() {
		const d = diffWords(de, normalizeSpacing(removePunctuation($user)));
		console.log('diffChars', d);
		diffFrom = '';
		diffTo = '';
		let diffToLen = 0
		let diffFromLen = 0;
		for (const p of d) {
			if (p.added) {
				diffTo += `<em>${p.value}</em>`;
				diffToLen += p.value.length;
			} else if (p.removed) {
				diffFrom += `${p.value}`;
				diffFromLen += p.value.length;
			} else {
				for (let i = 0; i < diffToLen - diffFromLen; i+=1) diffFrom += ' ';
				if (diffFromLen - diffToLen > 0) {
					diffTo += '<em>';
					for (let i = 0; i < diffFromLen - diffToLen; i+=1) diffTo += '_';
					diffTo += '</em>';
				}
				diffTo += p.value;
				diffFrom += p.value;
				diffToLen = diffFromLen = 0;
			}
		}
		if (diffTo != diffFrom) {
			showDiff = true;
			console.log('from', diffFrom);
			console.log('to', diffTo);
		} else {
			index += 1;
			nextTry();
		}
	}
</script>

<main>
	<div><input bind:value={$inputFile}></div>
	<p class="challenge">{en}</p>
	<div><input bind:value={$user} on:keydown={(e) => {
		if (e.key == 'Enter')	{
			if (e.ctrlKey) {
				index += 1; nextTry();
				return;
			}
			if (showDiff) {
				nextTry();
			} else {
				test();
			};
		}
	}}></div>
	{#if showDiff}
	<pre class='diff'>{@html diffFrom}</pre>
	<pre class='diff'>{@html diffTo}</pre>
	{/if}
	<button on:click={() => {nextTry();}}>again</button>
	<button on:click={() => {index += 1; nextTry();}}>next</button>
</main>

<style>
	:global(body) {
		background-color: #15141a;
		font-size: 18px;
		font-family: 'Courier New', Courier, monospace;
		color: #eee;
	}
	:global(input) {
		background-color: #15141a;
		color: #eee;
	}
	:global(button) {
		background-color: #15141a;
		color: #eee;
	}
	main {
		text-align: left;
		padding: 1em;
		width: auto;
		margin: 0 auto;
	}

	h1 {
		color: blue;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}

	input {
		width: 100%;
	}

	/* .challenge {
		height: 2em;
	} */

	.diff :global(em) {
		color: rgb(255, 62, 0);
		font-style: normal;
	}
</style>