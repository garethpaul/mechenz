# Nested Action Parser Depth

status: planned

## Context

`ActionParser` currently increments its action depth only for `div.action`
elements but decrements that depth for every closing `div`. A non-action
container inside an action can therefore end the action early and silently
drop the first span that follows it.

The failure is reproducible offline with:

```html
<div class="action"><div class="metadata">Meta</div><span>Expected</span></div>
```

The parser currently returns no actions for that response shape.

## Planned Scope

- Track the complete open-element stack while an action is active so only the
  matching action container ends that action.
- Preserve the existing contract of returning only the first non-empty span
  from each action.
- Add focused tests for an ordinary nested container before the first span and
  nested markup inside the captured span.
- Extend the static baseline and project documentation with the parser-depth
  contract and completed verification evidence.

## Out Of Scope

- Live target requests or scraped production fixtures.
- Changes to scrape settings, response-size limits, cache behavior, or email
  delivery.
- Broad HTML parsing or selector-library replacement.

## Planned Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- Mutation checks that reject premature action closure, flattened span text,
  stale plan status, and missing verification evidence.
- `git diff --check`
- Secret and generated-artifact inspection limited to intended paths.
