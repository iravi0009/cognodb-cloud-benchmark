from dataclasses import dataclass
from typing import Callable


@dataclass
class Workload:
    name: str
    description: str
    query: str
    parameters: dict


WORKLOADS = [

    Workload(
        name="person_lookup",
        description="Lookup a person by ID",
        query="""
        MATCH (p:Person {id: $person_id})
        RETURN p.id, p.name, p.city, p.role
        """,
        parameters={
            "person_id": "P000001",
        },
    ),

    Workload(
        name="company_lookup",
        description="Lookup a company by ID",
        query="""
        MATCH (c:Company {id: $company_id})
        RETURN c.id, c.name, c.industry, c.size
        """,
        parameters={
            "company_id": "C000001",
        },
    ),

    Workload(
        name="technology_lookup",
        description="Lookup a technology by ID",
        query="""
        MATCH (t:Technology {id: $technology_id})
        RETURN t.id, t.name, t.category
        """,
        parameters={
            "technology_id": "T000001",
        },
    ),

    Workload(
        name="person_company",
        description="Find the company where a person works",
        query="""
        MATCH (p:Person {id: $person_id})
              -[:WORKS_AT]->
              (c:Company)
        RETURN p.id, p.name, c.id, c.name
        """,
        parameters={
            "person_id": "P000001",
        },
    ),

    Workload(
        name="person_connections",
        description="Find people directly connected to a person",
        query="""
        MATCH (p:Person {id: $person_id})
              -[:KNOWS]-
              (other:Person)
        RETURN other.id, other.name, other.role
        LIMIT 20
        """,
        parameters={
            "person_id": "P000001",
        },
    ),

    Workload(
        name="person_technologies",
        description="Find technologies used by a person",
        query="""
        MATCH (p:Person {id: $person_id})
              -[:USES]->
              (t:Technology)
        RETURN t.id, t.name, t.category
        ORDER BY t.name
        """,
        parameters={
            "person_id": "P000001",
        },
    ),

    Workload(
        name="company_technologies",
        description="Find technologies used by a company",
        query="""
        MATCH (c:Company {id: $company_id})
              -[:USES]->
              (t:Technology)
        RETURN t.id, t.name, t.category
        ORDER BY t.name
        """,
        parameters={
            "company_id": "C000001",
        },
    ),

    Workload(
        name="two_hop_network",
        description="Two-hop KNOWS traversal",
        query="""
        MATCH (p:Person {id: $person_id})
              -[:KNOWS]-
              (friend:Person)
              -[:KNOWS]-
              (friend_of_friend:Person)
        WHERE friend_of_friend.id <> $person_id
        RETURN DISTINCT
            friend_of_friend.id,
            friend_of_friend.name
        LIMIT 50
        """,
        parameters={
            "person_id": "P000001",
        },
    ),

    Workload(
        name="technology_users",
        description="Find people using a technology",
        query="""
        MATCH (p:Person)-[:USES]->(t:Technology)
        WHERE t.id = $technology_id
        RETURN p.id, p.name, p.role
        LIMIT 50
        """,
        parameters={
            "technology_id": "T000001",
        },
    ),

    Workload(
        name="company_employee_count",
        description="Count employees of a company",
        query="""
        MATCH (c:Company {id: $company_id})
              <-[:WORKS_AT]-
              (p:Person)
        RETURN c.id, c.name, count(p) AS employee_count
        """,
        parameters={
            "company_id": "C000001",
        },
    ),
]