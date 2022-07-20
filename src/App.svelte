<script>
	import { writable } from "svelte/store";
	import { diffWords } from "diff";
	let inputFile = writable(localStorage.getItem("inputFile"));
	let text;
	let fragments = [];
	let en = "";
	let de = "";
	let index = 0;
	let user = writable("");
	let diffFrom = "";
	let diffTo = "";
	let showDiff = false;
	let totalErrorCount = 0;
	let currentErrorCount = 0;
	let userDisabled = false;
	let userInput;
	let inputFileE;
	let letterMode = writable(
		localStorage.getItem("letterMode") == "true" || false
	);

	function removePunctuation(s) {
		return s.replaceAll(/[-,!?".„():;@#$%_^&*<>]/g, " ");
	}

	function normalizeSpacing(s) {
		return s.replaceAll(/[ \t\n\r]+/g, " ").trim();
	}

	let nextTry = () => {
		totalErrorCount += currentErrorCount;
		currentErrorCount = 0;
		if (fragments[index] !== undefined) {
			en = fragments[index].en;
			de = fragments[index].de;
			$user = "";
			showDiff = false;
		} else {
			en = "<EOF>";
			de = "";
		}
	};

	async function loadText(url) {
		const res = await fetch(url);
		if (res.ok) {
			return await res.text();
		} else {
			throw new Error(text);
		}
	}

	letterMode.subscribe((value) => {
		localStorage.setItem("letterMode", value.toString());
		console.log("letterMode", value.toString());
	});

	inputFile.subscribe((url) => {
		localStorage.setItem("inputFile", url);
		loadText(url).then((txt) => {
			text = txt;
			const lines = text.split("\n");
			fragments = lines.map((line) => {
				let [left, right] = line.trim().split(";");
				return {
					en: right,
					de: normalizeSpacing(removePunctuation(left)),
				};
			});
			index = 0;
			nextTry();
		});
	});

	function test() {
		const d = diffWords(de, normalizeSpacing(removePunctuation($user)));
		$user = "";
		diffFrom = "";
		diffTo = "";
		let diffToLen = 0;
		let diffFromLen = 0;
		for (const p of d) {
			const v = p.value;
			if (p.added) {
				currentErrorCount += 1;
				diffTo += `<em>${v}</em>`;
				diffToLen += v.length;
			} else if (p.removed) {
				currentErrorCount += 1;
				diffFrom += `${v}`;
				diffFromLen += v.length;
			} else {
				for (let i = 0; i < diffToLen - diffFromLen; i += 1) diffFrom += " ";
				if (diffFromLen - diffToLen > 0) {
					diffTo += "<em>";
					for (let i = 0; i < diffFromLen - diffToLen; i += 1) diffTo += "_";
					diffTo += "</em>";
				}
				diffTo += v;
				diffFrom += v;
				diffToLen = diffFromLen = 0;
			}
		}
		if (diffTo != diffFrom) {
			showDiff = true;
			console.log("from", diffFrom);
			console.log("to", diffTo);
		} else {
			index += 1;
			nextTry();
		}
	}

	function inputKeydown(e) {
		if (showDiff) {
			nextTry();
			return;
		}
		if (e.key == "Enter") {
			if (e.ctrlKey) {
				index += 1;
				nextTry();
				return;
			}
			if ($letterMode) {
				if (currentErrorCount == 0 && $user.length > 0) index += 1;
				nextTry();
			} else {
				test();
			}
		}
	}
	function inputKeyup(e) {
		if (!$letterMode) return;
		if ($user.length <= de.length) {
			let sub = de.substring(0, $user.length);
			if (sub != $user) {
				$user = sub;
				currentErrorCount += 1;
				// Disable user input for 1 second.
				userDisabled = true;
				userInput.disabled = true;
				setTimeout(() => {
					userDisabled = false;
					userInput.disabled = false;
					userInput.focus();
				}, 1000);
			}
		} else {
			$user = de;
		}
		if ($user == de && currentErrorCount == 0) {
			index += 1;
			nextTry();
		}
	}
</script>

<main>
	<div><input bind:value={$inputFile} /></div>
	<p class="challenge">{en} {index}</p>
	<div>
		<input
			bind:this={userInput}
			class:disabled={userDisabled}
			class:complete={$user == de}
			bind:value={$user}
			on:keydown={inputKeydown}
			on:keyup={inputKeyup}
		/>
	</div>
	{#if showDiff}
		<pre class="diff">{@html diffFrom}</pre>
		<pre class="diff">{@html diffTo}</pre>
	{/if}
	<button
		on:click={() => {
			nextTry();
		}}
		>again
	</button>
	<button
		on:click={() => {
			index += 1;
			nextTry();
		}}>next</button
	>
	<button
		on:click={() => {
			$letterMode = !$letterMode;
		}}
		>mode: {$letterMode ? "letter" : "sentence"}
	</button>
	<button
		on:click={() => {
			currentErrorCount = 0;
			totalErrorCount = 0;
		}}
		>errors: {currentErrorCount} / {totalErrorCount}
	</button>
</main>

<style>
	:global(body) {
		background-color: #15141a;
		font-size: 18px;
		font-family: "Courier New", Courier, monospace;
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

	.disabled {
		color: rgb(238, 90, 90);
	}
	.complete {
		color: rgb(72, 170, 72);
	}
</style>
