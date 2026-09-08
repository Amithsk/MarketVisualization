# AGENTS.md --- Intraday Analysis Project

## Purpose

This repository contains the Intraday Analysis project, including
market-data handling, Zerodha integration, intraday analysis,
charts/visualizations, trade-plan workflows, and the supporting
frontend/backend logic.

This file defines the persistent development rules for Codex.

The goal is to make changes safely and incrementally while preserving
existing working behaviour.

------------------------------------------------------------------------

# 1. Mandatory Development Workflow

For every development task, follow this sequence:

## ANALYZE

Before changing code:

1.  Inspect the existing implementation.
2.  Identify the relevant files, modules, components, functions, APIs,
    database interactions, and data flow.
3.  Understand the current behaviour and why it behaves that way.
4.  Trace the data from source to backend to frontend where applicable.
5.  Identify dependencies and possible side effects.
6.  Check whether the requested behaviour already exists partially.
7.  Look for existing reusable logic before introducing new logic.
8.  Do not modify code during the analysis phase.

The analysis must be based on the actual repository implementation, not
assumptions.

### Analysis output

Report:

-   Current implementation
-   Relevant files/components
-   Current data flow
-   Root cause or implementation gap
-   Dependencies
-   Potential side effects
-   Proposed scope of change

------------------------------------------------------------------------

## PLAN

After analysis:

1.  Define the smallest safe implementation that satisfies the
    requirement.
2.  Identify the exact files/components that need modification.
3.  Explicitly identify files/components that should NOT be changed.
4.  Explain how the change interacts with existing functionality.
5.  Consider edge cases and backward compatibility.
6.  Consider frontend/backend/data consistency.
7.  Do not implement unrelated improvements.

If the requirement is ambiguous, stop and identify the ambiguity instead
of guessing.

------------------------------------------------------------------------

## IMPLEMENT

When implementation is authorized:

1.  Make only the changes required for the approved plan.
2.  Preserve existing working functionality.
3.  Follow the existing architecture and coding conventions.
4.  Reuse existing functions/components/services where appropriate.
5.  Avoid unnecessary refactoring.
6.  Do not change unrelated APIs, database structures, UI behaviour, or
    business logic.
7.  Do not replace an existing implementation merely because another
    approach looks cleaner.
8.  Keep changes focused and reviewable.

------------------------------------------------------------------------

## VALIDATE

After implementation:

1.  Run the relevant tests, checks, or build commands.
2.  Validate the affected functionality.
3.  Check for regressions.
4.  Validate important edge cases.
5.  For frontend changes, verify responsive/dynamic behaviour where
    relevant.
6.  For backend/data changes, verify data flow and error handling.
7.  For market-data changes, verify market-hours behaviour and request
    behaviour.
8.  Clearly distinguish validated behaviour from assumptions.

------------------------------------------------------------------------

## REPORT

Every completed task should report:

1.  What was changed
2.  Files changed
3.  Why the changes were required
4.  Root cause, when fixing a bug
5.  Validation performed
6.  Test/build results
7.  Any remaining limitations or risks
8.  Any unrelated improvements noticed but intentionally NOT implemented

------------------------------------------------------------------------

# 2. Scope Control --- Very Important

The project is under active development.

Do NOT:

-   Refactor unrelated code.
-   Rename unrelated variables, functions, components, or files.
-   Change working functionality while fixing another issue.
-   Modify database schemas unless explicitly requested.
-   Change API contracts unless explicitly requested.
-   Change authentication behaviour unless explicitly requested.
-   Replace an existing architecture without discussing it first.
-   Introduce new dependencies unless necessary.
-   Make broad UI redesigns when the task is a specific UI fix.
-   Fix unrelated bugs discovered during analysis.
-   Remove existing functionality because it appears unnecessary.
-   Make assumptions about trading rules that are not present in the
    requirement.

If a better improvement is discovered outside the requested scope:

-   Do NOT implement it automatically.
-   Mention it separately in the final report as a recommendation.

The default principle is:

> Make the smallest safe change that fully satisfies the requirement.

------------------------------------------------------------------------

# 3. Source of Truth

The existing repository is the primary source of truth for
implementation details.

Before changing behaviour:

