const { getEncoding } = require("js-tiktoken");
const enc = getEncoding("cl100k_base");
const t = JSON.parse(require("fs").readFileSync(process.argv[2], "utf8"));
let n = 0; for (const s of t) n += enc.encode(s).length;
console.log(JSON.stringify({texts: t.length, tokens: n, usd: n / 1e6 * 0.02}));
