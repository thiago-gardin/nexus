from __future__ import annotations

import sqlite3


TABLE_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS domains (
        domain_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        cognitive_purpose TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'draft', 'deprecated')),
        owner_human TEXT,
        owner_agent TEXT,
        source_types_supported TEXT NOT NULL DEFAULT '[]',
        local_entity_types TEXT NOT NULL DEFAULT '[]',
        relation_types TEXT NOT NULL DEFAULT '[]',
        promotion_rules TEXT NOT NULL DEFAULT '[]',
        governance_dependencies TEXT NOT NULL DEFAULT '[]',
        version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS domain_versions (
        domain_version_id TEXT PRIMARY KEY,
        domain_id TEXT NOT NULL,
        version_label TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('draft', 'active', 'inactive', 'deprecated')),
        charter TEXT NOT NULL DEFAULT '{}',
        allowed_entity_types TEXT NOT NULL DEFAULT '[]',
        allowed_relation_types TEXT NOT NULL DEFAULT '[]',
        allowed_payload_types TEXT NOT NULL DEFAULT '[]',
        required_fields TEXT NOT NULL DEFAULT '{}',
        promotion_rules TEXT NOT NULL DEFAULT '[]',
        created_at TEXT NOT NULL,
        activated_at TEXT,
        last_event_id TEXT,
        FOREIGN KEY(domain_id) REFERENCES domains(domain_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sources (
        source_id TEXT PRIMARY KEY,
        domain_id TEXT NOT NULL,
        source_type TEXT NOT NULL,
        source_origin TEXT NOT NULL,
        source_uri TEXT,
        storage_ref TEXT,
        raw_payload_ref TEXT NOT NULL,
        parsed_payload_ref TEXT,
        checksum TEXT NOT NULL,
        ingestion_status TEXT NOT NULL CHECK (ingestion_status IN ('pending', 'parsed', 'failed', 'reprocessed')),
        metadata TEXT NOT NULL DEFAULT '{}',
        provenance_record TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(domain_id) REFERENCES domains(domain_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS entities (
        entity_id TEXT PRIMARY KEY,
        scope TEXT NOT NULL CHECK (scope IN ('local', 'canonical')),
        domain_id TEXT,
        entity_type TEXT NOT NULL,
        label TEXT NOT NULL,
        short_description TEXT,
        attributes TEXT NOT NULL DEFAULT '{}',
        aliases TEXT NOT NULL DEFAULT '[]',
        confidence REAL NOT NULL DEFAULT 0.0,
        validation_status TEXT NOT NULL CHECK (validation_status IN ('proposed', 'validated', 'rejected', 'contested')),
        canonical_candidate_flag INTEGER NOT NULL DEFAULT 0 CHECK (canonical_candidate_flag IN (0, 1)),
        provenance_refs TEXT NOT NULL DEFAULT '[]',
        payload_refs TEXT NOT NULL DEFAULT '[]',
        version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(domain_id) REFERENCES domains(domain_id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS entity_aliases (
        alias_id TEXT PRIMARY KEY,
        entity_id TEXT NOT NULL,
        alias_value TEXT NOT NULL,
        alias_kind TEXT NOT NULL DEFAULT 'alternate',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        version INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY(entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
        UNIQUE(entity_id, alias_value)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS relations (
        relation_id TEXT PRIMARY KEY,
        source_entity_id TEXT NOT NULL,
        target_entity_id TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        directionality TEXT NOT NULL CHECK (directionality IN ('directed', 'undirected')),
        domain_context TEXT,
        evidence_refs TEXT NOT NULL DEFAULT '[]',
        confidence REAL NOT NULL DEFAULT 0.0,
        validation_status TEXT NOT NULL CHECK (validation_status IN ('proposed', 'validated', 'rejected', 'contested')),
        asserted_by TEXT NOT NULL,
        validated_by TEXT,
        version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(source_entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
        FOREIGN KEY(target_entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        target_object_type TEXT NOT NULL CHECK (target_object_type IN ('domain', 'source', 'entity', 'relation', 'decision', 'rule', 'payload', 'projection')),
        target_object_id TEXT NOT NULL,
        performed_by TEXT NOT NULL,
        performed_via TEXT NOT NULL CHECK (performed_via IN ('human_ui', 'agent_local', 'agent_remote', 'system', 'cli', 'api')),
        reason TEXT,
        payload TEXT NOT NULL DEFAULT '{}',
        before_state_ref TEXT,
        after_state_ref TEXT,
        reversible_flag INTEGER NOT NULL DEFAULT 0 CHECK (reversible_flag IN (0, 1)),
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS decisions (
        decision_id TEXT PRIMARY KEY,
        decision_type TEXT NOT NULL CHECK (decision_type IN ('approval', 'rejection', 'override', 'merge', 'split', 'promotion', 'demotion', 'edit_acceptance')),
        proposal_ref TEXT NOT NULL,
        target_refs TEXT NOT NULL DEFAULT '[]',
        proposed_by TEXT NOT NULL,
        decided_by TEXT,
        rationale TEXT,
        decision_state TEXT NOT NULL CHECK (decision_state IN ('pending', 'approved', 'rejected', 'overridden', 'expired')),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS proposals (
        proposal_id TEXT PRIMARY KEY,
        proposal_type TEXT NOT NULL CHECK (proposal_type IN ('entity_update', 'relation_create', 'relation_update', 'merge', 'separation', 'decision_suggestion', 'payload_edit', 'reentry')),
        target_object_type TEXT NOT NULL CHECK (target_object_type IN ('entity', 'relation', 'decision', 'payload', 'projection', 'source')),
        target_object_id TEXT NOT NULL,
        target_refs TEXT NOT NULL DEFAULT '[]',
        proposed_changes TEXT NOT NULL DEFAULT '{}',
        proposed_by TEXT NOT NULL,
        rationale TEXT,
        evidence_refs TEXT NOT NULL DEFAULT '[]',
        proposal_state TEXT NOT NULL CHECK (proposal_state IN ('pending', 'approved', 'rejected', 'expired')),
        decision_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS governance_rules (
        rule_id TEXT PRIMARY KEY,
        rule_type TEXT NOT NULL CHECK (rule_type IN ('identity', 'promotion', 'confidence', 'provenance', 'arbitration', 'validation', 'reentry')),
        name TEXT NOT NULL,
        scope TEXT NOT NULL,
        logic_description TEXT NOT NULL,
        machine_executable_repr TEXT,
        human_readable_repr TEXT NOT NULL,
        applies_to TEXT NOT NULL DEFAULT '[]',
        priority INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'deprecated', 'draft')),
        created_by TEXT NOT NULL,
        approved_by TEXT,
        version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS payloads (
        payload_id TEXT PRIMARY KEY,
        payload_type TEXT NOT NULL CHECK (payload_type IN ('raw_body', 'parsed_body', 'bio', 'description', 'transcript', 'attachment_extract', 'note', 'summary')),
        owner_object_type TEXT NOT NULL CHECK (owner_object_type IN ('source', 'entity', 'relation', 'decision', 'projection')),
        owner_object_id TEXT NOT NULL,
        storage_ref TEXT NOT NULL,
        format TEXT NOT NULL CHECK (format IN ('md', 'txt', 'json', 'html', 'pdf', 'bin')),
        checksum TEXT NOT NULL,
        editability TEXT NOT NULL CHECK (editability IN ('read_only', 'proposable_edit', 'editable_under_rule')),
        canonical_flag INTEGER NOT NULL DEFAULT 0 CHECK (canonical_flag IN (0, 1)),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        version INTEGER NOT NULL DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS projections (
        projection_id TEXT PRIMARY KEY,
        projection_type TEXT NOT NULL CHECK (projection_type IN ('entity_view', 'relation_view', 'decision_view', 'domain_snapshot', 'meeting_context', 'project_state', 'thread_view')),
        source_refs TEXT NOT NULL DEFAULT '[]',
        payload_refs TEXT NOT NULL DEFAULT '[]',
        materialization_format TEXT NOT NULL CHECK (materialization_format IN ('md', 'json', 'yaml')),
        storage_ref TEXT NOT NULL,
        generated_by TEXT NOT NULL,
        generation_scope TEXT NOT NULL CHECK (generation_scope IN ('local', 'remote', 'published')),
        freshness_status TEXT NOT NULL CHECK (freshness_status IN ('fresh', 'stale', 'rebuilding')),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS object_versions (
        version_id TEXT PRIMARY KEY,
        object_type TEXT NOT NULL,
        object_id TEXT NOT NULL,
        version_number INTEGER NOT NULL,
        serialized_state_ref TEXT NOT NULL,
        created_at TEXT NOT NULL,
        created_by TEXT NOT NULL,
        UNIQUE(object_type, object_id, version_number)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ingestion_jobs (
        job_id TEXT PRIMARY KEY,
        job_type TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
        target_ref TEXT NOT NULL,
        started_at TEXT,
        finished_at TEXT,
        logs_ref TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS materialization_jobs (
        job_id TEXT PRIMARY KEY,
        job_type TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
        target_ref TEXT NOT NULL,
        started_at TEXT,
        finished_at TEXT,
        logs_ref TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reentry_jobs (
        job_id TEXT PRIMARY KEY,
        job_type TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
        target_ref TEXT NOT NULL,
        started_at TEXT,
        finished_at TEXT,
        logs_ref TEXT
    )
    """,
]


INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_sources_domain_id ON sources(domain_id)",
    "CREATE INDEX IF NOT EXISTS idx_domain_versions_domain_id ON domain_versions(domain_id)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_domain_versions_active_domain ON domain_versions(domain_id) WHERE status = 'active'",
    "CREATE INDEX IF NOT EXISTS idx_entities_domain_id ON entities(domain_id)",
    "CREATE INDEX IF NOT EXISTS idx_entity_aliases_entity_id ON entity_aliases(entity_id)",
    "CREATE INDEX IF NOT EXISTS idx_relations_source_entity_id ON relations(source_entity_id)",
    "CREATE INDEX IF NOT EXISTS idx_relations_target_entity_id ON relations(target_entity_id)",
    "CREATE INDEX IF NOT EXISTS idx_events_target_object ON events(target_object_type, target_object_id)",
    "CREATE INDEX IF NOT EXISTS idx_events_performed_by ON events(performed_by)",
    "CREATE INDEX IF NOT EXISTS idx_decisions_state ON decisions(decision_state)",
    "CREATE INDEX IF NOT EXISTS idx_decisions_proposal_ref ON decisions(proposal_ref)",
    "CREATE INDEX IF NOT EXISTS idx_proposals_state ON proposals(proposal_state)",
    "CREATE INDEX IF NOT EXISTS idx_governance_rules_scope ON governance_rules(scope)",
    "CREATE INDEX IF NOT EXISTS idx_payloads_owner_object ON payloads(owner_object_type, owner_object_id)",
    "CREATE INDEX IF NOT EXISTS idx_projections_type ON projections(projection_type)",
    "CREATE INDEX IF NOT EXISTS idx_object_versions_object ON object_versions(object_type, object_id)",
]


def apply_migrations(connection: sqlite3.Connection) -> None:
    with connection:
        for statement in TABLE_STATEMENTS:
            connection.execute(statement)
        _migrate_proposals_contract(connection)
        for statement in INDEX_STATEMENTS:
            connection.execute(statement)


def _migrate_proposals_contract(connection: sqlite3.Connection) -> None:
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'proposals'"
    ).fetchone()
    if row is None:
        return
    create_sql = row[0] or ""
    if "payload_edit" in create_sql and "target_object_type IN ('entity', 'relation', 'decision', 'payload', 'projection', 'source')" in create_sql:
        return
    connection.execute("ALTER TABLE proposals RENAME TO proposals_legacy")
    connection.execute(
        """
        CREATE TABLE proposals (
            proposal_id TEXT PRIMARY KEY,
            proposal_type TEXT NOT NULL CHECK (proposal_type IN ('entity_update', 'relation_create', 'relation_update', 'merge', 'separation', 'decision_suggestion', 'payload_edit', 'reentry')),
            target_object_type TEXT NOT NULL CHECK (target_object_type IN ('entity', 'relation', 'decision', 'payload', 'projection', 'source')),
            target_object_id TEXT NOT NULL,
            target_refs TEXT NOT NULL DEFAULT '[]',
            proposed_changes TEXT NOT NULL DEFAULT '{}',
            proposed_by TEXT NOT NULL,
            rationale TEXT,
            evidence_refs TEXT NOT NULL DEFAULT '[]',
            proposal_state TEXT NOT NULL CHECK (proposal_state IN ('pending', 'approved', 'rejected', 'expired')),
            decision_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO proposals (
            proposal_id, proposal_type, target_object_type, target_object_id,
            target_refs, proposed_changes, proposed_by, rationale,
            evidence_refs, proposal_state, decision_id, created_at, updated_at
        )
        SELECT
            proposal_id, proposal_type, target_object_type, target_object_id,
            target_refs, proposed_changes, proposed_by, rationale,
            evidence_refs, proposal_state, decision_id, created_at, updated_at
        FROM proposals_legacy
        """
    )
    connection.execute("DROP TABLE proposals_legacy")
