# GitHub Raw Research: Agentic Coding Regressions

## Header

- Timestamp: 2026-05-05T20:42:59+09:30 Australia/Adelaide
- Method: authenticated read-only GitHub Search API collection, covering issues, pull requests, repositories, and code/file search where available.
- Limitations: raw GitHub search evidence, not a balanced synthesis; GitHub search ranking and rate limits can omit relevant material; outbound links inside GitHub pages were not counted as sources; no repository, issue, PR, star, fork, or settings mutation was performed.
- Source count: 130 distinct GitHub URLs.
- Source type counts: issue: 9, pull_request: 121
- Queries run: 26
- Query warnings: 6 search calls returned errors or parse failures; see method notes below.

## Queries Used

- `issues`: `"AI code review" "false positive"`
- `issues`: `"AI code review" bug`
- `issues`: `"coding agent" bug`
- `issues`: `"coding agent" regression`
- `issues`: `"agentic" "code review"`
- `issues`: `"Claude Code" bug`
- `issues`: `"Cursor" "agent" bug`
- `issues`: `"OpenAI Codex" bug`
- `issues`: `"GitHub Copilot" "code review"`
- `issues`: `"MCP" "agent" security`
- `issues`: `"AGENTS.md" "Codex"`
- `issues`: `"read-only" "agent" "pull request"`
- `repositories`: `agentic code review`
- `repositories`: `ai code review bot`
- `repositories`: `coding agent`
- `repositories`: `agent workflow kit`
- `repositories`: `agent governance`
- `repositories`: `AGENTS.md coding agent`
- `repositories`: `MCP security agent`
- `repositories`: `TDD coding agent`
- `code`: `"AGENTS.md" "coding agent"`
- `code`: `"CLAUDE.md" "rules"`
- `code`: `"session receipt" "agent"`
- `code`: `"read-only" "agent" "pull_request"`
- `code`: `"docs impact" "agent"`
- `code`: `"MCP" "allowlist" "agent"`

## Method Notes

- `search/issues` params `{'q': '"Cursor" "agent" bug', 'per_page': '50', 'sort': 'updated', 'order': 'desc'}` warning: gh: You have exceeded a secondary rate limit. Please wait a few minutes before you try again. For more on scraping GitHub and how it may affect your rights, please review our Terms of Service (https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) If you reach out to GitHub Support for help, please include the request ID 9415:1804E3:D156E3:ECC028:69F9D07A. (HTTP 403)
- `search/issues` params `{'q': '"OpenAI Codex" bug', 'per_page': '50', 'sort': 'updated', 'order': 'desc'}` warning: gh: You have exceeded a secondary rate limit. Please wait a few minutes before you try again. For more on scraping GitHub and how it may affect your rights, please review our Terms of Service (https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) If you reach out to GitHub Support for help, please include the request ID CCB2:1804E3:D15820:ECC198:69F9D07B. (HTTP 403)
- `search/issues` params `{'q': '"GitHub Copilot" "code review"', 'per_page': '50', 'sort': 'updated', 'order': 'desc'}` warning: gh: You have exceeded a secondary rate limit. Please wait a few minutes before you try again. For more on scraping GitHub and how it may affect your rights, please review our Terms of Service (https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) If you reach out to GitHub Support for help, please include the request ID D5A3:E577E:EB88A8:106F4AB:69F9D07D. (HTTP 403)
- `search/issues` params `{'q': '"MCP" "agent" security', 'per_page': '50', 'sort': 'updated', 'order': 'desc'}` warning: gh: You have exceeded a secondary rate limit. Please wait a few minutes before you try again. For more on scraping GitHub and how it may affect your rights, please review our Terms of Service (https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) If you reach out to GitHub Support for help, please include the request ID 90A0:E577E:EB8A40:106F66D:69F9D07E. (HTTP 403)
- `search/issues` params `{'q': '"AGENTS.md" "Codex"', 'per_page': '50', 'sort': 'updated', 'order': 'desc'}` warning: gh: You have exceeded a secondary rate limit. Please wait a few minutes before you try again. For more on scraping GitHub and how it may affect your rights, please review our Terms of Service (https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) If you reach out to GitHub Support for help, please include the request ID 937B:769E0:D3872D:EEE9AA:69F9D080. (HTTP 403)
- `search/issues` params `{'q': '"read-only" "agent" "pull request"', 'per_page': '50', 'sort': 'updated', 'order': 'desc'}` warning: gh: You have exceeded a secondary rate limit. Please wait a few minutes before you try again. For more on scraping GitHub and how it may affect your rights, please review our Terms of Service (https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) If you reach out to GitHub Support for help, please include the request ID 0D13:A478E:D2BE80:EE2830:69F9D082. (HTTP 403)