1.  Inspect the code.
2.  Trace the current behaviour.
3.  Understand existing assumptions.
4.  Identify the actual root cause.
5.  Then implement the smallest appropriate change.

Do not guess when the codebase can answer the question.

If documentation conflicts with the actual implementation, call out the
discrepancy before making a broad change.

------------------------------------------------------------------------

# 4. Intraday Analysis Project Rules

This project is focused on intraday market analysis.

Changes involving market data, candles, indicators, analysis, charts,
trade plans, or market-session behaviour must preserve consistency
across the complete data flow.

Where applicable, consider:

-   Market session
-   Candle timestamps
-   Candle interval
-   Historical data
-   Local/cached data
-   Live market data
-   Volume
-   Indicators
-   Trade-plan state
-   Frontend visualization
-   Backend processing
-   Database persistence

A change that appears correct in isolation must not introduce
inconsistency elsewhere in the analysis pipeline.

------------------------------------------------------------------------

# 5. Market Hours and Live Data

## Core principle

Live market requests should be restricted to the live trading session.

The project should avoid unnecessary live requests outside market hours.

For any feature involving live market data, first determine:

1.  Is the request occurring during the live trading session?
2.  Is the required data already available locally?
3.  Can the result be produced from existing historical/local data?
4.  Is a live request actually necessary?

------------------------------------------------------------------------

# 6. Local/Historical Data First, Live Data as Fallback

The intended market-data strategy is:

``` text
Request generated
       |
       v
Is the request during live trading hours?
       |
   +---+---+
   |       |
  NO      YES
   |       |
   v       v
Use      Check local/
available cached/ historical
historical data
data          |
               v
       Is required data present?
            /       \
          YES        NO
           |          |
           v          v
      Use local    Fetch live
        data         data
                      |
                      v
               Persist/use data
```

## During live trading hours

1.  Check whether the required data exists locally.
2.  If the required data exists, use the local data.
3.  Avoid making an unnecessary live API request.
4.  If the required data is missing or insufficient, fetch the required
    live data.
5.  Where appropriate, persist newly fetched data so subsequent requests
    can reuse it.
6.  Return the result.

## Outside live trading hours

1.  Do not trigger live market-data requests merely because an analysis
    request was generated.
2.  Use available historical/local data where appropriate.
3.  If live data is explicitly required for a future/live-only workflow,
    identify that requirement rather than silently making an unnecessary
    live request.

The purpose of this strategy is to reduce latency, reduce unnecessary
external API requests, and reduce dependency on live-data availability
while maintaining correct intraday behaviour.

------------------------------------------------------------------------

# 7. Zerodha Integration Rules

The project contains Zerodha integration.

When modifying Zerodha-related functionality:

1.  Preserve existing authentication behaviour.
2.  Do not introduce unnecessary API calls.
3.  Respect API/request limitations.
4.  Reuse existing integration logic where possible.
5.  Do not modify unrelated Zerodha workflows.
6.  Do not change authentication/session handling unless explicitly
    requested.
7.  Validate both successful and failure paths where practical.
8.  Consider rate limiting and request frequency for every new external
    request.

Any change that increases the number of external requests should be
explicitly justified.

------------------------------------------------------------------------

# 8. Market Data Request Efficiency

When implementing or modifying market-data retrieval:

Prefer:

``` text
Existing/local data
        ↓
Reuse if sufficient
        ↓
Fetch only missing data
        ↓
Persist when appropriate
```

Avoid:

``` text
Every request
      ↓
Always call live API
```

The implementation should minimize:

-   Network latency
-   Duplicate API requests
-   Repeated downloads
-   Unnecessary Zerodha requests
-   Repeated processing of unchanged data

Do not optimize by sacrificing correctness.

------------------------------------------------------------------------

# 9. Candle and Timestamp Rules

Candle timestamps are important to the analysis.

When modifying candle-related functionality:

1.  Preserve the actual candle timestamp.
2.  Keep candle ordering chronological.
3.  Ensure each candle is associated with its correct timeframe.
4.  Do not introduce artificial time gaps.
5.  Do not hard-code timestamp positioning in the UI when the timestamp
    can be derived from actual candle data.
6.  Preserve consistency between backend timestamps, database
    timestamps, and frontend display.

The time axis should represent the actual candle sequence appropriately.

------------------------------------------------------------------------

