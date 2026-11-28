"""Build the letter guide pages under /briefe/ plus sitemap.xml and robots.txt.

Usage: python3 tools/build_guides.py
Edit GUIDES below, then run it again. Content is general information, not legal advice.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://digital-future.ai"

GUIDES = [
    {
        "slug": "jobcenter",
        "title": "Brief vom Jobcenter verstehen",
        "description": "Was ein Brief vom Jobcenter meist bedeutet, welche Fristen wichtig sind und wie Sie ihn in Ihrer Sprache erklärt bekommen.",
        "intro": "Das Jobcenter schreibt oft, wenn es Unterlagen braucht, einen Termin vereinbart oder über Ihre Leistungen entscheidet. Viele dieser Briefe haben eine Frist.",
        "usually": [
            "Aufforderung zur Mitwirkung: Sie sollen Unterlagen schicken, zum Beispiel Gehaltsnachweise oder Kontoauszüge.",
            "Einladung zu einem Termin (Meldeaufforderung) mit Datum und Uhrzeit.",
            "Bescheid über Ihre Leistungen: wie viel Geld Sie bekommen und für welchen Zeitraum.",
        ],
        "check": [
            "Bis wann müssen Sie etwas tun? Das Datum steht meist fett oder im Text mit „bis zum“.",
            "Welche Unterlagen genau verlangt werden.",
            "Ihr Aktenzeichen oder Ihre Nummer der Bedarfsgemeinschaft für die Antwort.",
            "Ob am Ende eine Rechtsbehelfsbelehrung steht. Sie nennt die Frist für einen Widerspruch.",
        ],
        "ar_title": "رسالة من الجوب سنتر",
        "ar_text": "غالبًا يطلب الجوب سنتر مستندات أو يحدد موعدًا أو يخبرك بقرار عن المساعدة. انتبه إلى الموعد النهائي والمستندات المطلوبة ورقم ملفك.",
    },
    {
        "slug": "auslaenderbehoerde",
        "title": "Brief von der Ausländerbehörde verstehen",
        "description": "Termin, Aufenthaltserlaubnis, Unterlagen: was Briefe der Ausländerbehörde meist bedeuten und worauf Sie achten sollten.",
        "intro": "Die Ausländerbehörde schreibt meist wegen Ihres Aufenthaltstitels: für einen Termin, eine Verlängerung oder weil Unterlagen fehlen.",
        "usually": [
            "Termin zur Verlängerung oder Abholung Ihres Aufenthaltstitels.",
            "Liste der Unterlagen, die Sie mitbringen sollen, zum Beispiel Pass, Foto, Mietvertrag, Einkommensnachweise.",
            "Anhörung oder Entscheidung zu Ihrem Antrag.",
        ],
        "check": [
            "Datum und Uhrzeit des Termins und den Ort (Zimmer, Adresse).",
            "Alle Unterlagen auf der Liste, als Original und wenn verlangt als Kopie.",
            "Wann Ihr aktueller Aufenthaltstitel abläuft.",
            "Ob eine Frist für eine Antwort oder Stellungnahme genannt wird.",
        ],
        "ar_title": "رسالة من دائرة الأجانب",
        "ar_text": "غالبًا تكون الرسالة عن موعد لتجديد الإقامة أو عن مستندات ناقصة. انتبه إلى تاريخ الموعد وقائمة المستندات وتاريخ انتهاء إقامتك.",
    },
    {
        "slug": "finanzamt",
        "title": "Brief vom Finanzamt verstehen",
        "description": "Steuerbescheid, Erinnerung, Zahlung: was Briefe vom Finanzamt meist bedeuten und welche Fristen zählen.",
        "intro": "Das Finanzamt schreibt, wenn eine Steuererklärung fehlt, wenn es über Ihre Steuer entschieden hat oder wenn eine Zahlung offen ist.",
        "usually": [
            "Erinnerung an eine fehlende Steuererklärung.",
            "Steuerbescheid: ob Sie Geld zurückbekommen oder nachzahlen müssen.",
            "Zahlungsaufforderung mit Betrag und Datum.",
        ],
        "check": [
            "Das Datum, bis wann Sie die Erklärung abgeben oder zahlen müssen.",
            "Ihre Steuernummer für jede Antwort.",
            "Ob der Bescheid von Ihren Angaben abweicht.",
            "Die Rechtsbehelfsbelehrung am Ende. Sie nennt die Frist für einen Einspruch.",
        ],
        "ar_title": "رسالة من مكتب الضرائب",
        "ar_text": "غالبًا تكون تذكيرًا بإقرار ضريبي أو قرارًا ضريبيًا أو طلب دفع. انتبه إلى الموعد النهائي ورقمك الضريبي.",
    },
    {
        "slug": "vermieter",
        "title": "Brief vom Vermieter verstehen",
        "description": "Mieterhöhung, Nebenkosten, Kündigung: was Briefe vom Vermieter meist bedeuten und worauf Sie achten sollten.",
        "intro": "Vermieter schreiben oft wegen der Miete, der Nebenkosten oder Reparaturen. Manche Briefe verlangen eine Antwort bis zu einem Datum.",
        "usually": [
            "Mieterhöhung mit neuer Miete und Datum, ab wann sie gelten soll.",
            "Nebenkostenabrechnung mit Nachzahlung oder Guthaben.",
            "Ankündigung von Arbeiten in der Wohnung oder im Haus.",
        ],
        "check": [
            "Bis wann Sie zustimmen, zahlen oder antworten sollen.",
            "Ab welchem Datum sich etwas ändert.",
            "Beträge und den Zeitraum der Abrechnung.",
            "Bei Unsicherheit: ein Mieterverein kann den Brief prüfen.",
        ],
        "ar_title": "رسالة من المؤجر",
        "ar_text": "غالبًا تكون عن زيادة الإيجار أو حساب التكاليف الإضافية أو أعمال صيانة. انتبه إلى المواعيد والمبالغ وتاريخ بدء التغيير.",
    },
    {
        "slug": "krankenkasse",
        "title": "Brief von der Krankenkasse verstehen",
        "description": "Fragebogen, Beiträge, Nachweise: was Briefe der Krankenkasse meist bedeuten und welche Fristen wichtig sind.",
        "intro": "Die Krankenkasse schreibt oft wegen Ihrer Versicherung, Ihrer Familie oder Ihrer Beiträge und braucht dafür Angaben von Ihnen.",
        "usually": [
            "Fragebogen zur Familienversicherung oder zu Ihrem Einkommen.",
            "Bescheid über Ihre Beiträge.",
            "Bitte um Nachweise, zum Beispiel eine Schulbescheinigung oder eine Arbeitgeberbescheinigung.",
        ],
        "check": [
            "Bis wann Sie den Fragebogen oder die Nachweise schicken sollen.",
            "Ihre Versichertennummer für die Antwort.",
            "Welche Familienmitglieder betroffen sind.",
            "Ob sich Ihr Beitrag ändert und ab wann.",
        ],
        "ar_title": "رسالة من شركة التأمين الصحي",
        "ar_text": "غالبًا تطلب الشركة استبيانًا أو إثباتات عن دخلك أو عائلتك أو تخبرك بالاشتراكات. انتبه إلى الموعد النهائي ورقم التأمين.",
    },
]

STYLE = """
:root{color-scheme:dark}*{box-sizing:border-box}
body{margin:0;background:#060913;color:#F1F5F9;font-family:'Plus Jakarta Sans',system-ui,sans-serif;line-height:1.65}
a{color:#E6C594}main{max-width:820px;margin:0 auto;padding:32px 20px 64px}
header{display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid rgba(212,175,55,.22)}
header img{width:40px;height:40px;border-radius:50%;border:2px solid #D4AF37}
header a{font-family:'Cinzel',serif;font-weight:700;color:#E6C594;text-decoration:none;letter-spacing:.04em}
h1,h2{font-family:'Cinzel',serif;color:#F5E6B8;line-height:1.25}h1{font-size:2rem;margin:.5rem 0 1rem}h2{font-size:1.3rem;margin-top:2rem}
.card{border:1px solid rgba(212,175,55,.3);background:rgba(15,23,42,.76);border-radius:16px;padding:18px 20px;margin-top:1.5rem}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px}
.btn{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:12px;border:1px solid #D4AF37;color:#F5E6B8;text-decoration:none;font-weight:600}
.btn.primary{background:#D4AF37;color:#060913}
.ar{font-family:'Amiri',serif;font-size:1.15rem}.muted{color:#94A3B8;font-size:.9rem}
ul{padding-inline-start:1.2rem}li{margin:.35rem 0}
"""

HEAD = """<!doctype html>
<html lang="de" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#060913">
<title>{title} | DIGITAL-FUTURE.AI</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cinzel:wght@600;700&family=Plus+Jakarta+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>{style}</style>
</head>
<body>
<header><img src="/logo.png" alt="" width="40" height="40"><a href="/">DIGITAL FUTURE</a></header>
<main>
"""

FOOT = """<p class="muted" style="margin-top:2.5rem">Allgemeine Informationen, keine Rechtsberatung. Bei rechtlichen Fragen wenden Sie sich an eine Beratungsstelle oder einen Anwalt.</p>
<p class="muted"><a href="/briefe/">Alle Ratgeber</a> · <a href="/">Startseite</a></p>
</main>
</body>
</html>
"""


def bullets(items):
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def guide_page(guide):
    url = f"{SITE}/briefe/{guide['slug']}/"
    body = f"""<p class="muted"><a href="/briefe/">Ratgeber</a></p>
<h1>{escape(guide['title'])}</h1>
<p>{escape(guide['intro'])}</p>
<h2>Was meist im Brief steht</h2>
{bullets(guide['usually'])}
<h2>Darauf sollten Sie achten</h2>
{bullets(guide['check'])}
<div class="card">
<h2 style="margin-top:0">Ihren Brief erklären lassen</h2>
<p>Fotografieren Sie den Brief. Sie bekommen in Ihrer Sprache: was drinsteht, die Frist, was Sie tun müssen, und eine fertige Antwort.</p>
<div class="cta"><a class="btn primary" href="/#letterHelper">Brief erklären lassen</a></div>
</div>
<div class="card ar" dir="rtl" lang="ar">
<h2 style="margin-top:0">{escape(guide['ar_title'])}</h2>
<p>{escape(guide['ar_text'])}</p>
<div class="cta"><a class="btn" href="/#letterHelper">اشرح رسالتي</a></div>
</div>
"""
    return HEAD.format(title=escape(guide["title"]), description=escape(guide["description"]), url=url, style=STYLE) + body + FOOT


def index_page():
    url = f"{SITE}/briefe/"
    items = "".join(
        f'<div class="card"><h2 style="margin-top:0"><a href="/briefe/{g["slug"]}/">{escape(g["title"])}</a></h2><p class="muted">{escape(g["description"])}</p></div>'
        for g in GUIDES
    )
    body = f"""<h1>Ratgeber: Behördenbriefe verstehen</h1>
<p>Kurze Erklärungen zu häufigen Briefen in Deutschland, mit den Fristen und Unterlagen, auf die es ankommt.</p>
<p class="ar" dir="rtl" lang="ar">شروحات قصيرة لأكثر الرسائل الرسمية شيوعًا في ألمانيا.</p>
{items}
"""
    return HEAD.format(title="Ratgeber: Behördenbriefe verstehen", description="Erklärungen zu Briefen vom Jobcenter, der Ausländerbehörde, dem Finanzamt, dem Vermieter und der Krankenkasse.", url=url, style=STYLE) + body + FOOT


def main():
    for guide in GUIDES:
        folder = ROOT / "briefe" / guide["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(guide_page(guide), encoding="utf-8")
    (ROOT / "briefe" / "index.html").write_text(index_page(), encoding="utf-8")
    urls = [f"{SITE}/", f"{SITE}/briefe/"] + [f"{SITE}/briefe/{g['slug']}/" for g in GUIDES]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nDisallow: /tests/\nDisallow: /tools/\nDisallow: /security/\nSitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8",
    )
    print(f"built {len(GUIDES)} guides, index, sitemap.xml and robots.txt")


if __name__ == "__main__":
    main()
