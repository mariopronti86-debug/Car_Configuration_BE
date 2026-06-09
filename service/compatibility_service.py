from model.compatibility import Compatibility, CompatibilityRule
from repository import compatibility_repository, optional_repository


# ── GET ALL RULES 
def get_all_rules(session):
    return compatibility_repository.get_all_rules(session)


# ── CREATE RULE 
def create_rule(session, data):

    if "rule_type" not in data or not data["rule_type"].strip():
        raise ValueError("Campo 'rule_type' obbligatorio!")

    rule_types_validi = ["incompatible", "requires"]
    if data["rule_type"] not in rule_types_validi:
        raise ValueError(f"rule_type deve essere uno di: {rule_types_validi}")

    nuova_rule = CompatibilityRule(rule_type=data["rule_type"])

    return compatibility_repository.create_rule(session, nuova_rule)


# ── DELETE RULE 
def delete_rule(session, rule_id):
    rule = compatibility_repository.get_rule_by_id(session, rule_id)

    if rule is None:
        raise ValueError(f"Regola con id={rule_id} non trovata!")

    compatibility_repository.delete_rule_by_id(session, rule)


# ── GET ALL COMPATIBILITIES 
def get_all(session):
    return compatibility_repository.get_all(session)


# ── CREATE COMPATIBILITY 
def create(session, data):

    for campo in ["optional_id", "optional_with_id", "rule_id"]:
        if campo not in data:
            raise ValueError(f"Campo '{campo}' obbligatorio!")

    opt_a = optional_repository.get_by_id(session, int(data["optional_id"]))
    opt_b = optional_repository.get_by_id(session, int(data["optional_with_id"]))
    rule  = compatibility_repository.get_rule_by_id(session, int(data["rule_id"]))

    if opt_a is None:
        raise ValueError(f"Optional con id={data['optional_id']} non trovato!")
    if opt_b is None:
        raise ValueError(f"Optional con id={data['optional_with_id']} non trovato!")
    if rule is None:
        raise ValueError(f"Regola con id={data['rule_id']} non trovata!")

    if opt_a.optional_id == opt_b.optional_id:
        raise ValueError("I due optional non possono essere uguali!")

    # Controllo se esiste già una regola tra questi due optional
    esistente = compatibility_repository.get_between(session, opt_a.optional_id, opt_b.optional_id)
    if esistente is not None:
        raise ValueError("Esiste già una regola di compatibilità tra questi due optional!")

    nuova_comp = Compatibility(
        optional_id=opt_a.optional_id,
        optional_with_id=opt_b.optional_id,
        rule_id=rule.rule_id,
    )

    return compatibility_repository.create(session, nuova_comp)


# ── DELETE COMPATIBILITY 
def delete(session, compatibility_id):
    comp = compatibility_repository.get_by_id(session, compatibility_id) if hasattr(compatibility_repository, "get_by_id") else None

    # Recupero diretto dalla sessione se non c'è un metodo dedicato
    from model.compatibility import Compatibility as CompModel
    comp = session.get(CompModel, compatibility_id)

    if comp is None:
        raise ValueError(f"Compatibility con id={compatibility_id} non trovata!")

    compatibility_repository.delete_by_id(session, comp)


# ── CHECK OPTIONAL LIST 
def check_optional_list(session, optional_ids):
    """
    Verifica che la lista di optional selezionati non violi le regole di compatibilità.
    Ritorna una lista di violazioni trovate (lista vuota = tutto ok).
    Ogni violazione è un dict: { optional_id_a, optional_id_b, rule_type, message }
    """
    violazioni = []

    # Controlla incompatibilità: ogni coppia di optional selezionati
    for i in range(len(optional_ids)):
        for j in range(i + 1, len(optional_ids)):
            comp = compatibility_repository.get_between(session, optional_ids[i], optional_ids[j])
            if comp is not None and comp.rule.rule_type == "incompatible":
                violazioni.append({
                    "optional_id_a": optional_ids[i],
                    "optional_id_b": optional_ids[j],
                    "rule_type":     comp.rule.rule_type,
                    "message":       f"Optional {optional_ids[i]} e Optional {optional_ids[j]} sono incompatibili!",
                })

    # Controlla requires: se A richiede B, B deve essere nella lista
    for opt_id in optional_ids:
        entries = compatibility_repository.get_by_optional(session, opt_id)
        for entry in entries:
            if entry.rule.rule_type == "requires":
                altro_id = entry.optional_with_id if entry.optional_id == opt_id else entry.optional_id
                if altro_id not in optional_ids:
                    violazioni.append({
                        "optional_id_a": opt_id,
                        "optional_id_b": altro_id,
                        "rule_type":     "requires",
                        "message":       f"Optional {opt_id} richiede anche l'Optional {altro_id}!",
                    })

    return violazioni