## Sources

1. https://github.com/JovieInc/Jovie/pull/7965
   - Type: pull_request
   - Project/owner: JovieInc/Jovie
   - Title/file: feat(calendar): add events to release calendar
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

2. https://github.com/mikelear/leartech-qa-canary/pull/1
   - Type: pull_request
   - Project/owner: mikelear/leartech-qa-canary
   - Title/file: chore: bootstrap test — verify first-PR pipelines
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

3. https://github.com/dashpay/dash/pull/7242
   - Type: pull_request
   - Project/owner: dashpay/dash
   - Title/file: backport: bitcoin#22764, #24505, #26074, #26039, #28230, #29277, #28597 (wallet deprecation + RPC type checking)
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

4. https://github.com/F0RLE/Axelate/pull/79
   - Type: pull_request
   - Project/owner: F0RLE/Axelate
   - Title/file: Refactor launcher runtime and chat flow
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

5. https://github.com/openshift/origin/pull/31122
   - Type: pull_request
   - Project/owner: openshift/origin
   - Title/file: Increase pathological event thresholds for API server rollout scenarios
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

6. https://github.com/GlacierEQ/kilocode/pull/1
   - Type: pull_request
   - Project/owner: GlacierEQ/kilocode
   - Title/file: sync to main
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

7. https://github.com/hoppscotch/hoppscotch/pull/6279
   - Type: pull_request
   - Project/owner: hoppscotch/hoppscotch
   - Title/file: fix: stop secret variable values from leaking to backend
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

8. https://github.com/trycompai/comp/pull/2671
   - Type: pull_request
   - Project/owner: trycompai/comp
   - Title/file: feat: ENG-221 — treatment plan as first-class + vendor AI widening + matrix polish
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

9. https://github.com/seungpyoson/codex-plugin-multi/pull/81
   - Type: pull_request
   - Project/owner: seungpyoson/codex-plugin-multi
   - Title/file: Expose external review lifecycle events
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

10. https://github.com/mercutiojohn/RSSHub/pull/35
   - Type: pull_request
   - Project/owner: mercutiojohn/RSSHub
   - Title/file: [pull] master from diygod:master
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

11. https://github.com/utkarshdalal/GameNative/pull/1146
   - Type: pull_request
   - Project/owner: utkarshdalal/GameNative
   - Title/file: Re-enable local saves only with cloud sync safety nets
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

12. https://github.com/teutonet/teutonet-helm-charts/pull/1981
   - Type: pull_request
   - Project/owner: teutonet/teutonet-helm-charts
   - Title/file: feat(base-cluster/monitoring)!: add alert for retention and automatically set retention based on size
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

13. https://github.com/StackOneHQ/agent-plugins-marketplace/pull/15
   - Type: pull_request
   - Project/owner: StackOneHQ/agent-plugins-marketplace
   - Title/file: feat(ENG-70): enable SFE preprocessing to reduce Bash false positives
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

14. https://github.com/PostHog/posthog/pull/57258
   - Type: pull_request
   - Project/owner: PostHog/posthog
   - Title/file: feat(insights): add sessionPropertyPreAggregation modifier
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

15. https://github.com/open-component-model/open-component-model/pull/2344
   - Type: pull_request
   - Project/owner: open-component-model/open-component-model
   - Title/file: feat(sigstore): add cosign signing handler [1/2]
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

16. https://github.com/FRRouting/frr/pull/20886
   - Type: pull_request
   - Project/owner: FRRouting/frr
   - Title/file: zebra: add json support for svd vxlan type
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

17. https://github.com/RedHatProductSecurity/aegis-ai/pull/560
   - Type: pull_request
   - Project/owner: RedHatProductSecurity/aegis-ai
   - Title/file: Kernel suggest impact integration
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

