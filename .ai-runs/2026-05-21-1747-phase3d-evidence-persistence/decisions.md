# Decisions

- Keep evidence persistence under the existing query log repository boundary because retrieval results, answers, and citations are operational details of query logs.
- Store snapshot fields such as document title, source URI, quote text, score, and access reason so Operations can still report historical evidence even if documents change later.
- Aggregate top evidence from both retrieval result rows and citation rows.
- Keep answer text/refusal metadata separate from citation rows so unsupported answers can still be audited.
- Add only top evidence API/UI in this slice; detailed query drilldown can follow later.
