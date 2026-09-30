Add the following subsection immediately after Rollback Procedure.

## Rollback Checklist

Use this checklist to verify a clean rollback from Angel 4.1 to Angel 4.0.1.

### Preparation

```text
□ Angel 4.1 services stopped
□ Engineering API stopped
□ No active database writes occurring
□ Latest backups available
□ Rollback location verified
```

### Restore Application Files

```text
□ Angel 4.0.1 application directory restored
□ Angel 4.0.1 launchers restored
□ Custom scripts restored
□ Configuration files restored
□ Environment settings restored
```

### Restore Database

```text
□ SQLite database restored from backup
□ Database file integrity verified
□ Database permissions verified
□ Pre-upgrade database version confirmed
```

### Restore Knowledge Assets

```text
□ Knowledge repositories restored
□ Imported documents restored
□ Knowledge Center data verified
□ Custom knowledge packs verified
```

### Service Validation

```text
□ Angel 4.0.1 launches successfully
□ UI loads correctly
□ Conversation history accessible
□ Date/time routing operational
□ Weather routing operational
□ Knowledge Center operational
□ Document import functionality operational
```

### Data Validation

```text
□ Existing conversations visible
□ Historical conversations load correctly
□ Knowledge repositories accessible
□ Knowledge search functioning
□ User settings preserved
□ Custom integrations functioning
```

### Engineering Layer Verification

Because Angel 4.1 introduces new engineering records, verify rollback expectations:

```text
□ Angel 4.1 engineering tables no longer required
□ 4.1 engineering API disabled
□ No dependencies on 4.1 lifecycle records remain
□ Existing 4.0.1 functionality unaffected
```

### Final Acceptance Checklist

```text
□ Application starts cleanly
□ No database errors present
□ No migration errors present
□ No missing file warnings present
□ Core workflows validated
□ User data preserved
□ System ready for production use
```

---

### Rollback Success Criteria

A rollback is considered successful when:

- Angel 4.0.1 starts normally
- Existing conversations are intact
- Knowledge Center functions correctly
- Core routing features operate normally
- No database integrity issues are reported
- No Angel 4.1 engineering dependencies remain active

```text
Rollback Status: PASS
```

If any item above cannot be verified, rollback should be considered incomplete until the issue is resolved.


This gives the release notes a production-style upgrade section with a formal rollback validation process, which is typically expected for a platform introducing new persistence structures and lifecycle records.