18. https://github.com/StackOneHQ/defender/pull/39
   - Type: pull_request
   - Project/owner: StackOneHQ/defender
   - Title/file: feat(ENG-129): add obfuscation normalisation chain to Tier 1 detection
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

19. https://github.com/peethr/n8n/pull/1
   - Type: pull_request
   - Project/owner: peethr/n8n
   - Title/file: Update
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

20. https://github.com/demisto/content/pull/43793
   - Type: pull_request
   - Project/owner: demisto/content
   - Title/file: [NGNIX API Module] Add Further Cache Controls
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

21. https://github.com/microlinkhq/www/pull/2021
   - Type: pull_request
   - Project/owner: microlinkhq/www
   - Title/file: chore: customers landing
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

22. https://github.com/n8n-io/n8n/pull/27044
   - Type: pull_request
   - Project/owner: n8n-io/n8n
   - Title/file: chore: Update pnpm catalog to 10.2.10 [SECURITY]
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

23. https://github.com/DataDog/rshell/pull/220
   - Type: pull_request
   - Project/owner: DataDog/rshell
   - Title/file: fix(review-fix-loop): only increment clean streak on no-findings iterations
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

24. https://github.com/Scottcjn/rustchain-bounties/issues/73
   - Type: issue
   - Project/owner: Scottcjn/rustchain-bounties
   - Title/file: [BOUNTY] Code Review Bounty Program — Review PRs, Earn RTC (100 RTC Pool)
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

25. https://github.com/tuist/tuist/pull/10489
   - Type: pull_request
   - Project/owner: tuist/tuist
   - Title/file: feat(server): manage Kura from ops
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

26. https://github.com/openclaw/openclaw/pull/68774
   - Type: pull_request
   - Project/owner: openclaw/openclaw
   - Title/file: fix(memory-core): prevent staged dream candidates from leaking into MEMORY.md
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

27. https://github.com/raycast/extensions/pull/27225
   - Type: pull_request
   - Project/owner: raycast/extensions
   - Title/file: Add paypal-invoices extension
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

28. https://github.com/1bananachicken/MaaNTE/pull/108
   - Type: pull_request
   - Project/owner: 1bananachicken/MaaNTE
   - Title/file: feat(rhythm): 优化节奏游戏场景检测和歌曲选择逻辑
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

29. https://github.com/Zipstack/unstract/pull/1929
   - Type: pull_request
   - Project/owner: Zipstack/unstract
   - Title/file: UN-2946 [FEAT] Prompt Studio lookups bridge, executor hook, and IDE wiring (OSS side)
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

30. https://github.com/seungpyoson/codex-plugin-multi/pull/82
   - Type: pull_request
   - Project/owner: seungpyoson/codex-plugin-multi
   - Title/file: Fix reviewer runtime diagnostics and cache drift visibility
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

31. https://github.com/mahendra-google/google-cloud-dotnet/pull/10
   - Type: pull_request
   - Project/owner: mahendra-google/google-cloud-dotnet
   - Title/file: feat(Storage): Enable full object checksum validation for multi chunk resumable uploads
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

32. https://github.com/aignostics/python-sdk/pull/513
   - Type: pull_request
   - Project/owner: aignostics/python-sdk
   - Title/file: feat(platform): support external token providers and simplify caching [PYSDK-123]
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

33. https://github.com/Dargon789/Rabby/pull/93
   - Type: pull_request
   - Project/owner: Dargon789/Rabby
   - Title/file: Snyk fix 9b5ecce84e737bc7781a872416e3930c
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

34. https://github.com/n8n-io/n8n/pull/29698
   - Type: pull_request
   - Project/owner: n8n-io/n8n
   - Title/file: feat(core): Add n8n-object-validation ESLint rule for community nodes
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

35. https://github.com/getsentry/XcodeBuildMCP/pull/391
   - Type: pull_request
   - Project/owner: getsentry/XcodeBuildMCP
   - Title/file: feat: Workspace filesystem cleanup
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

36. https://github.com/NVIDIA/physicsnemo/pull/1614
   - Type: pull_request
   - Project/owner: NVIDIA/physicsnemo
   - Title/file: Model state channels last checkpoint patch
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

37. https://github.com/jleechanorg/mctrl_test/pull/54
   - Type: pull_request
   - Project/owner: jleechanorg/mctrl_test
   - Title/file: feat: Word Ladder BFS solution
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

