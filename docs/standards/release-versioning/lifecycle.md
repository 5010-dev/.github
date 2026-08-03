# Compatibility lifecycle

Maturity and support are separate dimensions. Every consumer-selectable release
line MUST identify its maturity channel. Stable and Incubating release lines
MUST also identify their support state.

## Maturity channels

| Channel | Contract |
| --- | --- |
| Development/Snapshot | Unstable build for bounded testing; MUST NOT be the preferred stable selection |
| Alpha | Compatibility is not promised; known consumers still receive breaking-change notice |
| Beta | Intended compatibility direction is established; support and retirement expectations are declared before broad consumption |
| RC | Final release candidate; intentional compatibility changes require a new RC and renewed validation |
| Incubating | SemVer `0.x` line with a consumer-selectable but not yet Stable compatibility contract |
| Stable | Declared compatibility surface is protected under the selected version scheme |

Release units MAY skip channels that add no useful validation boundary. Native
ecosystem spelling and ordering take precedence. `dev`, `staging`, and
`production` are environments, not maturity channels.

The default registry channel and mutable `latest` alias MUST select the Stable
release whose support state is Preferred. When a release unit has no Stable
release, the channel or alias MUST instead select the Incubating release whose
support state is Preferred and MUST NOT imply Stable maturity. A prerelease MUST
use a native prerelease version or separate channel. Stable promotion publishes
a new final version; it MUST NOT mutate an existing prerelease, tag, or artifact.

## Support states

```text
Preferred -> Supported -> Deprecated -> EOL
```

- **Preferred** is the default line for new consumers: Stable when available,
  otherwise Incubating.
- **Supported** receives the fixes declared by its repository policy.
- **Deprecated** has a successor or retirement path and remains supported only
  to the stated level until its deadline.
- **EOL** receives no new compatibility or fix guarantee.

A Deprecated line MUST NOT receive new features. It receives only the fixes
declared by its repository support policy until its deadline.

A Stable or Incubating line can be Deprecated while another line is Preferred.
By default, a release unit supports one latest Preferred line: Stable when
available, otherwise Incubating. N-1, LTS, maintenance branches, and backports
are not automatic requirements. A repository supporting multiple lines MUST
record each line's end date, fix and backport scope, and owner. This standard
does not require a roll-forward-only service to create a maintenance branch or
backport policy.

## Incubating `0.x`

A SemVer `0.x` line is Incubating rather than Stable and MUST use the support
state transitions above.

- A compatible fix SHOULD increment patch and a breaking change SHOULD
  increment minor unless the ecosystem defines more specific behavior.
- Known consumers MUST still receive compatibility classification and migration
  guidance.
- A production or independently deployed consumer relying on a stable surface
  SHOULD trigger a `1.0.0` readiness decision.

## Deprecation notice

The default notice period is proportional to consumer reach:

| Consumer reach | Default notice |
| --- | --- |
| Co-deployed or single-owner | No fixed calendar minimum; atomic migration, cutover, and rollback MUST be verified |
| Identifiable internal cross-repository consumers | 90 days `SHOULD` |
| External or unidentified consumers | 180 days `SHOULD` |
| Alpha | No fixed period; known consumers MUST be notified |
| Beta | Consumer-reach period and promotion or retirement target MUST be declared on entry |

A repository shortening an applicable 90- or 180-day default MUST use either a
recorded exception or the emergency-change path below. A recorded exception
MUST identify the affected or reasonably discoverable consumers, reason,
mitigation, approval, review date, and evidence supporting the shorter period.
For external or unidentified consumers, the repository MUST also record its
discovery and notification attempts and the accepted residual risk.

## Stable deprecation contract

Deprecating a stable compatibility surface MUST record:

- the deprecated scope;
- its replacement or successor;
- migration guidance;
- announcement date;
- earliest removal or EOL date;
- support level during the notice period;
- owner; and
- security or integrity emergency conditions.

An announced earliest removal date MUST NOT be moved earlier for routine
reasons. A stable package MUST expose deprecation in at least one compatible
release before breaking removal. An independently consumed stable API major
MUST keep the old and new majors available concurrently during migration. A
co-deployed or single-owner API MAY instead use a verified atomic migration,
cutover, and rollback path under the consumer-reach policy above.

HTTP APIs SHOULD connect canonical documentation and runtime signals using the
standard `Deprecation` and `Sunset` fields when applicable.

## Bad releases and preservation

Lifecycle deprecation and a defective release are different states:

- **Deprecated** is a valid release that consumers should stop selecting.
- **Yanked/Retracted** is a specific defective release excluded from new
  dependency selection while existing locked builds remain reproducible.
- **Deleted** removes availability and is reserved for secrets, malware, legal,
  privacy, or equivalent integrity incidents where preservation is unsafe.

A published version, tag, or artifact identifier MUST NOT be overwritten or
reused for different content, including after deletion. Repositories SHOULD
prefer ecosystem-native deprecate, yank, or retract operations over deletion.
If corrected content remains intended for distribution, it MUST use a new
version or repository-native release identifier. Otherwise, a repository MAY
yank or retract the defective release without publishing a replacement.
Emergency deletion MUST record credential rotation or containment, affected
scope, replacement, required consumer action, owner, and follow-up review.

Database migrations are superseded by later migrations rather than deprecated,
yanked, or deleted. Mutable container aliases do not express support state.

## Emergency change

Security, regulatory, legal, privacy, or integrity emergencies MAY shorten a
notice period or require an immediate breaking change. The owning repository
MUST record the affected scope, reason, replacement, consumer action, owner,
approval, and follow-up review. Emergency authority does not permit artifact
overwrite, identifier reuse, or false compatibility claims.

## Relevant upstream specifications

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Google AIP-181 stability levels](https://google.aip.dev/181)
- [Google AIP-185 API versioning](https://google.aip.dev/185)
- [Go module deprecation and retraction](https://go.dev/ref/mod)
- [Cargo publishing and yank](https://doc.rust-lang.org/cargo/reference/publishing.html)
- [Python package file yanking](https://packaging.python.org/en/latest/specifications/file-yanking/)
- [npm package deprecation](https://docs.npmjs.com/deprecating-and-undeprecating-packages-or-package-versions/)
- [RFC 9745: The Deprecation HTTP response header field](https://www.rfc-editor.org/rfc/rfc9745.html)
- [RFC 8594: The Sunset HTTP header field](https://www.rfc-editor.org/rfc/rfc8594.html)