# 10. Chart and Timeline Behaviour

The project contains chart/timeline visualizations.

When modifying chart or timeline behaviour:

-   Candle-to-timestamp association must remain correct.
-   The UI should derive positioning from actual data rather than
    arbitrary fixed positioning.
-   Do not use static pixel offsets to solve dynamic data-layout
    problems unless there is a clear technical reason.
-   Layouts must adapt to different values, text lengths, and screen
    sizes.
-   Do not assume that Nifty and individual stocks will always produce
    identical text widths or data ranges.
-   Avoid overlap between labels, volume values, percentage changes,
    indicators, and other chart elements.
-   Prefer flex/grid/layout constraints, calculated dimensions,
    wrapping, or other dynamic mechanisms where appropriate.

If a UI issue appears only for Nifty or another specific instrument,
investigate the underlying data/content dimensions before introducing an
instrument-specific hard-coded offset.

------------------------------------------------------------------------

# 11. Dynamic UI Principle

A recurring requirement in this project is that UI elements must be
dynamic rather than statically positioned.

For example, when displaying:

-   Volume
-   Volume change %
-   Price change %
-   Indicator values
-   Candle labels
-   Trade-plan markers
-   Timeline labels

do not assume a fixed width will always be sufficient.

Prefer:

-   Dynamic layout
-   Content-aware sizing
-   Responsive positioning
-   Proper spacing
-   Text wrapping where appropriate
-   CSS/layout mechanisms that respond to content

A solution should work for both:

-   Individual stocks
-   Nifty/index data

and should not depend on one specific number of digits or text length.

------------------------------------------------------------------------

# 12. Volume and Volume-Change Display

When modifying volume displays:

-   Volume and volume-change percentage must remain independently
    readable.
-   Percentage text must not overlap the volume value.
-   The layout must accommodate different number lengths.
-   Do not solve the problem with a fixed position that only works for
    one instrument.
-   Test with both stock and Nifty/index data.
-   Test with different volume magnitudes and percentage lengths.

If the same component behaves correctly for stocks but incorrectly for
Nifty, investigate content size/layout constraints before creating
separate static positioning rules.

------------------------------------------------------------------------

# 13. Trade Plan and Timeline

The project includes trade-plan workflows.

When modifying trade-plan visualization:

-   Keep candles aligned with their actual timeframe.
-   Preserve the association between trade-plan events and their
    underlying candle timestamps.
-   When a trade plan exits, ensure subsequent timeline/candle alignment
    remains based on actual timestamps/data.
-   Do not introduce artificial spacing merely to make a mockup visually
    appear correct.
-   Distinguish between temporary mockup behaviour and production
    data-driven behaviour.

If a visual alignment issue is known to be related to mockup data rather
than the production data model, do not over-engineer a permanent
workaround.

------------------------------------------------------------------------

# 14. Indicator/Data Processing Rules

Indicator calculations must preserve the required historical context.

When modifying indicator processing:

1.  Understand how many candles are required for each indicator.
2.  Do not silently discard source data without understanding why.
3.  If `dropna()` or equivalent filtering is used, verify which rows are
    being removed and why.
4.  Distinguish between:
    -   Source data
    -   Processed data
    -   Indicator-valid data
    -   Inserted database data

For example, if an indicator requires 20 candles, the first candles may
legitimately have unavailable indicator values. Do not treat this
automatically as a duplicate-data problem.

Any change to indicator preprocessing should validate row counts before
and after processing.

------------------------------------------------------------------------

# 15. Database Rules

When modifying database-related logic:

-   Preserve existing schema unless explicitly requested.
-   Do not delete or overwrite data unnecessarily.
-   Understand insertion/update semantics before modifying them.
-   Check for duplicate handling separately from indicator-related
    filtering.
-   Validate source-row count versus processed-row count versus
    inserted-row count.
-   Preserve timestamps and instrument identity.
-   Avoid destructive migrations without explicit approval.

When investigating missing rows, trace:

``` text
Source data
   ↓
Data cleaning
   ↓
Indicator calculation
   ↓
NaN filtering
   ↓
Duplicate handling
   ↓
Database insertion
```

Do not assume missing rows are duplicates without tracing this pipeline.

------------------------------------------------------------------------

# 16. Testing and Validation Strategy

