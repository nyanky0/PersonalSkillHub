#!/usr/bin/env python3
"""Regenerate references/*.md for the sertica-web-api skill from the captured OpenAPI spec.

Usage: python build_references.py [path/to/swagger.json|.gz]   (default: ../assets/sertica-swagger.json.gz)
"""
from __future__ import annotations

import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SPEC_DEFAULT = SKILL / "assets" / "sertica-swagger.json.gz"
REF = SKILL / "references"
METHODS = ("get", "post", "put", "patch", "delete")
BASE = "https://indobaruna-test.sertica.com/api"

DOMAINS = [
    ("01", "platform-auth-users", "Platform: auth, users, rights, options, settings", [
        "Auth", "Users", "UserGroups", "UserRights", "CombinedUserRoles", "Roles", "UserSettings",
        "License", "Log", "Embarkations", "LocalizationLanguages", "LocalizationTexts", "MailAccounts",
        "Reminders", "ExternalCalendars", "ScreenLayouts", "GridLayouts", "GridColumnLayouts",
        "AvailableGridLayouts", "Options", "OptionsGlobals", "OptionsOffices",
        "OptionsDynamicReportTemplates", "OptionsOfficeDynamicReportTemplates",
        "OptionsOfficeLabelTemplates", "Counters", "CounterTypes", "ValueLists", "StandardTexts"]),
    ("02", "integrations-automation", "Integrations, automation and master-data tooling", [
        "Webhooks", "ScheduledTasks", "DataTransactions", "TransactionQueue", "IosDataSync", "Device",
        "AiClient", "VrsApiConfigurations", "VrsApiScripts", "MasterDataManagement",
        "MasterDataManagementTasks", "MasterDataManagementTreeStructure",
        "MasterDataManagementUnitTreeStructure", "MDMUnit", "MasterUnit", "ExcelImport",
        "TreeStructure", "ApprovalSetups", "ApprovalWebExcludedUnits", "FinancialFollowupNodeResponses",
        "Receivers", "RejectReasons", "PostponementReasons", "ActivityGroups"]),
    ("03", "procurement-purchase", "Procurement: requisitions, RFQ, purchase orders, invoices, budgets", [
        "PurchaseOrders", "PurchaseOrderPositions", "PurchaseOrderApprovals",
        "PurchaseOrderDeliveryCosts", "CalculatePurchaseOrder", "PurchaseTypes", "PurchaseGroups",
        "RequestForQuotes", "Requisitions", "RequisitionPositions", "Shipments", "UnitShipments",
        "ImInvoices", "InvoiceDocuments", "Budgets", "BudgetAccrualExports", "Carriers",
        "DeliveryConditions", "DeliveryCosts", "PaymentConditions", "ShipmentWays", "Destinations",
        "PackingUnits", "Priorities"]),
    ("04", "jobs-maintenance", "Jobs, job requests, inspections, maintenance history", [
        "Jobs", "JobHistories", "JobHistoryDataEntries", "JobHistoryDataEntryDocuments", "JobGroups",
        "JobRequests", "JobRequestTemplates", "JobRequestMailTemplates", "JobRequestTemplateLogos",
        "JobRecommendations", "JobSequences", "JobTemplates", "JobResponsibles", "JobListWebSearch",
        "AvailableJobListWebSearch", "JobMailTemplates", "ExpectedFaults", "SuggestedActions",
        "InspectionJobs", "InspectionJobHistories", "InspectionLists", "InspectionAreas",
        "InspectionListTypes"]),
    ("05", "components", "Components (machinery/equipment instances) and their structure", [
        "Components", "ComponentPhotos", "ComponentMaps", "ComponentLocations", "ComponentTypes"]),
    ("06", "items-inventory", "Items, warehouses, stock and item trees", [
        "Items", "ItemPhotos", "ItemGroups", "ItemTypes", "ItemLocations", "ItemLocationTree",
        "ItemTree", "ItemWarehouses", "ItemWarehouseHistories", "Warehouses", "ExternalItems",
        "ItemGroupSelection", "ItemGroupSelectionTree"]),
    ("07", "fleet-equipment-tanks", "Fleet equipment, tanks, seals, measurements, liquids", [
        "Equipments", "Tanks", "TankOperationConfigurations", "Purifiers", "Seals", "SealTypes",
        "SealStorageLocations", "SubSealPoints", "SubSealPointComponentTypes", "EnvironmentalItems",
        "MeasuringUnits", "MeasurementTypes", "MeasurementLocations", "Measurements", "Soundings",
        "SoundingTables", "SoundingStatuses", "SoundingTableDocuments", "LiquidTypes", "LubeOilTypes",
        "FuelTypes", "Substances"]),
    ("08", "documents-forms", "Document management, forms and form templates", [
        "Documents", "DocumentClasses", "DocumentGroups", "DocumentTypes", "DocumentMailTemplates",
        "DocumentTransactions", "DocumentTree", "DocumentWeblinks", "Forms", "FormTemplates",
        "FormTemplateDocuments", "FormTemplateHelpImageDocuments", "FormTemplateTables",
        "FormDocuments", "FormBrowser", "FormsSignature", "ControlledCopies",
        "ControlledCopyRevisionDocuments"]),
    ("09", "management-system-qms", "Management system (QMS): documents, change requests, evaluations", [
        "ManagementSystems", "ManagementSystemSections", "ManagementSystemDocuments",
        "ManagementSystemDocumentDocuments", "ManagementSystemChangeRequests", "ManagementSystemROCs",
        "ManagementSystemApprovedPlanDocuments", "ManagementSystemTemplateDocuments",
        "ManagementSystemPublish", "ManagementSystemBrowser",
        "ManagementSystemDocumentAcknowledgements", "EvaluationQuestions", "EvaluationAnswers",
        "EvaluationQuestionObjectLinks", "ChangeRequestCriticalities", "ChangeRequestSources",
        "ChangeRequestDocuments", "Sections", "Procedures"]),
    ("10", "vessel-reports", "Vessel reports, report types, logbook and voyage reporting", [
        "VesselReports", "VesselReportTypes", "VesselReportTypeGroups", "VesselReportTables",
        "VesselReportSequences", "VesselReportSequenceInstances", "VesselReportSignature",
        "VesselReportScripts", "VesselReportBrowser", "VesselReportFieldListTemplates",
        "VesselReportFieldListTemplateRevisionCaches", "VesselReportTableRevisionCaches",
        "VesselReportTypeRevisionCaches", "VesselReportTypeFieldDefinitions", "VoyageReports",
        "LogbookEvents", "LogbookDocuments", "ElectronicLogbook"]),
    ("11", "elogbooks-operations", "Electronic logbooks: ORB, BRB, GRB, ODSRB operations", [
        "OrbOperations", "OrbNoons", "BrbOperations", "BrbReceivers", "GrbOperations",
        "GarbageReceivers", "OdsrbOperations", "OdsrbReceivers", "EventReports",
        "OperationTypeConfigurations"]),
    ("12", "certificates-compliance", "Certificates, compliance registries, fleets and ports", [
        "Certificates", "CertificateDocuments", "CertificateGroups", "CertificateGroupRules",
        "CertificateLocations", "CertificateNotificationSettings", "CertificateTree", "ClassSocieties",
        "ClassCodes", "Flags", "Ports", "CountryCodes"]),
    ("13", "analytics-dashboards", "Analytics, reports, data warehouse and web dashboards", [
        "Analytics", "AnalyticsCustomMenus", "AnalyticsCustomTemplates", "AnalyticsExcelTemplates",
        "AnalyticsReports", "AnalyticsResources", "AnalyticsSubscriptions",
        "AnalyticsTemplateUserRights", "AnalyticsUserMenus", "DataWarehouseAnalyticsTemplates",
        "DataWarehouseConnections", "WebDashboards", "WebDashboardPages", "WebDashboardContent",
        "WebDashboardPageBackgrounds", "WebTaskListConfigurations"]),
    ("14", "master-data-reference", "Reference/master data: units, companies, accounts, codes", [
        "Units", "UnitGroups", "UnitCompanies", "Companies", "Addresses", "AddressCategories",
        "AddressClassifications", "Currencies", "VAT", "AccountingDimensions",
        "AccountingDimensionsCache", "TechnicalAccounts", "Accounts", "PostingPeriods", "Departments",
        "FunctionAreas", "Resources", "Projects", "GroupCodes", "VesselTypes",
        "CommunicationLanguages"]),
]

