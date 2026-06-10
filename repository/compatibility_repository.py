from sqlalchemy import select, or_, and_
from model.compatibility import Compatibility, CompatibilityRule


# GET ALL RULES
def get_all_rules(session):
    return session.execute(select(CompatibilityRule)).scalars().all()


# GET RULE BY ID
def get_rule_by_id(session, rule_id):
    return session.get(CompatibilityRule, rule_id)


# CREATE RULE
def create_rule(session, rule):
    session.add(rule)
    session.commit()
    return rule


# DELETE RULE
def delete_rule_by_id(session, rule):
    session.delete(rule)
    session.commit()


# GET ALL
def get_all(session):
    return session.execute(select(Compatibility)).scalars().all()


# GET BY ID
def get_by_id(session, compatibility_id):
    return session.get(Compatibility, compatibility_id)


# GET BETWEEN: cerca una regola tra due optional in qualsiasi ordine
def get_between(session, opt_a, opt_b):
    return session.execute(
        select(Compatibility).where(
            or_(
                and_(Compatibility.optional_id == opt_a, Compatibility.optional_with_id == opt_b),
                and_(Compatibility.optional_id == opt_b, Compatibility.optional_with_id == opt_a),
            )
        )
    ).scalars().first()


# GET BY OPTIONAL: tutte le regole che coinvolgono un dato optional
def get_by_optional(session, optional_id):
    return session.execute(
        select(Compatibility).where(
            or_(
                Compatibility.optional_id == optional_id,
                Compatibility.optional_with_id == optional_id,
            )
        )
    ).scalars().all()


# CREATE
def create(session, compatibility):
    session.add(compatibility)
    session.commit()
    return compatibility


# DELETE
def delete_by_id(session, compatibility):
    session.delete(compatibility)
    session.commit()