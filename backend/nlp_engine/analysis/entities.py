import os
import re
import json
from collections import Counter
from groq import Groq

# Attempt spaCy load safely
nlp_spacy = None
try:
    import spacy
    nlp_spacy = spacy.load("en_core_web_sm")
except Exception:
    nlp_spacy = None


def extract_entities(text: str) -> list[dict]:
    """Extract flat entities for backward compatibility."""
    detailed = extract_chapter_entities(text)
    flat = []
    for cat, items in detailed.items():
        for item in items:
            flat.append({
                "text": item["name"],
                "label": cat.upper(),
                "description": f"Entity of type {cat}",
                "count": item["count"],
            })
    return flat


def _sanitize_hindi_entities(data: dict, text: str) -> dict:
    """Keep only entity names grounded in the Hindi chapter text."""
    generic_terms = {
        "आधार पर", "स्थानों में", "क्रोध करने", "स्वभाव की", "वाचन का",
        "नाट्य प्रस्तुति", "वह कर", "जन्म उत्तर", "की अन्य", "हुआ था",
        "मुख्य", "अध्याय", "पाठ", "प्रश्न", "उत्तर", "रीप्रिंट",
    }
    normalized_text = re.sub(r"\s+", " ", text).strip()
    result = {}

    for category in ("persons", "locations", "organizations", "dates", "other"):
        cleaned = []
        for item in data.get(category, []) if isinstance(data, dict) else []:
            if not isinstance(item, dict):
                continue
            name = re.sub(r"\s+", " ", str(item.get("name", ""))).strip(" .,;:।")
            if not name or name.lower() in {term.lower() for term in generic_terms}:
                continue
            if name not in normalized_text:
                continue
            if category == "dates":
                if not re.fullmatch(r"(?:1[5-9]\d{2}|20\d{2})", name):
                    continue
                if re.search(rf"Reprint\s*{re.escape(name)}", normalized_text, re.IGNORECASE):
                    continue
            elif re.search(r"\d", name) or len(name) > 45:
                continue
            cleaned.append({"name": name, "count": max(1, int(item.get("count", 1)))})
        result[category] = cleaned[:15]

    return result


