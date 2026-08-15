from dataclasses import dataclass


@dataclass
class Workload:
    name: str
    description: str
    query: str
    parameters: dict


WORKLOADS = [

    Workload(
        name="wikivote_point_lookup",
        description="Point lookup of a WikiUser by ID",
        query="""
        MATCH (u:WikiUser {id: $user_id})
        RETURN u.id
        """,
        parameters={
            "user_id": 3,
        },
    ),

    Workload(
        name="wikivote_indexed_lookup",
        description="Indexed lookup of a WikiUser by ID",
        query="""
        MATCH (u:WikiUser)
        WHERE u.id = $user_id
        RETURN u.id
        """,
        parameters={
            "user_id": 3,
        },
    ),

    Workload(
        name="wikivote_one_hop",
        description="One-hop outgoing vote traversal",
        query="""
        MATCH (u:WikiUser {id: $user_id})
              -[:VOTES]->
              (v:WikiUser)
        RETURN v.id
        LIMIT 50
        """,
        parameters={
            "user_id": 3,
        },
    ),

    Workload(
        name="wikivote_two_hop",
        description="Two-hop vote traversal",
        query="""
        MATCH (u:WikiUser {id: $user_id})
              -[:VOTES]->
              (v:WikiUser)
              -[:VOTES]->
              (w:WikiUser)
        WHERE w.id <> $user_id
        RETURN DISTINCT w.id
        LIMIT 50
        """,
        parameters={
            "user_id": 3,
        },
    ),

    Workload(
        name="wikivote_three_hop",
        description="Three-hop vote traversal",
        query="""
        MATCH (u:WikiUser {id: $user_id})
              -[:VOTES]->
              (v:WikiUser)
              -[:VOTES]->
              (w:WikiUser)
              -[:VOTES]->
              (x:WikiUser)
        WHERE x.id <> $user_id
        RETURN DISTINCT x.id
        LIMIT 50
        """,
        parameters={
            "user_id": 3,
        },
    ),

    Workload(
        name="wikivote_outgoing_count",
        description="Count outgoing votes from a user",
        query="""
        MATCH (u:WikiUser {id: $user_id})
              -[:VOTES]->
              (v:WikiUser)
        RETURN u.id, count(v) AS vote_count
        """,
        parameters={
            "user_id": 3,
        },
    ),

    Workload(
        name="wikivote_incoming_count",
        description="Count incoming votes to a user",
        query="""
        MATCH (u:WikiUser {id: $user_id})
              <-[:VOTES]-
              (v:WikiUser)
        RETURN u.id, count(v) AS vote_count
        """,
        parameters={
            "user_id": 3,
        },
    ),

    Workload(
        name="wikivote_high_degree",
        description="Find users with high outgoing vote degree",
        query="""
        MATCH (u:WikiUser)-[:VOTES]->(v:WikiUser)
        WITH u, count(v) AS degree
        RETURN u.id, degree
        ORDER BY degree DESC
        LIMIT 20
        """,
        parameters={},
    ),

    Workload(
        name="wikivote_global_count",
        description="Count all Wiki-Vote relationships",
        query="""
        MATCH ()-[r:VOTES]->()
        RETURN count(r) AS total_votes
        """,
        parameters={},
    ),

]