For every meaningful change:

## Functional validation

Verify the requested behaviour.

## Regression validation

Verify nearby existing functionality still works.

## Data validation

Where market data is involved, check:

-   Number of source rows
-   Number of processed rows
-   Number of valid rows
-   Number of inserted rows
-   Timestamp continuity
-   Instrument identity
-   Indicator availability

## UI validation

For UI changes, verify:

-   Normal stock data
-   Nifty/index data
-   Different value lengths
-   Different screen widths where relevant
-   No text overlap
-   Correct candle/timestamp association

## API validation

For external data changes, verify:

-   Requests occur only when necessary
-   Local data is reused where available
-   Live fallback works when local data is insufficient
-   Requests outside the intended market session are not triggered
    unnecessarily

------------------------------------------------------------------------

# 17. Do Not Over-Optimize During a Bug Fix

The project is still evolving.

If the task is:

> Fix a specific bug

then fix the bug first.

Do not automatically:

-   Rewrite the component
-   Rewrite the API layer
-   Replace the data architecture
-   Introduce a new state-management system
-   Refactor unrelated modules
-   Change database structure

If architectural improvement is warranted, report it separately.

------------------------------------------------------------------------

# 18. Requirements Traceability

For each task, identify the requirement being implemented.

A useful format is:

``` text
Requirement
    ↓
Current behaviour
    ↓
Gap/root cause
    ↓
Implementation
    ↓
Validation
```

This is especially important for the intraday-analysis project because
multiple features interact with the same market-data pipeline.

------------------------------------------------------------------------

# 19. Communication Protocol

When a task is given to Codex, do not immediately start making changes
if the task requires meaningful repository analysis.

First determine whether the user asked for:

-   Analysis only
-   Analysis + plan
-   Implementation
-   Implementation + validation

If the user explicitly says:

> "Analyze only"

then do not modify files.

If the user says:

> "Do not change anything"

then analysis/reporting only.

If implementation is requested, still perform analysis before changing
code.

------------------------------------------------------------------------

# 20. Change Discipline

Every change should be:

-   Focused
-   Minimal
-   Reversible where practical
-   Consistent with existing architecture
-   Supported by validation

Avoid large batches of unrelated changes.

When multiple issues are present, separate them into independent changes
unless they genuinely share the same root cause.

------------------------------------------------------------------------

# 21. Recommended Task Format

When receiving a development request, internally structure the task as:

``` text
ANALYZE
↓
What currently happens?
Why does it happen?
Where is it implemented?

PLAN
↓
What is the smallest safe change?
Which files are affected?
What remains untouched?

IMPLEMENT
↓
Make only the approved changes.

VALIDATE
↓
Run relevant checks/tests.
Verify the requested behaviour.
Check regressions.

REPORT
↓
Changed files
Root cause
Implementation
Validation
Remaining issues
```

------------------------------------------------------------------------

# 22. Important Project Principle

The project is being developed incrementally.

Do not assume that every issue should be solved with a new architecture.

Prefer:

> Understand → isolate → make the smallest safe change → validate.

The objective is not merely to make the current screen or request work.

The objective is to preserve the integrity of the overall
intraday-analysis workflow.

------------------------------------------------------------------------

# 23. Future Architecture Changes

Some requirements may evolve as the project matures.

Examples include:

-   Local market-data caching
-   Historical Nifty data
-   Live-data fallback
-   Market-hours request guards
-   Improved data persistence
-   Faster analysis
-   Reduced external API calls
-   Better chart responsiveness

When implementing such changes:

1.  First analyze the existing architecture.
2.  Identify the current bottleneck.
3.  Determine whether an incremental change is sufficient.
4.  Avoid prematurely introducing a large architecture.
5.  Preserve backward compatibility where practical.
6.  Validate performance improvements with actual measurements where
    possible.

------------------------------------------------------------------------

# 24. Final Rule

When uncertain:

**Do not guess.**

Inspect the repository, trace the behaviour, explain the uncertainty,
and ask for clarification when the requirement cannot safely be
inferred.

The permanent development philosophy for this repository is:

> **ANALYZE → PLAN → IMPLEMENT → VALIDATE → REPORT**

with:

> **Minimal change + Existing behaviour preserved + Data-driven
> implementation + No unnecessary refactoring**
