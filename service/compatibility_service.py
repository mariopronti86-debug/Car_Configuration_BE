from model.compatibility import Compatibility, CompatibilityRule
from repository import compatibility_repository, optional_repository


# ── GET ALL RULES
def get_all_rules(session):
    return compatibility_repository.get_all_rules(session)


# ── CREATE RULE
def create_rule(session, data):

    if data.get("rule_type") not in ["incompatible", "requires"]:
        raise ValueError("rule_type deve essere 'incompatible' o 'requires'!")

    nuova_rule = CompatibilityRule(rule_type=data["rule_type"])
    return compatibility_repository.create_rule(session, nuova_rule)


# ── DELETE RULE
def delete_rule(session, rule_id):
    rule = compatibility_repository.get_rule_by_id(session, rule_id)

    if rule is None:
        raise ValueError(f"Regola con id={rule_id} non trovata!")

    compatibility_repository.delete_rule_by_id(session, rule)


# ── GET ALL
def get_all(session):
    return compatibility_repository.get_all(session)


# ── CREATE
def create(session, data):

    if not data.get("optional_id") or not data.get("optional_with_id") or not data.get("rule_id"):
        raise ValueError("Tutti i campi sono obbligatori!")

    opt_a = optional_repository.get_by_id(session, int(data["optional_id"]))
    opt_b = optional_repository.get_by_id(session, int(data["optional_with_id"]))
    rule  = compatibility_repository.get_rule_by_id(session, int(data["rule_id"]))

    if opt_a is None or opt_b is None:
        raise ValueError("Uno degli optional non esiste!")

    if rule is None:
        raise ValueError(f"Regola con id={data['rule_id']} non trovata!")

    if opt_a.optional_id == opt_b.optional_id:
        raise ValueError("I due optional non possono essere uguali!")

    if compatibility_repository.get_between(session, opt_a.optional_id, opt_b.optional_id) is not None:
        raise ValueError("Esiste già una regola tra questi due optional!")

    nuova_comp = Compatibility(
        optional_id=opt_a.optional_id,
        optional_with_id=opt_b.optional_id,
        rule_id=rule.rule_id,
    )

    return compatibility_repository.create(session, nuova_comp)


# ── DELETE
def delete(session, compatibility_id):
    comp = compatibility_repository.get_by_id(session, compatibility_id)

    if comp is None:
        raise ValueError(f"Compatibility con id={compatibility_id} non trovata!")

    compatibility_repository.delete_by_id(session, comp)


# ── CHECK LISTA OPTIONAL
# Ritorna lista di violazioni trovate (lista vuota = nessun problema)
def check_optional_list(session, optional_ids):
    violazioni = []

    # Controlla incompatibilità tra ogni coppia
    for i in range(len(optional_ids)):
        for j in range(i + 1, len(optional_ids)):
            comp = compatibility_repository.get_between(session, optional_ids[i], optional_ids[j])
            if comp is not None and comp.rule.rule_type == "incompatible":
                violazioni.append(f"Optional {optional_ids[i]} e Optional {optional_ids[j]} sono incompatibili!")

    # Controlla requires: se A richiede B, B deve essere nella lista
    for opt_id in optional_ids:
        for comp in compatibility_repository.get_by_optional(session, opt_id):
            if comp.rule.rule_type == "requires":
                altro_id = comp.optional_with_id if comp.optional_id == opt_id else comp.optional_id
                if altro_id not in optional_ids:
                    violazioni.append(f"Optional {opt_id} richiede anche l'Optional {altro_id}!")

    return violazioni