TD_PAIR = re.compile(r">([^<>]{1,60})</td>\s*<td[^>]*>([^<>]{1,60})</td>")
INTERNAL = re.compile(r"^(Logimatic|Logihold\.BusinessObjects\.LogiholdObjModel\.(Search|View)|System\.)")


def load_spec(path: Path) -> dict:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    return json.loads(path.read_text(encoding="utf-8"))


def clean(text: str) -> str:
    return " ".join((text or "").split())


def rights_of(op: dict) -> str:
    desc = (op.get("responses", {}).get("403", {}) or {}).get("description", "") or ""
    pairs = [f"{k}:{v}" for k, v in TD_PAIR.findall(desc)]
    seen, out = set(), []
    for p in pairs:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return ", ".join(out[:3]) + (f" +{len(out) - 3}" if len(out) > 3 else "")


def short_model(node) -> str:
    """Shorten a schema $ref / array-of-ref into a display name."""
    if not isinstance(node, dict):
        return ""
    if "$ref" in node:
        name = node["$ref"].rsplit("/", 1)[-1]
    elif node.get("type") == "array":
        inner = short_model(node.get("items", {}))
        return f"{inner}[]" if inner else ""
    else:
        return node.get("type", "")
    name = re.sub(r"`\d+\[\[.*", "", name)
    parts = name.split(".")
    if parts and parts[0] == "SerticaWebApi":
        parts = parts[1:]
    if parts and parts[0] == "Models":
        parts = parts[1:]
    if len(parts) >= 2 and parts[-1] == parts[-2]:
        parts = parts[-1:]
    return ".".join(parts) or name


