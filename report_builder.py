"""
Vertu Motors — Daily Security Report Generator
===============================================
Run:  python3 generate_report.py

To add/remove sites: edit sites_config.py only.
To change report content: edit the SITE_DATA section near the bottom of this file.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from sites_config import SITES as SITE_REGISTRY, ARC_CENTRES

PAGE_W, PAGE_H = A4

DARK_TEAL    = colors.HexColor("#0E3D40")
MID_TEAL     = colors.HexColor("#1A5C61")
GOLD         = colors.HexColor("#E8B84B")
LIGHT_BG     = colors.HexColor("#F6F8F8")
BORDER       = colors.HexColor("#D0DCDD")
TEXT_DARK    = colors.HexColor("#1A2626")
TEXT_MID     = colors.HexColor("#3D5254")
TEXT_MUTED   = colors.HexColor("#6B8284")
RED_BG       = colors.HexColor("#FEF0F0")
RED_ACC      = colors.HexColor("#C0392B")
RED_BORDER   = colors.HexColor("#F5C6C6")
AMBER_BG     = colors.HexColor("#FEFAF0")
AMBER_ACC    = colors.HexColor("#B7860B")
AMBER_BORDER = colors.HexColor("#F0DFA0")
GREEN_BG     = colors.HexColor("#F0FAF4")
GREEN_ACC    = colors.HexColor("#1E7A46")
GREEN_BORDER = colors.HexColor("#A8D8B8")
BLUE_BG      = colors.HexColor("#EFF6FF")
BLUE_ACC     = colors.HexColor("#1A5FA8")
BLUE_BORDER  = colors.HexColor("#B5D4F4")
WHITE        = colors.white

def S(name, **kw):
    d = dict(fontName="Helvetica", fontSize=9, textColor=TEXT_DARK, leading=13)
    d.update(kw)
    return ParagraphStyle(name, **d)

STYLES = {
    "site_hdr":  S("sh",  fontName="Helvetica-Bold", fontSize=11, textColor=DARK_TEAL, leading=14),
    "site_addr": S("sa",  fontName="Helvetica",      fontSize=7.5, textColor=TEXT_MUTED, leading=10),
    "ev_time":   S("et",  fontName="Courier",        fontSize=7.5, textColor=TEXT_MUTED, leading=11),
    "ev_main":   S("em",  fontName="Helvetica-Bold", fontSize=8.5, textColor=TEXT_DARK,  leading=12),
    "ev_note":   S("en",  fontName="Helvetica",      fontSize=8,   textColor=TEXT_MID,   leading=11),
    "col_hdr":   S("ch",  fontName="Helvetica-Bold", fontSize=7.5, textColor=WHITE,      leading=11, alignment=TA_CENTER),
    "maint_cam": S("mc",  fontName="Helvetica-Bold", fontSize=8,   textColor=TEXT_DARK,  leading=11),
    "maint_rsn": S("mr",  fontName="Helvetica",      fontSize=8,   textColor=TEXT_MID,   leading=11),
    "maint_dt":  S("md",  fontName="Courier",        fontSize=7.5, textColor=TEXT_MUTED, leading=11),
    "quiet":     S("q",   fontName="Helvetica",      fontSize=8.5, textColor=GREEN_ACC,  leading=12),
    "quiet_note":S("qn",  fontName="Helvetica",      fontSize=8,   textColor=colors.HexColor("#4A7A5A"), leading=11),
    "footer":    S("f",   fontName="Helvetica",      fontSize=7,   textColor=TEXT_MUTED, leading=10),
    "badge_ok":  S("bok", fontName="Helvetica-Bold", fontSize=7,   textColor=GREEN_ACC,  leading=9),
    "badge_warn":S("bwn", fontName="Helvetica-Bold", fontSize=7,   textColor=AMBER_ACC,  leading=9),
    "badge_bad": S("bbd", fontName="Helvetica-Bold", fontSize=7,   textColor=RED_ACC,    leading=9),
    "badge_info":S("bin", fontName="Helvetica-Bold", fontSize=7,   textColor=BLUE_ACC,   leading=9),
}

STATUS_META = {
    "alert":     ("Alert",     RED_BG,   RED_ACC,   RED_BORDER),
    "warning":   ("Activity",  AMBER_BG, AMBER_ACC, AMBER_BORDER),
    "clear":     ("Clear",     GREEN_BG, GREEN_ACC, GREEN_BORDER),
    "no_signal": ("No signal", AMBER_BG, AMBER_ACC, AMBER_BORDER),
}

BADGE_MAP = {
    "Resolved":         (STYLES["badge_ok"],   GREEN_BG),
    "False alarm":      (STYLES["badge_ok"],   GREEN_BG),
    "No action":        (STYLES["badge_ok"],   GREEN_BG),
    "Keyholder called": (STYLES["badge_warn"], AMBER_BG),
    "Attempted":        (STYLES["badge_warn"], AMBER_BG),
    "Genuine incident": (STYLES["badge_bad"],  RED_BG),
}

def _boxed(rows, dw):
    t = Table([[r] for r in rows], colWidths=[dw])
    t.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.5,BORDER),("ROUNDEDCORNERS",[4]),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    return t

def report_header(dw, report_date, period):
    left = Table([
        [Paragraph('<font color="#E8B84B"><b>Pathway Risk Management</b></font>',
            S("ht", fontName="Helvetica-Bold", fontSize=15, textColor=GOLD, leading=19))],
        [Paragraph('Vertu Motors — Daily Security Report',
            S("hs", fontName="Helvetica", fontSize=8,
              textColor=colors.HexColor("#9EBABB"), leading=11))],
    ], colWidths=[dw*0.6])
    left.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),DARK_TEAL),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    right = Table([
        [Paragraph("Report date", S("rl", fontName="Helvetica", fontSize=7,
             textColor=colors.HexColor("#9EBABB"), leading=10, alignment=TA_RIGHT)),
         Paragraph(report_date, S("rv", fontName="Helvetica-Bold", fontSize=9,
             textColor=WHITE, leading=12, alignment=TA_RIGHT))],
        [Paragraph("Period covered", S("rl2", fontName="Helvetica", fontSize=7,
             textColor=colors.HexColor("#9EBABB"), leading=10, alignment=TA_RIGHT)),
         Paragraph(period, S("rv2", fontName="Helvetica", fontSize=8,
             textColor=colors.HexColor("#C8DCDD"), leading=11, alignment=TA_RIGHT))],
    ], colWidths=[dw*0.4])
    right.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),DARK_TEAL),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),6*mm),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    t = Table([[left, right]], colWidths=[dw*0.6, dw*0.4])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),DARK_TEAL),
        ("TOPPADDING",(0,0),(-1,-1),11),("BOTTOMPADDING",(0,0),(-1,-1),11),
        ("LEFTPADDING",(0,0),(0,0),6*mm),("RIGHTPADDING",(-1,0),(-1,0),0),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    return t

def dashboard(dw, stats):
    n = len(stats)
    cw = dw / n
    val_row = [Paragraph(str(v), S("dv", fontName="Helvetica-Bold", fontSize=26,
        textColor=tc, leading=30, alignment=TA_CENTER)) for v,l,bg,tc in stats]
    lbl_row = [Paragraph(l, S("dl", fontName="Helvetica", fontSize=7,
        textColor=tc, leading=10, alignment=TA_CENTER)) for v,l,bg,tc in stats]
    t = Table([val_row, lbl_row], colWidths=[cw]*n)
    style = [
        ("TOPPADDING",(0,0),(-1,0),12),("BOTTOMPADDING",(0,0),(-1,0),3),
        ("TOPPADDING",(0,1),(-1,1),0), ("BOTTOMPADDING",(0,1),(-1,1),12),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("LINEBELOW",(0,1),(-1,1),0.5,BORDER),
    ]
    for i,(_,__,bg,___) in enumerate(stats):
        style.append(("BACKGROUND",(i,0),(i,-1),bg))
        if i > 0:
            style.append(("LINEBEFORE",(i,0),(i,-1),0.5,WHITE))
    t.setStyle(TableStyle(style))
    return t

def overview_table(dw, sites):
    cw = [dw*0.36, dw*0.14, dw*0.14, dw*0.15, dw*0.15, dw*0.13]
    hdr = [Paragraph(h, STYLES["col_hdr"]) for h in
           ["Dealership","Alarms","False alarms","Audio challenges","CCTV OOH","Status"]]

    def nz(v, tc=RED_ACC):
        if v == 0:
            return Paragraph("—", S("z0", fontName="Helvetica", fontSize=8.5,
                textColor=TEXT_MUTED, leading=12, alignment=TA_CENTER))
        return Paragraph(str(v), S("nv", fontName="Helvetica-Bold", fontSize=9,
            textColor=tc, leading=12, alignment=TA_CENTER))

    rows = [hdr]
    for s in sites:
        lbl, sbg, stc, _ = STATUS_META[s["status"]]
        rows.append([
            Paragraph(s["name"], S("on", fontName="Helvetica-Bold", fontSize=8.5,
                textColor=DARK_TEAL, leading=12)),
            nz(s["alarms"]),
            nz(s["false_alarms"], tc=AMBER_ACC),
            nz(s["audio"],        tc=AMBER_ACC),
            nz(s["cctv_ooh"],     tc=BLUE_ACC),
            Paragraph(f"● {lbl}", S("st", fontName="Helvetica-Bold", fontSize=7.5,
                textColor=stc, leading=11, alignment=TA_CENTER)),
        ])

    t = Table(rows, colWidths=cw)
    style = [
        ("BACKGROUND",(0,0),(-1,0),MID_TEAL),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LINEBELOW",(0,0),(-1,0),0.5,colors.HexColor("#0A3033")),
        ("BOX",(0,0),(-1,-1),0.5,BORDER),("ROUNDEDCORNERS",[4]),
    ]
    for i in range(1, len(rows)):
        style.append(("BACKGROUND",(0,i),(-2,i), LIGHT_BG if i%2==0 else WHITE))
        style.append(("LINEBELOW",(0,i),(-1,i),0.5,BORDER))
        _, sbg, _, _ = STATUS_META[sites[i-1]["status"]]
        style.append(("BACKGROUND",(5,i),(5,i), sbg))
    t.setStyle(TableStyle(style))
    return t

def section_div(dw, title, color=MID_TEAL):
    t = Table([[Paragraph(f"  {title}", S("sd", fontName="Helvetica-Bold",
        fontSize=8.5, textColor=WHITE, leading=12))]], colWidths=[dw])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),color),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    return t

def mini_hdr(dw, label, bg, tc):
    t = Table([[Paragraph(label, S("mh", fontName="Helvetica-Bold",
        fontSize=7.5, textColor=tc, leading=11))]], colWidths=[dw])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),bg),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
    ]))
    return t

def event_rows(dw, events):
    rows = []
    for ev in events:
        content = [Paragraph(ev["main"], STYLES["ev_main"])]
        if ev.get("note"):
            content.append(Paragraph(ev["note"], STYLES["ev_note"]))
        badge = ev.get("badge","")
        if badge:
            bstyle, bbg = BADGE_MAP.get(badge, (STYLES["badge_info"], BLUE_BG))
            bc = Table([[Paragraph(badge, bstyle)]], colWidths=[None])
            bc.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),bbg),
                ("BOX",(0,0),(-1,-1),0.5,BORDER),("ROUNDEDCORNERS",[3]),
                ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
            ]))
            content.append(bc)
        ct = Table([[c] for c in content], colWidths=[dw-26*mm])
        ct.setStyle(TableStyle([
            ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),1),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ]))
        rt = Table([[Paragraph(ev["time"], STYLES["ev_time"]), ct]],
            colWidths=[24*mm, dw-24*mm])
        rt.setStyle(TableStyle([
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(0,0),8),("LEFTPADDING",(1,0),(1,0),4),
            ("RIGHTPADDING",(1,0),(1,0),8),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LINEBELOW",(0,0),(-1,-1),0.5,BORDER),
        ]))
        rows.append(rt)
    return rows

def no_events_row(dw, msg):
    t = Table([[Paragraph(msg, S("ne", fontName="Helvetica", fontSize=8,
        textColor=TEXT_MUTED, leading=11))]], colWidths=[dw])
    t.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("LINEBELOW",(0,0),(-1,-1),0.5,BORDER),
    ]))
    return t

def clear_row(dw):
    t = Table([[
        Paragraph("✓", S("ck", fontName="Helvetica-Bold", fontSize=10,
            textColor=GREEN_ACC, leading=13)),
        Paragraph("No alarm activations or CCTV events recorded in this period.",
            STYLES["quiet"]),
    ]], colWidths=[8*mm, dw-8*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),GREEN_BG),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(0,0),8),("LEFTPADDING",(1,0),(1,0),4),
        ("RIGHTPADDING",(1,0),(1,0),8),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    return t

def no_signal_row(dw):
    t = Table([[
        Paragraph("!", S("ns", fontName="Helvetica-Bold", fontSize=10,
            textColor=AMBER_ACC, leading=13)),
        Paragraph("No alarm signal received in the past 7 days — please confirm system connectivity.",
            STYLES["quiet_note"]),
    ]], colWidths=[8*mm, dw-8*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),AMBER_BG),
        ("BOX",(0,0),(-1,-1),0.5,AMBER_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(0,0),8),("LEFTPADDING",(1,0),(1,0),4),
        ("RIGHTPADDING",(1,0),(1,0),8),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    return t

def site_card(dw, site):
    blocks = []

    # Header row — site name and address only, no ARC reference
    hdr_t = Table([[
        Paragraph(site["name"], STYLES["site_hdr"]),
        Paragraph(site.get("address",""), STYLES["site_addr"]),
    ]], colWidths=[dw])
    hdr_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LIGHT_BG),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("VALIGN",(0,0),(-1,-1),"BOTTOM"),
        ("LINEBELOW",(0,0),(-1,-1),0.5,BORDER),
    ]))
    blocks.append(hdr_t)

    status = site.get("status","clear")

    if status == "no_signal":
        blocks.append(no_signal_row(dw))
    elif status == "clear":
        blocks.append(clear_row(dw))
    else:
        alarms = site.get("alarms",[])
        n = len(alarms)
        blocks.append(mini_hdr(dw,
            f"ALARM ACTIVATIONS — {n} event{'s' if n!=1 else ''}" if n else "ALARM ACTIVATIONS",
            RED_BG, RED_ACC))
        if alarms:
            for r in event_rows(dw, alarms): blocks.append(r)
        else:
            blocks.append(no_events_row(dw, "No alarm activations in this period."))

        audio = site.get("audio",[])
        if audio:
            blocks.append(mini_hdr(dw,
                f"AUDIO CHALLENGES — {len(audio)} issued", AMBER_BG, AMBER_ACC))
            for r in event_rows(dw, audio): blocks.append(r)

    return KeepTogether([_boxed(blocks, dw), Spacer(1,3*mm)])

def add_footer(canvas, doc):
    canvas.saveState()
    lm, bm, dw = 14*mm, 8*mm, PAGE_W-28*mm
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(lm, bm, "Pathway Risk Management  |  Confidential — Vertu Motors client report")
    canvas.drawRightString(lm+dw, bm, f"Page {doc.page}")
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(lm, bm+4*mm, lm+dw, bm+4*mm)
    canvas.restoreState()

# =============================================================================
#  REPORT SETTINGS
# =============================================================================

REPORT_DATE   = "Tuesday 12 May 2026"
REPORT_PERIOD = "11 May (evening) – 12 May 2026"
OUTPUT_PATH   = "/mnt/user-data/outputs/Vertu_Daily_Security_Report_12May2026_v4.pdf"

# =============================================================================
#  SITE DATA
#  Add an entry here for every site that has activity today.
#  Sites in sites_config.py that are NOT listed here are shown as "clear".
#  Keys must match the "id" field in sites_config.py.
#
#  STATUS OPTIONS:
#    "alert"     - genuine incident requiring action
#    "warning"   - activity recorded (false alarms, audio challenges etc.)
#    "clear"     - no activity (auto-applied if id not listed here)
#    "no_signal" - no signal received in past 7 days
#
#  EVENT FIELDS:  time, level (high/medium/low), main, note, badge
#  BADGE OPTIONS: "Genuine incident" | "False alarm" | "No action" |
#                 "Resolved" | "Keyholder notified"
# =============================================================================

SITE_DATA = {
    "ferrari_exeter": {
        "status": "alert",
        "alarms": [
            {"time": "05:38  12/05", "level": "high",
             "main": "Intrusion detection — Camera 3 (exterior). Alarm probability: 100%.",
             "note": "05:40: Keyholder notified. Alarm suspended to 06:00. 06:03: Audio challenge issued via on-site speaker. 06:04: Keyholder confirmed awareness. Cause: intrusion / suspicious activity. Alarm closed.",
             "badge": "Genuine incident"},
        ],
        "audio": [
            {"time": "06:03  12/05", "level": "high",
             "main": "Audio challenge issued following intrusion detection.",
             "note": "Keyholder confirmed. See alarm entry above.", "badge": "Resolved"},
        ],
    },
    "plymouth_renault": {
        "status": "warning",
        "alarms": [
            {"time": "20:58  11/05", "level": "medium",
             "main": "Intruder alarm — showroom entrance door contact and roller shutters 1 & 2.",
             "note": "Keyholder notified. False alarm confirmed. Alarm closed.",
             "badge": "False alarm"},
        ],
        "audio": [],
    },
    "exeter_jlr": {
        "status": "warning",
        "alarms": [
            {"time": "04:38  12/05", "level": "medium",
             "main": "Intruder alarm — audio challenge issued. No further action required.",
             "note": "", "badge": "No action"},
        ],
        "audio": [
            {"time": "18:50  11/05", "level": "low",    "main": "Motion detected — audio challenge issued.", "note": "Out-of-hours working on site.", "badge": ""},
            {"time": "20:51  11/05", "level": "medium", "main": "Motion detected — audio challenge issued.", "note": "", "badge": ""},
            {"time": "22:29  11/05", "level": "medium", "main": "Motion detected — audio challenge issued.", "note": "", "badge": ""},
            {"time": "23:13  11/05", "level": "low",    "main": "Motion detected — audio challenge issued.", "note": "Disregarded per site standing instructions.", "badge": ""},
            {"time": "04:38  12/05", "level": "medium", "main": "Intruder alarm — audio challenge issued.", "note": "No further action required.", "badge": ""},
            {"time": "06:59  12/05", "level": "medium", "main": "Motion detected — audio challenge issued.", "note": "", "badge": ""},
        ],
    },
    "plymouth_volvo": {
        "status": "warning",
        "alarms": [
            {"time": "20:58  11/05", "level": "medium",
             "main": "Intruder alarm triggered.",
             "note": "Keyholder notified. False alarm confirmed. Alarm closed.",
             "badge": "False alarm"},
        ],
        "audio": [],
    },
    "carlisle": {
        "status": "clear",
        "alarms": [], "audio": [],
    },
    "yeovil_valet": {
        "status": "no_signal",
        "alarms": [], "audio": [],
    },
    # All other sites not listed here appear as "clear" automatically
}

# =============================================================================
#  BUILD
# =============================================================================

def build_pdf(output_path, report_date, report_period, site_data, site_registry=None, arc_centres=None):
    if site_registry is None:
        site_registry = SITE_REGISTRY
    if arc_centres is None:
        arc_centres = ARC_CENTRES
    active = [s for s in site_registry if s.get("active", True)]

    merged = []
    for reg in active:
        sid = reg["id"]
        ev  = site_data.get(sid, {})
        merged.append({
            "id":          sid,
            "name":        reg["name"],
            "address":     reg.get("address",""),
            "arc_label":   arc_centres.get(reg["arc"], reg["arc"]),
            "arc_short":   arc_centres.get(reg["arc"], reg["arc"])[:6].upper(),
            "status":      ev.get("status","clear"),
            "alarms":      ev.get("alarms",[]),
            "audio":       ev.get("audio",[]),
            "maintenance": ev.get("maintenance",[]),
        })

    total_alarms   = sum(len(s["alarms"])  for s in merged)
    total_false    = sum(1 for s in merged for e in s["alarms"] if e.get("badge")=="False alarm")
    total_audio    = sum(len(s["audio"])   for s in merged)
    total_cctv_ooh = sum(len(s["alarms"])+len(s["audio"]) for s in merged)
    genuine        = total_alarms - total_false

    doc = SimpleDocTemplate(output_path, pagesize=A4,
        topMargin=14*mm, bottomMargin=16*mm,
        leftMargin=14*mm, rightMargin=14*mm)
    dw = PAGE_W - 28*mm
    story = []

    story.append(report_header(dw, report_date, report_period))
    story.append(dashboard(dw, [
        (total_cctv_ooh, "CCTV activations\nout of hours",  BLUE_BG,  BLUE_ACC),
        (total_audio,    "Audio challenges\nissued",         AMBER_BG, AMBER_ACC),
        (total_alarms,   "Total alarms",                     RED_BG,   RED_ACC),
        (total_false,    "False alarms\nconfirmed",          AMBER_BG, AMBER_ACC),
        (genuine,        "Genuine incidents",                RED_BG,   RED_ACC),
    ]))
    story.append(Spacer(1, 4*mm))

    story.append(section_div(dw, f"ALL DEALERSHIPS — OVERVIEW  ({len(active)} sites monitored)"))
    story.append(Spacer(1, 2*mm))
    story.append(overview_table(dw, [{
        "name":        s["name"],
        "alarms":      len(s["alarms"]),
        "false_alarms":sum(1 for e in s["alarms"] if e.get("badge")=="False alarm"),
        "audio":       len(s["audio"]),
        "cctv_ooh":    len(s["alarms"])+len(s["audio"]),
        "status":      s["status"],
    } for s in merged]))
    story.append(Spacer(1, 5*mm))

    story.append(section_div(dw, "DETAILED ACTIVITY BY DEALERSHIP"))
    story.append(Spacer(1, 3*mm))
    for s in merged:
        story.append(site_card(dw, s))

    story.append(HRFlowable(width=dw, thickness=0.5, color=BORDER))
    story.append(Spacer(1, 2*mm))
    story.append(Table([[
        Paragraph("Prepared by: <b>Pathway Risk Management</b>", STYLES["footer"]),
        Paragraph(f"Report generated: {report_date}",
            S("fr", fontName="Helvetica", fontSize=7, textColor=TEXT_MUTED,
              leading=10, alignment=TA_RIGHT)),
    ]], colWidths=[dw*0.5, dw*0.5], style=[
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    print(f"Done → {OUTPUT_PATH}")

if __name__ == "__main__":
    # Standalone test run using module-level sample data
    build_pdf(OUTPUT_PATH, REPORT_DATE, REPORT_PERIOD, SITE_DATA)
