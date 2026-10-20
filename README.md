1. Identify flaky outcomes from same-revision reruns without quarantining permanent failures.

2. Result:
   Injected flakes detected: 20  
   Precision: 1.0  
   Recall: 1.0  

   Measured by `make bench`; raw [results](evidence/bench.json), [checks](evidence/checks.log), and [environment](evidence/environment.json).

3. Architecture:
```mermaid
flowchart LR
    CIHistory --> SameRevisionReruns --> EvidencePolicy --> QuarantineProposal --> PRComment
```

4. Run it (from this folder):
```sh
make setup
make lint test bench
make demo
```

5. Decisions and limits: Evaluation uses seeded synthetic history, including permanently failing controls. The policy proposes quarantine after repeated mixed outcomes; the report specifies seven-day expiry and nightly execution, but does not modify an external test runner. Cost is modeled from synthetic durations. The flake-report GitHub Action posts the report to same-repository PRs; fork PRs are skipped because their tokens cannot write comments. See evidence/comment.md and the workflow.

6. Next: Import real JUnit rerun history and enforce quarantine expiry in a test scheduler.

PR reporting demonstration uses synthetic history only.
