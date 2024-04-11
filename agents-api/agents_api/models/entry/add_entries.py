import pandas as pd

from ...clients.cozo import client
from ...common.protocol.entries import Entry
from ...common.utils import json
from ...common.utils.datetime import utcnow


def add_entries_query(entries: list[Entry]) -> pd.DataFrame:
    entries_lst = []
    for e in entries:
        ts = utcnow().timestamp()
        source = json.dumps(e.source)
        role = json.dumps(e.role)
        name = json.dumps(e.name)
        content: str = (
            e.content if isinstance(e.content, str) else json.dumps(e.content)
        )
        tokenizer = json.dumps(e.tokenizer)
        if e.content:
            entries_lst.append(
                f'[to_uuid("{e.id}"), to_uuid("{e.session_id}"), {source}, {role}, {name}, __"{content}"__, {e.token_count}, {tokenizer}, {ts}, {ts}]'
            )

    if not len(entries_lst):
        return "?[] <- [[]]"

    entries_query = ",\n".join(entries_lst)

    query = f"""
    {{
        ?[entry_id, session_id, source, role, name, content, token_count, tokenizer, created_at, timestamp] <- [
            {entries_query}
        ]

        :insert entries {{
            entry_id,
            session_id,
            source,
            role,
            name, =>
            content,
            token_count,
            tokenizer,
            created_at,
            timestamp,
        }}
        :returning
    }}
    """

    return client.run(query)
