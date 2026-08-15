from dataclasses import dataclass


@dataclass
class Workload:
    name: str
    description: str
    query: str
    parameters: dict


WORKLOADS = [
    Workload("wikivote_point_lookup", "Point lookup of a WikiUser by ID", "FOR u IN wikivote_users FILTER u._key == @user_id RETURN u", {"user_id": 3}),
    Workload("wikivote_indexed_lookup", "Indexed lookup of WikiUser by id property", "FOR u IN wikivote_users FILTER u.id == @user_id RETURN u", {"user_id": 3}),
    Workload("wikivote_one_hop", "One-hop outgoing vote traversal", "FOR v IN 1..1 OUTBOUND CONCAT('wikivote_users/', @user_id) wikivote_votes RETURN v._key LIMIT 50", {"user_id": 3}),
    Workload("wikivote_two_hop", "Two-hop vote traversal", "FOR v IN 2..2 OUTBOUND CONCAT('wikivote_users/', @user_id) wikivote_votes FILTER v._key != @user_id RETURN DISTINCT v._key LIMIT 50", {"user_id": 3}),
    Workload("wikivote_three_hop", "Three-hop vote traversal", "FOR v IN 3..3 OUTBOUND CONCAT('wikivote_users/', @user_id) wikivote_votes FILTER v._key != @user_id RETURN DISTINCT v._key LIMIT 50", {"user_id": 3}),
    Workload("wikivote_outgoing_count", "Count outgoing votes from a user", "RETURN {user_id: @user_id, vote_count: LENGTH(FOR v IN 1..1 OUTBOUND CONCAT('wikivote_users/', @user_id) wikivote_votes RETURN 1)}", {"user_id": 3}),
    Workload("wikivote_incoming_count", "Count incoming votes to a user", "RETURN {user_id: @user_id, vote_count: LENGTH(FOR v IN 1..1 INBOUND CONCAT('wikivote_users/', @user_id) wikivote_votes RETURN 1)}", {"user_id": 3}),
    Workload("wikivote_high_degree", "Find users with high outgoing vote degree", "FOR u IN wikivote_users LET degree = LENGTH(FOR v IN 1..1 OUTBOUND u wikivote_votes RETURN 1) SORT degree DESC LIMIT 20 RETURN {id: u._key, degree}", {}),
    Workload("wikivote_global_count", "Count all Wiki-Vote relationships", "RETURN LENGTH(wikivote_votes)", {}),
]
