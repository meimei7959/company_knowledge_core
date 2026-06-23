# 研发工程质量门 Quality Example

## Acceptable Result Shape

The Development Agent states the implementation scope, runs targeted tests, runs `development_quality_gate`, records verdict and findings, and hands off to Test or Architecture with evidence.

## Rejection Example

Reject or reroute when implementation touches high-risk files without architecture review, changes code without tests or blocker reason, grows god files, hides quality gate failures, or claims final QA/product acceptance.