38. https://github.com/0xPolygon/bor/pull/2194
   - Type: pull_request
   - Project/owner: 0xPolygon/bor
   - Title/file: consensus/bor, internal/cli: full grpc implementation
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

39. https://github.com/Prekzursil/quality-zero-platform/pull/142
   - Type: pull_request
   - Project/owner: Prekzursil/quality-zero-platform
   - Title/file: fix(qzp-v2 phase 5): bump-shas JSON report — populate repo from target slug, not caller
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

40. https://github.com/Dougley/frugal/pull/136
   - Type: pull_request
   - Project/owner: Dougley/frugal
   - Title/file: fix(deps): update all non-major dependencies
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

41. https://github.com/useautumn/autumn/pull/1190
   - Type: pull_request
   - Project/owner: useautumn/autumn
   - Title/file: sync utils
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

42. https://github.com/lightspeed-core/lightspeed-stack/pull/1627
   - Type: pull_request
   - Project/owner: lightspeed-core/lightspeed-stack
   - Title/file: LCORE-203: Unified mcp registration endpoints
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

43. https://github.com/CalmKernelTR/turkish-llm-bench/pull/3
   - Type: pull_request
   - Project/owner: CalmKernelTR/turkish-llm-bench
   - Title/file: v0.3.0 Tier 1-3 — 8-vendor cross-validation findings + decisions audit trail
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

44. https://github.com/lightspeed-core/lightspeed-stack/pull/1683
   - Type: pull_request
   - Project/owner: lightspeed-core/lightspeed-stack
   - Title/file: LCORE-1983: Added e2e scenario for OpenTelemetry
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

45. https://github.com/fossasia/eventyay/pull/3081
   - Type: pull_request
   - Project/owner: fossasia/eventyay
   - Title/file: Allow users to cancel individual tickets within an order
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

46. https://github.com/n8n-io/n8n/pull/29452
   - Type: pull_request
   - Project/owner: n8n-io/n8n
   - Title/file: feat: Add valid-credential-references ESLint rule
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

47. https://github.com/n8n-io/n8n/pull/29500
   - Type: pull_request
   - Project/owner: n8n-io/n8n
   - Title/file: fix(ai-builder): Handle properties with contradicting displayOptions as OR alternatives instead of AND
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

48. https://github.com/quazfenton/binG/pull/79
   - Type: pull_request
   - Project/owner: quazfenton/binG
   - Title/file: ruInS
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

49. https://github.com/leynos/visual-storytelling-skills/pull/1
   - Type: pull_request
   - Project/owner: leynos/visual-storytelling-skills
   - Title/file: Add shot specifier and phoneticize skills
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

50. https://github.com/alpic-ai/skybridge/pull/635
   - Type: pull_request
   - Project/owner: alpic-ai/skybridge
   - Title/file: fix(deps): update all non-major dependencies
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" "false positive"
   - Pattern/risk keyword: `"AI code review" "false positive"`

51. https://github.com/EndeavorEverlasting/AxTask/pull/5
   - Type: pull_request
   - Project/owner: EndeavorEverlasting/AxTask
   - Title/file: feat(gantt): ship free task Gantt + avatar/coin-gated customization pack
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

52. https://github.com/Marin-Solutions/checkybot/pull/189
   - Type: pull_request
   - Project/owner: Marin-Solutions/checkybot
   - Title/file: Fix SEO checks first-run setup
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

53. https://github.com/Utkarshchaudhary009/dr.t/pull/3
   - Type: pull_request
   - Project/owner: Utkarshchaudhary009/dr.t
   - Title/file: Fix Telegram greeting loop so direct messages reach AI pipeline
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

54. https://github.com/phoenix-rtos/phoenix-rtos-kernel/pull/749
   - Type: pull_request
   - Project/owner: phoenix-rtos/phoenix-rtos-kernel
   - Title/file: vm: improve error handling
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

55. https://github.com/CesiumGS/cesium/pull/13463
   - Type: pull_request
   - Project/owner: CesiumGS/cesium
   - Title/file: Fix useless assignments
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

56. https://github.com/JovieInc/Jovie/pull/7986
   - Type: pull_request
   - Project/owner: JovieInc/Jovie
   - Title/file: feat(waitlist): add chat access gate
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

