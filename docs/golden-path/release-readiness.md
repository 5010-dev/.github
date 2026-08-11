# Golden Path release-readiness checklist

Use this checklist before the repository's real merge, release, promotion, or
deployment boundary. Mark only applicable items and keep evidence in the
repository's normal pull request, release, deployment, or security records. The
checklist is guidance, not a central approval queue.

## Repository contract

- [ ] The applicable standard profiles match real source and native manifests.
- [ ] Exact toolchains, native manifests, locks or integrity records, and
      private-registry boundaries are committed and agree.
- [ ] Root `just init`, `just check`, and `just ci` are truthful; no required
      capability is a successful no-op.
- [ ] Ambiguous native roots are classified without package mappings,
      release-unit inference, or dummy manifests.
- [ ] Every deviation records its exact requirement, scope, risk, owner,
      approval, expiry, and exit condition.

## Validation and review

- [ ] The owning repository's canonical CI prepares locked dependencies and
      runs `just ci` once.
- [ ] Generated output, artifact builds, package checks, supported-runtime
      matrices, and deployment smoke tests run only where the repository's
      declared boundaries require them.
- [ ] The pull request follows the organization contribution policy and the
      repository template.
- [ ] A change to a released or cross-component contract states its real
      compatibility boundary; unreleased intermediates are corrected in place.

## Dependency and security state

- [ ] One automation owner manages each dependency surface; Dependabot and
      Renovate do not overlap.
- [ ] Routine grouping and pull-request limits fit repository review capacity.
- [ ] Security alerts, routing failures, suppressed findings, and unresolved
      security updates remain visible to an accountable owner.
- [ ] Security updates are not delayed, closed, or discarded for routine
      regrouping.
- [ ] A default-branch alert is called closed only after the fixed native lock
      is on the default branch and current alert state confirms closure.

## Release or promotion

- [ ] Repository-owned release units, version intent, source SHA, artifact
      identities, and publication workflow agree where a release exists.
- [ ] Promotion follows the repository's accepted branch model; a green
      development branch is not reported as production.
- [ ] Release, deployment, and post-merge workflows have reached a terminal
      result before their outcome is claimed.
- [ ] The handoff distinguishes local tests, synthetic fixtures, CI, release,
      deployment, and live security evidence.

Completing this list does not prove platform enforcement, production health, or
security closure without the corresponding current source evidence.
