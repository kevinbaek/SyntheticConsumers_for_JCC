| Model | Calls | Input tokens (M) | Output tokens (M) | Thinking tokens (M) | Input cost (USD) | Output cost (USD) | Total (USD) | Token measurement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | 8,790 | 11.70 | 3.66 | 0.00 | 58.5 | 109.9 | 168.5 | o200k_base tokenizer (js-tiktoken) on every call, +3 tokens per message and +3 for the reply |
| Gemini 3.1 Pro | 8,790 | 11.57 | 3.74 | 7.16 | 23.1 | 130.7 | 153.8 | API usage metadata of all 8,790 calls |
| Claude Sonnet 5 | 8,790 | 15.27 | 4.25 | 0.00 | 30.5 | 42.5 | 73.0 | Anthropic token-counting endpoint on a random sample per call type |
| All three | 26,370 | – | – | – | – | – | 395.3 | |
