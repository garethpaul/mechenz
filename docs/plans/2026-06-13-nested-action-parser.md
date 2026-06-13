# Nested Action Parser Depth

status: completed

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
- Preserve the existing contract of returning only the first span from each
  action when it contains text.
- Add focused tests for an ordinary nested container before the first span and
  nested markup inside the captured span.
- Extend the static baseline and project documentation with the parser-depth
  contract and completed verification evidence.

## Out Of Scope

- Live target requests or scraped production fixtures.
- Changes to scrape settings, response-size limits, cache behavior, or email
  delivery.
- Broad HTML parsing or selector-library replacement.

## Work Completed

- Made active action depth account for every nested `div`, while only an
  outer `div.action` starts a new action.
- Added offline coverage for a nested metadata container before the first span
  and nested inline markup within that span.
- Extended the baseline checker and project documentation with the response
  shape contract.

## Verification Completed

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m unittest discover -s tests -p 'test_main.py' -v` (13 tests)
- `test_extract_actions_keeps_action_open_across_nested_div`
- `test_extract_actions_collects_nested_markup_inside_first_span`
- Mutation checks reject premature action closure, flattened span text, stale
  plan status, and missing verification evidence.
- `git diff --check`
- Secret and generated-artifact inspection limited to intended paths