def body_model(op: dict) -> str:
    try:
        return short_model(op["requestBody"]["content"]["application/json"]["schema"])
    except Exception:
        return ""


def resp_model(op: dict) -> str:
    r = op.get("responses", {})
    for code in ("200", "201"):
        try:
            return short_model(r[code]["content"]["application/json"]["schema"])
        except Exception:
            continue
    return ""


def collect(spec: dict):
    ops = []
    for path, item in spec["paths"].items():
        for method, op in item.items():
            if method not in METHODS:
                continue
            ops.append({
                "method": method.upper(),
                "path": path,
                "tag": (op.get("tags") or ["(untagged)"])[0],
                "summary": clean(op.get("summary")),
                "body": body_model(op),
                "resp": resp_model(op),
                "rights": rights_of(op),
                "params": [(p.get("in"), p.get("name"), p.get("required", False)) for p in op.get("parameters", [])],
                "codes": sorted(op.get("responses", {}).keys()),
            })
    return ops


def write_domain_files(ops, header_note):
    by_tag = defaultdict(list)
    for o in ops:
        by_tag[o["tag"]].append(o)
    used = set()
    for num, slug, title, tags in DOMAINS:
        present = [t for t in tags if t in by_tag]
        used.update(present)
        missing = [t for t in tags if t not in by_tag]
        n = sum(len(by_tag[t]) for t in present)
        lines = [f"# {title}", "", header_note, "",
                 f"Domain tags: {', '.join(tags)}", "",
                 f"Operations in this file: **{n}**", ""]
        for t in present:
            lines += [f"## {t} ({len(by_tag[t])} ops)", "",
                      "| Method | Path | Summary | Body | Rights |",
                      "|---|---|---|---|---|"]
            for o in sorted(by_tag[t], key=lambda x: (x["path"], x["method"])):
                lines.append(f"| {o['method']} | `{o['path']}` | {o['summary']} | {o['body']} | {o['rights']} |")
            lines.append("")
        if missing:
            lines += [f"Tags declared in this domain but absent from the captured spec: {', '.join(missing)}", ""]
        (REF / f"endpoints-{num}-{slug}.md").write_text("\n".join(lines), encoding="utf-8")
    leftover = sorted(set(by_tag) - used)
    if leftover:
        lines = ["# Uncategorised module tags", "", header_note, "",
                 "These tags exist in the spec but were not assigned to a domain file (add them to `DOMAINS` in `scripts/build_references.py`).", ""]
        for t in leftover:
            lines += [f"## {t} ({len(by_tag[t])} ops)", "",
                      "| Method | Path | Summary | Body | Rights |", "|---|---|---|---|---|"]
            for o in sorted(by_tag[t], key=lambda x: (x["path"], x["method"])):
                lines.append(f"| {o['method']} | `{o['path']}` | {o['summary']} | {o['body']} | {o['rights']} |")
            lines.append("")
        (REF / "endpoints-99-uncategorised.md").write_text("\n".join(lines), encoding="utf-8")
    return sorted(by_tag), leftover


def write_index(ops, header_note):
    lines = ["# All SERTICA Web API operations (flat index)", "", header_note, "",
             f"{len(ops)} operations. Sorted by path — grep this file by path, module or verb.", "",
             "| Method | Path | Module tag | Summary | Body |", "|---|---|---|---|---|"]
    for o in sorted(ops, key=lambda x: (x["path"], x["method"])):
        lines.append(f"| {o['method']} | `{o['path']}` | {o['tag']} | {o['summary']} | {o['body']} |")
    (REF / "endpoint-index.md").write_text("\n".join(lines), encoding="utf-8")