57. https://github.com/openplaud/openplaud/pull/76
   - Type: pull_request
   - Project/owner: openplaud/openplaud
   - Title/file: fix(upload): parse audio duration in JS, drop ffprobe dependency
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

58. https://github.com/KooshaPari/PhenoProject/pull/56
   - Type: pull_request
   - Project/owner: KooshaPari/PhenoProject
   - Title/file: Harden Taskfile Python project detection
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

59. https://github.com/n8n-io/n8n/pull/29701
   - Type: pull_request
   - Project/owner: n8n-io/n8n
   - Title/file: fix(core): Improve AI chat file upload handling and error states
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

60. https://github.com/getsentry/sentry-java/pull/5366
   - Type: pull_request
   - Project/owner: getsentry/sentry-java
   - Title/file: fix(feedback): Improve shake detection sensitivity
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

61. https://github.com/konflux-ci/konflux-ci/pull/6336
   - Type: pull_request
   - Project/owner: konflux-ci/konflux-ci
   - Title/file: fix(KFLUXVNGD-876): Envtest suites bypass SetupWithManager
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

62. https://github.com/meshery/meshery/pull/17423
   - Type: pull_request
   - Project/owner: meshery/meshery
   - Title/file: chore: Migrate E2E test 'extensions.spec.js' to TypeScript
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

63. https://github.com/stackrox/stackrox/pull/20155
   - Type: pull_request
   - Project/owner: stackrox/stackrox
   - Title/file: feat(roxctl): migrate-to-operator subcommands
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

64. https://github.com/daytonaio/daytona/pull/4594
   - Type: pull_request
   - Project/owner: daytonaio/daytona
   - Title/file: Feat/sandbox sheet revamp
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

65. https://github.com/withcoral/coral/pull/208
   - Type: pull_request
   - Project/owner: withcoral/coral
   - Title/file: chore(main): release 0.2.0
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

66. https://github.com/PostHog/posthog/pull/56763
   - Type: pull_request
   - Project/owner: PostHog/posthog
   - Title/file: feat(llma): ai events strip fixes
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

67. https://github.com/dashpay/dash-evo-tool/pull/763
   - Type: pull_request
   - Project/owner: dashpay/dash-evo-tool
   - Title/file: fix: auto-fetch profile from network when no cached data exists
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