def extract_chapter_entities(text: str) -> dict:
    """
    Extract Named Entities from NCERT chapter text:
    - Persons (e.g. M. Hamel, Franz, Wachter)
    - Locations (e.g. Alsace, Lorraine, Paris, Berlin)
    - Organizations (e.g. Prussian Army, School Board)
    - Dates / Time markers (e.g. 1870, Sunday morning, forty years)
    - Other entities

    Returns categorized dictionary with actual entity names and occurrence counts.
    """
    if not text or not text.strip():
        return {
            "persons": [],
            "locations": [],
            "organizations": [],
            "dates": [],
            "other": [],
        }

    is_devanagari = len(re.findall(r'[\u0900-\u097F]', text)) > (len(text) * 0.15)

    # If spaCy English model is available and text is English
    if nlp_spacy is not None and not is_devanagari:
        doc = nlp_spacy(text[:25000])
        categories = {
            "persons": Counter(),
            "locations": Counter(),
            "organizations": Counter(),
            "dates": Counter(),
            "other": Counter(),
        }

        for ent in doc.ents:
            name = ent.text.strip().replace("\n", " ")
            if len(name) < 2 or re.match(r"^\d+$", name):
                continue

            label = ent.label_
            if label in {"PERSON"}:
                categories["persons"][name] += 1
            elif label in {"GPE", "LOC", "FAC"}:
                categories["locations"][name] += 1
            elif label in {"ORG"}:
                categories["organizations"][name] += 1
            elif label in {"DATE", "TIME"}:
                categories["dates"][name] += 1
            elif label in {"EVENT", "NORP", "LAW", "PRODUCT"}:
                categories["other"][name] += 1

        result = {}
        for cat, counts in categories.items():
            result[cat] = [
                {"name": name, "count": count}
                for name, count in counts.most_common(15)
            ]
        # If spaCy extracted good entities, return them
        if any(len(v) > 0 for v in result.values()):
            return result

    # Multilingual / LLM-based entity extraction for Devanagari or fallback
        groq_key = os.getenv("GROQ_API_KEY", "")
    try:
        client = Groq(api_key=groq_key)
        prompt = f"""Extract actual Named Entities from this NCERT chapter text.
Categorize into:
1. "persons": names of specific individuals, characters, or historical figures
2. "locations": cities, countries, towns, regions, specific places
3. "organizations": institutions, government bodies, armies, schools
4. "dates": years, dates, temporal phrases, historical periods
5. "other": significant historical events, languages, treaties

For each entity, provide its actual name and approximate frequency in the text.
Return ONLY valid JSON in this format:
{{
  "persons": [{{"name": "...", "count": 5}}],
  "locations": [{{"name": "...", "count": 3}}],
  "organizations": [{{"name": "...", "count": 2}}],
  "dates": [{{"name": "...", "count": 2}}],
  "other": [{{"name": "...", "count": 1}}]
}}

Text:
{text[:4500]}
"""
        resp = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=800,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?", "", raw)
        raw = re.sub(r"```$", "", raw).strip()
        return _sanitize_hindi_entities(json.loads(raw), text)
    except Exception as e:
        print(f"[Entities] Entity extraction fallback: {e}")

    # Offline regex-based fallback
    capitalized_words = Counter(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', text))
    date_patterns = Counter(re.findall(r'\b(?:18\d\d|19\d\d|20\d\d|Sunday|Monday|Tuesday|morning|afternoon|year)\b', text, re.IGNORECASE))

    # Hindi fallback for installations without a working LLM/API. These
    # patterns capture proper names near common Hindi context markers.
    known_persons = (
        "तुलसीदास", "राम", "लक्ष्मण", "परशुराम", "विश्वामित्र", "सीता",
        "हनुमान", "कबीर", "सूरदास", "प्रेमचंद", "रहीम", "मीरा",
    )
    known_locations = (
        "उत्तर प्रदेश", "बाँदा", "राजापुर", "काशी", "अयोध्या", "अवध",
        "ब्रज", "वाराणसी", "दिल्ली", "भारत", "गंगा", "हिमालय",
    )
    hindi_names = Counter({
        name: len(re.findall(re.escape(name), text))
        for name in known_persons
        if name in text
    })
    hindi_locations = Counter({
        name: len(re.findall(re.escape(name), text))
        for name in known_locations
        if name in text
    })
    hindi_dates = Counter()
    for match in re.finditer(r"(?<!\d)(?:1[5-9]\d{2}|20\d{2})(?!\d)", text):
        value = match.group(0)
        before = text[max(0, match.start() - 12):match.start()].lower()
        if "reprint" not in before:
            hindi_dates[value] += 1
    if hindi_names or hindi_locations or hindi_dates:
        names = [{"name": name, "count": count} for name, count in hindi_names.most_common(15)]
        return {
            "persons": names[:8],
            "locations": [
                {"name": name, "count": count}
                for name, count in hindi_locations.most_common(15)
            ],
            "organizations": [],
            "dates": [{"name": value, "count": count} for value, count in hindi_dates.most_common(10)],
            "other": [],
        }

    common_stops = {"The", "This", "That", "When", "Then", "After", "Before", "There", "Chapter"}
    filtered_caps = [
        {"name": name, "count": count}
        for name, count in capitalized_words.most_common(20)
        if name not in common_stops
    ]

    return {
        "persons": filtered_caps[:6],
        "locations": filtered_caps[6:10],
        "organizations": filtered_caps[10:13],
        "dates": [{"name": k, "count": v} for k, v in date_patterns.most_common(5)],
        "other": filtered_caps[13:16],
    }