def write_models(spec, ops, header_note):
    schemas = spec["components"]["schemas"]
    usage = Counter()
    for o in ops:
        for key in ("body", "resp"):
            name = o[key].replace("[]", "")
            if name:
                usage[name] += 1

    def full_name(short: str):
        for k in schemas:
            if k == short or k.endswith("." + short):
                return k
        return None

    # --- models-index.md -------------------------------------------------
    lines = ["# SERTICA schema index (1,104 schemas)", "", header_note, "",
             "`shortName` is how the model appears in `core-models.md` and in `scripts/sertica_api.py model <shortName>`.",
             "Enums list their allowed string values — SERTICA sends enums as strings.", "",
             "## Models used by request bodies / responses", "",
             "| Model | Kind | Fields | Body+response uses |", "|---|---|---|---|"]
    rows, enum_rows = [], []
    for name in sorted(schemas):
        s = schemas[name]
        nprops = len(s.get("properties", {}) or {})
        if "enum" in s:
            enum_rows.append((name, nprops, s["enum"]))
            continue
        if INTERNAL.match(name) and not name.startswith("SerticaWebApi"):
            continue
        short = short_model({"$ref": f"#/components/schemas/{name}"})
        rows.append((short, nprops, usage.get(short, 0), name))
    for short, nprops, used, name in sorted(rows, key=lambda r: (-r[2], r[0])):
        kind = "object" if nprops else "scalar/array"
        lines.append(f"| `{short}` | {kind} | {nprops} | {used} |")
    lines += ["", "## Enums (string values)", "", "| Enum | Values |", "|---|---|"]
    for name, _n, values in sorted(enum_rows):
        short = name.split(".")[-1]
        lines.append(f"| `{short}` | {'`, `'.join(str(v) for v in values[:16])} |")
    (REF / "models-index.md").write_text("\n".join(lines), encoding="utf-8")

    # --- core-models.md --------------------------------------------------
    top = [r for r in rows if r[2] > 0 and r[1] > 0]
    top.sort(key=lambda r: (-r[2], r[0]))
    lines = ["# Core models — fields of the most-used SERTICA DTOs", "", header_note, "",
             f"Top {min(45, len(top))} models ranked by how many operations take or return them. "
             "SERTICA models set `additionalProperties: false`: only the documented keys are accepted.",
             "`?` marks nullable fields. Nested models are listed by their short name — look them up with "
             "`python scripts/sertica_api.py model <Name>`.", ""]
    for short, nprops, used, name in top[:45]:
        s = schemas[name]
        lines += [f"## {short}  ({nprops} fields, {used} ops)", ""]
        for pn, pv in s.get("properties", {}).items():
            if "$ref" in pv:
                t = short_model(pv)
            elif pv.get("type") == "array":
                t = short_model(pv)
            elif "enum" in pv:
                t = "enum(" + "|".join(str(v) for v in pv["enum"][:8]) + ")"
            else:
                t = pv.get("type", "?")
                if pv.get("format"):
                    t += f":{pv['format']}"
            lines.append(f"- `{pn}` : {t}{' ?' if pv.get('nullable') else ''}")
        lines += ["", f"*(schema: `{name}`)*", ""]
    (REF / "core-models.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    spec_path = Path(sys.argv[1]) if len(sys.argv) > 1 else SPEC_DEFAULT
    spec = load_spec(spec_path)
    REF.mkdir(parents=True, exist_ok=True)
    ops = collect(spec)
    captured = date.today().isoformat()
    header_note = (f"Auto-generated by `scripts/build_references.py` from the SERTICA OpenAPI spec "
                   f"({spec['info'].get('version')}, {len(spec['paths'])} paths, {len(ops)} operations) — "
                   f"regenerated {captured}. Base URL: `{BASE}`. Auth: `Authorization: Bearer <accessToken>` "
                   f"from `POST {BASE}/Auth`.")
    tags, leftover = write_domain_files(ops, header_note)
    write_index(ops, header_note)
    write_models(spec, ops, header_note)
    print(f"ops={len(ops)} tags={len(tags)} schemas={len(spec['components']['schemas'])}")
    print("tags:", ", ".join(tags))
    if leftover:
        print("UNCATEGORISED:", ", ".join(leftover))
    for f in sorted(REF.glob("*.md")):
        print(f"  {f.name}: {f.stat().st_size:,} bytes, {sum(1 for _ in f.open(encoding='utf-8'))} lines")


if __name__ == "__main__":
    main()