68. https://github.com/Tracer-Cloud/opensre/pull/1302
   - Type: pull_request
   - Project/owner: Tracer-Cloud/opensre
   - Title/file: fix(claude-code): parse auth status JSON before exit code; use authMethod (#1260)
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

69. https://github.com/Voornaamenachternaam/aad-sso-wordpress-ng/pull/22
   - Type: pull_request
   - Project/owner: Voornaamenachternaam/aad-sso-wordpress-ng
   - Title/file: Achieve PHPStan level max with complete type safety
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

70. https://github.com/open-mercato/open-mercato/pull/1593
   - Type: pull_request
   - Project/owner: open-mercato/open-mercato
   - Title/file: feat(ai-framework): AI framework unification + testing subagents flow with better agent -> human communication
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

71. https://github.com/Marin-Solutions/checkybot/pull/190
   - Type: pull_request
   - Project/owner: Marin-Solutions/checkybot
   - Title/file: Validate API assertion regex patterns
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

72. https://github.com/Katsiarynakavaleuskaya/PulsePlate/pull/1665
   - Type: pull_request
   - Project/owner: Katsiarynakavaleuskaya/PulsePlate
   - Title/file: fix(security): include rag-vector-cpu profile in dependency controls
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

73. https://github.com/n8n-io/n8n/pull/29549
   - Type: pull_request
   - Project/owner: n8n-io/n8n
   - Title/file: fix: Fix 2 security issues in axios, fast-xml-parser
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

74. https://github.com/bulletxyz/bullet-exchange-interface/pull/26
   - Type: pull_request
   - Project/owner: bulletxyz/bullet-exchange-interface
   - Title/file: feat(security): added pyth signature support
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

75. https://github.com/getsentry/sentry-java/pull/5365
   - Type: pull_request
   - Project/owner: getsentry/sentry-java
   - Title/file: chore(deps): update Native SDK to v0.14.0
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

76. https://github.com/paperclipai/paperclip/pull/5263
   - Type: pull_request
   - Project/owner: paperclipai/paperclip
   - Title/file: fix: routine execution zombie gap — constraint + skip_if_active + force-terminate
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

77. https://github.com/mendixlabs/mxcli/pull/519
   - Type: pull_request
   - Project/owner: mendixlabs/mxcli
   - Title/file: fix: infer SingleObject from import mapping root when JsonStructure absent
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

78. https://github.com/KooshaPari/helioscope/pull/271
   - Type: pull_request
   - Project/owner: KooshaPari/helioscope
   - Title/file: chore: pin GitHub Actions to specific SHAs
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

79. https://github.com/n8n-io/n8n/pull/28017
   - Type: pull_request
   - Project/owner: n8n-io/n8n
   - Title/file: feat: Include @n8n/agents in backend (no-changelog)
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

80. https://github.com/DashFin-FarDb/financial-asset-relationship-db/pull/1119
   - Type: pull_request
   - Project/owner: DashFin-FarDb/financial-asset-relationship-db
   - Title/file: Add graph persistence round-trip contract tests
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

81. https://github.com/RedHatInsights/insights-rbac/pull/2825
   - Type: pull_request
   - Project/owner: RedHatInsights/insights-rbac
   - Title/file: Bump dependencies
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

82. https://github.com/zarbopiero963-droid/Pickfair-nogui/pull/214
   - Type: pull_request
   - Project/owner: zarbopiero963-droid/Pickfair-nogui
   - Title/file: [TASK: claude_bug_pr2b_workflow_shell_injection] Harden module ultra-check workflow shell interpolation
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

83. https://github.com/thpoll83/PolyKybdHost/pull/3
   - Type: pull_request
   - Project/owner: thpoll83/PolyKybdHost
   - Title/file: feat: LRU overlay cache mode to reduce HID traffic on app switch
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

84. https://github.com/speakeasy-api/gram/pull/2181
   - Type: pull_request
   - Project/owner: speakeasy-api/gram
   - Title/file: feat: skills registry
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

85. https://github.com/n8n-io/n8n/pull/29636
   - Type: pull_request
   - Project/owner: n8n-io/n8n
   - Title/file: feat(ai-builder): Guarantee user-visible output on terminal states
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

86. https://github.com/freeipa/freeipa/pull/8264
   - Type: pull_request
   - Project/owner: freeipa/freeipa
   - Title/file: ipatests: Add AD trust NFS automount integration tests
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

87. https://github.com/Huynhthuongg/EIOS-CLI/pull/1
   - Type: pull_request
   - Project/owner: Huynhthuongg/EIOS-CLI
   - Title/file: Add Vercel Speed Insights integration
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

88. https://github.com/KooshaPari/McpKit/pull/34
   - Type: pull_request
   - Project/owner: KooshaPari/McpKit
   - Title/file: chore: add language-aware taskfile
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

89. https://github.com/n8n-io/n8n/pull/29688
   - Type: pull_request
   - Project/owner: n8n-io/n8n
   - Title/file: fix(Notion Node): Serialize staticData as ISO string in NotionTrigger
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

90. https://github.com/osbuild/image-builder-frontend/pull/4383
   - Type: pull_request
   - Project/owner: osbuild/image-builder-frontend
   - Title/file: Wizard/ImageOutput: filter supported bootc environments by distro (HMS-10618)
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

91. https://github.com/daytonaio/daytona/pull/4626
   - Type: pull_request
   - Project/owner: daytonaio/daytona
   - Title/file: feat(guides): Flue guide
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

92. https://github.com/2digits-agency/configs/pull/2036
   - Type: pull_request
   - Project/owner: 2digits-agency/configs
   - Title/file: Update dependency @typescript/native-preview to v7.0.0-dev.20260505.1
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

93. https://github.com/CalmKernelTR/turkish-llm-bench/pull/6
   - Type: pull_request
   - Project/owner: CalmKernelTR/turkish-llm-bench
   - Title/file: v0.3.0 Tier 4-6 — artifacts, scripts, charts, leaderboard, CHANGELOG, README
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

94. https://github.com/getsentry/sentry-native/pull/1694
   - Type: pull_request
   - Project/owner: getsentry/sentry-native
   - Title/file: fix(native): Fix smaller findings for Linux minidump writer
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

95. https://github.com/blinklabs-io/dingo/pull/2168
   - Type: pull_request
   - Project/owner: blinklabs-io/dingo
   - Title/file: database: include block_index in cert ordering for account restore
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

96. https://github.com/sanjaydgtoohl/lms-backend/pull/95
   - Type: pull_request
   - Project/owner: sanjaydgtoohl/lms-backend
   - Title/file: Add fields on user table organisation and zone
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

97. https://github.com/firecrawl/firecrawl/pull/3481
   - Type: pull_request
   - Project/owner: firecrawl/firecrawl
   - Title/file: fix(elixir-sdk): proper error handling for API responses and string enum support
   - Raw relevance note: Matched GitHub issue/PR search query: "AI code review" bug
   - Pattern/risk keyword: `"AI code review" bug`

98. https://github.com/agentfront/frontmcp/pull/393
   - Type: pull_request
   - Project/owner: agentfront/frontmcp
   - Title/file: Skill over mcp
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

99. https://github.com/hashintel/hash/pull/8569
   - Type: pull_request
   - Project/owner: hashintel/hash
   - Title/file: Update `playwright` npm packages
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

100. https://github.com/numbersprotocol/proofsnap-extension/pull/28
   - Type: pull_request
   - Project/owner: numbersprotocol/proofsnap-extension
   - Title/file: Add CI/CD pipeline, linting, debounced settings, and cleanup improvements
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

101. https://github.com/microsoft/vscode/issues/293826
   - Type: issue
   - Project/owner: microsoft/vscode
   - Title/file: Github Copilot Edit mode gone after latest update?
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

102. https://github.com/onixldlc/CodeFormer/pull/5
   - Type: pull_request
   - Project/owner: onixldlc/CodeFormer
   - Title/file: fix: replace deprecated `setup.py develop` with `pip install -e` for basicsr
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

103. https://github.com/valory-xyz/olas-operate-app/pull/1909
   - Type: pull_request
   - Project/owner: valory-xyz/olas-operate-app
   - Title/file: feat(agents): block new agent creation for Polystrat, Optimus and Agents.fun
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

104. https://github.com/electron/electron/pull/51425
   - Type: pull_request
   - Project/owner: electron/electron
   - Title/file: fix: remove atspi active state for background apps
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

105. https://github.com/grafana/traces-drilldown/pull/704
   - Type: pull_request
   - Project/owner: grafana/traces-drilldown
   - Title/file: chore(deps): update dependency @playwright/test to v1.59.1
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

106. https://github.com/Aivar-Siva/PLAN-Kiro-LCCA/pull/3
   - Type: pull_request
   - Project/owner: Aivar-Siva/PLAN-Kiro-LCCA
   - Title/file: Version1.0
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

107. https://github.com/envoyproxy/envoy/pull/44854
   - Type: pull_request
   - Project/owner: envoyproxy/envoy
   - Title/file: deps: bump hickory-proto/hickory-resolver 0.25.2 → 0.26.1 (RUSTSEC-2026-0118, RUSTSEC-2026-0119)
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

108. https://github.com/Vatsal143/skills-getting-started-with-github-copilot/issues/1
   - Type: issue
   - Project/owner: Vatsal143/skills-getting-started-with-github-copilot
   - Title/file: Exercise: Getting Started with GitHub Copilot
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

109. https://github.com/bharatsingh390-hash/skills-getting-started-with-github-copilot/issues/1
   - Type: issue
   - Project/owner: bharatsingh390-hash/skills-getting-started-with-github-copilot
   - Title/file: Exercise: Getting Started with GitHub Copilot
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

110. https://github.com/narasam/skills-getting-started-with-github-copilot/issues/1
   - Type: issue
   - Project/owner: narasam/skills-getting-started-with-github-copilot
   - Title/file: Exercise: Getting Started with GitHub Copilot
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

111. https://github.com/oven-sh/bun/pull/29359
   - Type: pull_request
   - Project/owner: oven-sh/bun
   - Title/file: test: sync Node.js test suite with v24.14.1 (d89bb1b482)
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

112. https://github.com/indexnetwork/index/pull/725
   - Type: pull_request
   - Project/owner: indexnetwork/index
   - Title/file: feat: notify counterparty with Telegram deep link on opportunity acceptance
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

113. https://github.com/msmyrn96/skills-getting-started-with-github-copilot/issues/1
   - Type: issue
   - Project/owner: msmyrn96/skills-getting-started-with-github-copilot
   - Title/file: Exercise: Getting Started with GitHub Copilot
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

114. https://github.com/grafana/x-ray-datasource/pull/656
   - Type: pull_request
   - Project/owner: grafana/x-ray-datasource
   - Title/file: chore(deps): update frontend dependencies
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

115. https://github.com/david-mangoro/skills-getting-started-with-github-copilot/issues/1
   - Type: issue
   - Project/owner: david-mangoro/skills-getting-started-with-github-copilot
   - Title/file: Exercise: Getting Started with GitHub Copilot
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

116. https://github.com/generative-computing/mellea/pull/942
   - Type: pull_request
   - Project/owner: generative-computing/mellea
   - Title/file: feat(stdlib): add stream_with_chunking() with per-chunk validation (#901)
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

117. https://github.com/Lynquatiq/vscode/pull/1
   - Type: pull_request
   - Project/owner: Lynquatiq/vscode
   - Title/file: JABU SHIRUKU
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

118. https://github.com/leynos/rstest-bdd/pull/482
   - Type: pull_request
   - Project/owner: leynos/rstest-bdd
   - Title/file: Fix release publish dependency isolation
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

119. https://github.com/onixldlc/CodeFormer/pull/4
   - Type: pull_request
   - Project/owner: onixldlc/CodeFormer
   - Title/file: Fix broken Docker build: replace deprecated `setup.py develop` with pip editable install
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

120. https://github.com/twclarkee/skills-getting-started-with-github-copilot/issues/1
   - Type: issue
   - Project/owner: twclarkee/skills-getting-started-with-github-copilot
   - Title/file: Exercise: Getting Started with GitHub Copilot
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

121. https://github.com/k1nG-z00f/MVPyPicks/pull/1
   - Type: pull_request
   - Project/owner: k1nG-z00f/MVPyPicks
   - Title/file: [WIP] Create skeleton Django REST application framework
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

122. https://github.com/networklessons/labs/pull/64
   - Type: pull_request
   - Project/owner: networklessons/labs
   - Title/file: Update actions/setup-python action to v6
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

123. https://github.com/md-muntasir-shihab/Campusway-BD/pull/29
   - Type: pull_request
   - Project/owner: md-muntasir-shihab/Campusway-BD
   - Title/file: Remove unused `react-quill` dependency blocking CI with React 19
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

124. https://github.com/onixldlc/CodeFormer/pull/3
   - Type: pull_request
   - Project/owner: onixldlc/CodeFormer
   - Title/file: fix: replace deprecated `python setup.py develop` with `pip install -e` in Dockerfile
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

125. https://github.com/getlarge/themoltnet/pull/997
   - Type: pull_request
   - Project/owner: getlarge/themoltnet
   - Title/file: fix(api,sdk): unified PrincipalIdentity creator model (closes #992)
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

126. https://github.com/coollabsio/coolify/pull/9931
   - Type: pull_request
   - Project/owner: coollabsio/coolify
   - Title/file: feat(api): add application and server terminal command endpoints
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

127. https://github.com/leynos/netsuke/pull/285
   - Type: pull_request
   - Project/owner: leynos/netsuke
   - Title/file: Expose --config <PATH> and NETSUKE_CONFIG precedence (3.11.3)
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

128. https://github.com/vllm-project/vllm/pull/38476
   - Type: pull_request
   - Project/owner: vllm-project/vllm
   - Title/file: [WIP] Add TRITON_MLA_SPARSE backend for SM80 sparse MLA support
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

129. https://github.com/JetBrains/junie-github-action/pull/140
   - Type: pull_request
   - Project/owner: JetBrains/junie-github-action
   - Title/file: [Junie]: Update Junie CLI Version to 1543.12 in Files
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`

130. https://github.com/didwanm/skills-getting-started-with-github-copilot/issues/1
   - Type: issue
   - Project/owner: didwanm/skills-getting-started-with-github-copilot
   - Title/file: Exercise: Getting Started with GitHub Copilot
   - Raw relevance note: Matched GitHub issue/PR search query: "coding agent" bug
   - Pattern/risk keyword: `"coding agent" bug`
