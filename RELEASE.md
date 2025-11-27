# Pozi-0reliance-Lab Release Process

## Release Checklist

- [x] All documentation updated to reference 0Reliance/Pozi-0reliance-Lab
- [x] All tests pass locally and in CI
- [x] Site builds successfully with `mkdocs build`
- [x] Docker Compose deployment verified
- [x] GitHub Actions CI and deploy workflows present
- [x] No exposed secrets or tokens in repo
- [x] Branch protection enabled on `main`
- [x] Release notes and changelog written
- [x] Tag release (e.g., `v1.0.0-beta`)
- [x] GitHub Pages enabled and site published

## Release Steps

1. Merge all changes to `main`.
2. Run CI and ensure all checks pass.
3. Tag the release:
   ```bash
   git tag v1.0.0-beta
   git push origin v1.0.0-beta
   ```
4. Draft release notes in GitHub Releases.
5. Verify site at https://0Reliance.github.io/Pozi-0reliance-Lab/
6. Announce release to team/community.

## Changelog Template

### v1.0.0-beta (2025-11-27)
- Initial public beta release
- All documentation and automation updated for 0Reliance
- CI and deploy workflows added
- Security and installation docs reviewed
- Docker Compose and AI backend validated
