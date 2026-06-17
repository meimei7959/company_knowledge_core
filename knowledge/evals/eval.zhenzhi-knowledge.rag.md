---
type: EvalCase
title: zhenzhi-knowledge RAG eval
description: Evaluation case for local retrieval context generation.
timestamp: "2026-06-17T02:30:00Z"
evalId: eval.zhenzhi-knowledge.rag
owner: meimei
status: verified
targetRef: tools/tool.zhenzhi-knowledge.md
expected: sourceRef
---

## Input

Run `zhenzhi-knowledge rag search` or `zhenzhi-knowledge start` on a task with matching verified knowledge.

## Expected

The retrieval output includes sourceRef and does not return secret or customer_confidential content.
