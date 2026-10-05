"""Deterministic multilingual intent catalogue and approved fallback templates."""
import re

CATALOGUE = {
    "dialogue": {"aliases": r"^(?:(?:bro|bhai)\s+)?(?:hi|hey|hello|good (?:morning|evening|afternoon)|thanks?(?: you)?|thank you|okay|ok|nice|great|who are you|what can you do|how (?:are you|can you help(?: me)?)|what.s up|kya chal raha hai|kaisa hai|kaise ho|namaste|shukriya|theek hai|नमस्ते|धन्यवाद|कैसे हो|आप कौन हैं)[!?.\s]*(?:bro|bhai)?[!?.\s]*$", "tools": ["get_project_summary"]},
    "priorities": {"aliases": r"main execution items|execution priorities|review priorities|items.*(?:should|to).*review", "tools": ["get_project_summary", "get_execution_warnings", "get_pending_reviews"]},
    "overview": {"aliases": r"overview|summary|project status|परियोजना.*स्थिति|सारांश|project.*haal|project.*sthiti", "tools": ["get_project_summary"]},
    "pending": {"aliases": r"pending|await|(?<![\u0900-\u097f])लंबित(?![\u0900-\u097f])|बाकी.*समीक्षा|review.*baaki|review.*baki|kaunsi teams|कौन.*टीम", "tools": ["get_pending_reviews"]},
    "delayed": {"aliases": r"delay|late|देरी|विलंब|deri", "tools": ["get_delayed_activities"]},
    "risk": {"aliases": r"at risk|जोखिम|risk|khatra", "tools": ["get_delayed_activities"]},
    "warnings": {"aliases": r"warning|attention|चेतावनी|dhyan", "tools": ["get_execution_warnings"]},
    "variance": {"aliases": r"variance|progress|actual|प्रगति|विचलन|pragati", "tools": ["get_schedule_variance"]},
    "health": {"aliases": r"health|declin|स्वास्थ्य|sehat", "tools": ["get_project_health", "search_project_memory"]},
    "changes": {"aliases": r"changed|this week|बदल|इस सप्ताह|badla|hafte", "tools": ["search_project_memory"]},
    "dependencies": {"aliases": r"dependenc|milestone|predecessor|निर्भर|मील का पत्थर|nirbhar", "tools": ["get_dependency_impact"]},
    "timeline": {"aliases": r"timeline|previously|इतिहास|पहले|pehle", "tools": ["get_activity_timeline"]},
    "memory": {"aliases": r"memory|lesson|decision|स्मृति|सीख|निर्णय|faisl|yaad", "tools": ["search_project_memory"]},
    "assigned": {"aliases": r"assigned|my team|my work|मेरी टीम|काम सौंप|meri team|mera kaam", "tools": ["get_schedule_variance"]},
    "submit_help": {"aliases": r"(?:how|कैसे|kaise).*(?:submit|field update|जमा|अपडेट)|(?:submission guidance)", "tools": []},
    "review_help": {"aliases": r"(?:how|कैसे|kaise).*(?:review|समीक्षा)|review process|समीक्षा प्रक्रिया", "tools": []},
    "evidence_help": {"aliases": r"evidence requirements|what evidence|साक्ष्य|saboot|evidence.*needed", "tools": []},
    "provider_help": {"aliases": r"provider|api key|ai unavailable|ai.*उपलब्ध", "tools": []},
}

TEXT = {
 "en": {
  "scope": "I explain authorized PRAVAHA projects, schedules, field execution, reviews, warnings and memory. Choose a suggested project question.",
  "clarify": "Please choose one topic and an authorized project. Select an activity for its timeline; use the evidence search for decisions or lessons.",
  "unavailable": "Guided fallback - AI temporarily unavailable. This is a predefined response using the current authorized evidence, not an AI analysis.",
  "checked": "Data checked at {timestamp}. Scope: {scope}. {count} evidence records shown; partial page: {partial}.",
  "pending": "There are {count} updates awaiting PM review in {project}. Reported progress remains unconfirmed until PM review.",
  "data": "Current authorized {topic} evidence for {project} is shown below. Missing values are UNKNOWN; these records do not prove causes or future dates.",
  "empty": "No matching authorized records were returned. This does not establish that work, decisions or lessons occurred.",
  "submit_help": "Open Field Updates / Add field update in the Team Leader workspace. Describe the assigned activity, location, date and observed progress. Submit evidence; deterministic matching recommends a link and your PM confirms actuals.",
  "review_help": "The assigned PM opens Planner Review, checks field evidence and match, then confirms, changes the match, unmatches or requests information. Only PM confirmation contributes authoritative actual progress. The assistant cannot review or approve.",
  "evidence_help": "Include the activity code, location, observed date, progress and supporting field evidence. Imported baselines and PM-confirmed actuals remain distinct. A current health score alone cannot prove historical decline or its cause.",
  "provider_help": "An operator configures Groq/NVIDIA keys and a compatible model on the backend, then restarts it. Guided answers work without a key. Never paste secrets into chat. Account quota and access are controlled by the provider.",
 },
 "hi": {
  "scope": "मैं अधिकृत PRAVAHA परियोजना, समय-सारणी, फील्ड कार्य, समीक्षा, चेतावनी और स्मृति समझाता हूँ। सुझाया गया परियोजना प्रश्न चुनें।",
  "clarify": "कृपया एक विषय और अधिकृत परियोजना चुनें। इतिहास के लिए गतिविधि चुनें; निर्णय या सीख के लिए साक्ष्य खोजें।",
  "unavailable": "निर्देशित विकल्प - AI अस्थायी रूप से अनुपलब्ध। यह वर्तमान अधिकृत साक्ष्य पर आधारित पूर्वनिर्धारित उत्तर है, AI विश्लेषण नहीं।",
  "checked": "डेटा जाँच: {timestamp}। दायरा: {scope}। {count} साक्ष्य रिकॉर्ड; आंशिक पृष्ठ: {partial}।",
  "pending": "{project} में {count} अपडेट PM समीक्षा की प्रतीक्षा में हैं। PM समीक्षा तक रिपोर्ट की प्रगति अपुष्ट है।",
  "data": "{project} के वर्तमान अधिकृत {topic} साक्ष्य नीचे हैं। अनुपलब्ध मान UNKNOWN हैं; ये रिकॉर्ड कारण या भविष्य की तारीख सिद्ध नहीं करते।",
  "empty": "कोई संबंधित अधिकृत रिकॉर्ड नहीं मिला। इससे काम, निर्णय या सीख होने का प्रमाण नहीं मिलता।",
  "submit_help": "टीम लीडर कार्यक्षेत्र में Field Updates / Add field update खोलें। गतिविधि, स्थान, तारीख और देखी गई प्रगति लिखें। साक्ष्य जमा करें; नियम-आधारित मैच सुझाव देता है और PM वास्तविक प्रगति की पुष्टि करता है।",
  "review_help": "नियुक्त PM Planner Review में फील्ड साक्ष्य और मैच जाँचता है, फिर पुष्टि, मैच बदलाव, अनमैच या जानकारी माँगता है। केवल PM पुष्टि वास्तविक प्रगति में जुड़ती है। सहायक समीक्षा या मंजूरी नहीं देता।",
  "evidence_help": "गतिविधि कोड, स्थान, देखी गई तारीख, प्रगति और फील्ड साक्ष्य दें। आयातित बेसलाइन और PM-पुष्ट वास्तविक प्रगति अलग हैं। वर्तमान स्वास्थ्य अकेले ऐतिहासिक गिरावट या कारण सिद्ध नहीं करता।",
  "provider_help": "संचालक backend पर Groq/NVIDIA कुंजी और संगत मॉडल सेट करके पुनः शुरू करता है। बिना कुंजी निर्देशित उत्तर उपलब्ध हैं। गोपनीय कुंजी चैट में न डालें। कोटा और पहुँच प्रदाता तय करता है।",
 },
 "hi-Latn": {
  "scope": "Main authorized PRAVAHA projects, schedule, field kaam, reviews, warnings aur memory samjhata hoon. Suggested project sawal chunein.",
  "clarify": "Ek topic aur authorized project chunein. Timeline ke liye activity chunein; decisions ya lessons ke liye evidence search karein.",
  "unavailable": "Guided fallback - AI abhi uplabdh nahi hai. Yeh current authorized evidence se bana predefined jawab hai, AI analysis nahi.",
  "checked": "Data check: {timestamp}. Scope: {scope}. {count} evidence records; partial page: {partial}.",
  "pending": "{project} mein {count} updates PM review ka intezar kar rahe hain. PM review tak reported progress confirmed nahi hai.",
  "data": "{project} ka current authorized {topic} evidence neeche hai. Missing values UNKNOWN hain; records cause ya future date prove nahi karte.",
  "empty": "Koi matching authorized record nahi mila. Isse kaam, decision ya lesson hone ka saboot nahi milta.",
  "submit_help": "Team Leader workspace mein Field Updates / Add field update kholein. Activity, location, date aur observed progress likhein. Evidence submit karein; deterministic matcher link suggest karta hai aur PM actuals confirm karta hai.",
  "review_help": "Assigned PM Planner Review mein field evidence aur match dekhta hai, phir confirm, match change, unmatch ya information request karta hai. Sirf PM confirmation authoritative actual progress banata hai. Assistant approve nahi karta.",
  "evidence_help": "Activity code, location, observed date, progress aur field evidence dein. Imported baseline aur PM-confirmed actual alag hain. Current health se historical decline ya cause prove nahi hota.",
  "provider_help": "Operator backend mein Groq/NVIDIA key aur compatible model configure karke restart kare. Bina key guided answers milte hain. Secrets chat mein na daalein. Provider account quota aur access control karta hai.",
 },
}

TOPICS = {
 "en": {"overview":"project overview", "delayed":"delayed activities", "risk":"at-risk activities", "warnings":"execution warnings", "variance":"progress and variance", "health":"health and recorded history", "changes":"recent changes", "dependencies":"dependency exposure", "timeline":"activity timeline", "memory":"institutional memory", "assigned":"assigned work"},
 "hi": {"overview":"परियोजना सारांश", "delayed":"विलंबित गतिविधियाँ", "risk":"जोखिम वाली गतिविधियाँ", "warnings":"चेतावनियाँ", "variance":"प्रगति और विचलन", "health":"स्वास्थ्य और दर्ज इतिहास", "changes":"हाल के बदलाव", "dependencies":"निर्भरता प्रभाव", "timeline":"गतिविधि इतिहास", "memory":"संस्थागत स्मृति", "assigned":"सौंपा गया काम"},
 "hi-Latn": {"overview":"project summary", "delayed":"delay wala kaam", "risk":"risk wali activities", "warnings":"warnings", "variance":"progress aur variance", "health":"health aur recorded history", "changes":"haal ke badlav", "dependencies":"dependency impact", "timeline":"activity history", "memory":"project memory", "assigned":"assigned kaam"},
}


def detect_language(question, default):
    if re.search(r"[\u0900-\u097f]", question):
        return "hi"
    if re.search(r"\b(kaunsi|kaunse|kaun|kaise|kaisa|hain|hai|kya|meri|mera|rahi|rahe|baaki|baki|sawal|hafte|bhai|batao|mujhe|hoon|chahiye|chal|dekhna|samjhao|shukriya|namaste)\b", question, re.I):
        return "hi-Latn"
    if re.search(r"\b(which|what|show|explain|project|status|activities|progress|warnings|thanks|hello|good|how|tell|can|please)\b", question, re.I) and not re.fullmatch(r"(?:hi|hey|hello|thanks?(?: you)?|ok(?:ay)?|nice|great)[!?.\s]*(?:bro)?[!?.\s]*", question, re.I):
        return "en"
    return default


def recognize(question, requested=None, previous=None):
    if requested:
        return requested if requested in CATALOGUE else "clarify"
    if question.lower().startswith("search:"):
        return "memory"
    if re.search(CATALOGUE["dialogue"]["aliases"], question, re.I):
        return "dialogue"
    if re.fullmatch(r"(?:tell me more|explain (?:that|more)|why(?: is that)?|and (?:now|what next)|what next|aur batao|aur samjhao|kyun)[?!.\s]*", question, re.I) and previous in CATALOGUE:
        return previous
    matches = [key for key, item in CATALOGUE.items() if re.search(item["aliases"], question, re.I)]
    if "priorities" in matches:
        return "priorities"
    if re.search(r"project.*(?:status|scene|haal|sthiti)|(?:current|today.s|30.second).*brief|execution summary|परियोजना.*(?:स्थिति|हाल)|प्रोजेक्ट.*(?:स्थिति|हाल)", question, re.I):
        return "overview"
    if re.search(r"कौन.*(?:देर|विलंब)|गतिविध.*(?:देर|विलंब)", question):
        return "delayed"
    if re.search(r"चेतावनी|ध्यान", question):
        return "warnings"
    help_matches = [m for m in matches if m.endswith("_help")]
    if help_matches:
        return help_matches[0] if len(help_matches) == 1 else "clarify"
    if "changes" in matches and "health" in matches:
        return "health"
    if "risk" in matches and "delayed" in matches:
        return "risk"
    if matches:
        return matches[0] if len(matches) == 1 else "clarify"
    if re.match(r"^(?:and |also |what about |can you (?:expand|explain) (?:on )?(?:that|these|those))", question, re.I) and previous in CATALOGUE:
        return previous
    return "overview" if re.search(r"\b(?:project|pravaha|schedule|execution|field|wbs|activity|activities|team|review|baseline|data|work)\b|परियोजना|प्रोजेक्ट|कार्य|काम", question, re.I) else "scope"


def policy_boundary(question):
    """Server policy before context retrieval; user intent hints cannot bypass it."""
    if re.search(r"(?:\.?env\b|api[_ -]?key|jwt[_ -]?secret|session[_ -]?(?:secret|token)|database[_ -]?(?:password|url|credential|config)|connection string|password|credentials?|hidden prompt|system (?:prompt|instructions)|source (?:code|files)|backend (?:code|files)|server (?:details|config)|internal (?:implementation|infrastructure|authorization|prompt|instructions|rules)|private (?:employee|code)|secrets?|stack trace|deployment config|(?:print|reveal|repeat|dump).*(?:instructions|prompt|keys|rules|configuration))", question, re.I):
        return "private"
    if re.search(r"\b(?:cricket|football|match winner|weather|love letter|romantic|poem|recipe|movie|song|politic|bitcoin|stock price|medical advice|diagnos|celebrity|horoscope)\b", question, re.I):
        return "scope"
    return None


def fallback(intent, language, tools, context):
    t = TEXT[language]
    project = context["projectName"] or context["organizationName"]
    if intent in {"scope", "clarify", "dialogue", "private"}:
        messages = {
            "en": {"private": "I can explain PRAVAHA features at a high level, but I cannot reveal secrets, private credentials, code or internal configuration.", "scope": f"I'm your PRAVAHA project assistant. I can help with {project}'s progress, assigned work, reviews, warnings and dependencies. What would you like to check?", "clarify": f"What would you like to explore in {project}: progress, delays, reviews, warnings or dependencies?", "dialogue": f"Hi! I'm your PRAVAHA project assistant for {project}. AI is unavailable right now, but project guidance is available below."},
            "hi-Latn": {"private": "Main PRAVAHA features samjha sakta hoon, lekin secrets, private credentials, code ya internal configuration nahi dikha sakta.", "scope": f"Main PRAVAHA project assistant hoon. {project} ka progress, assigned kaam, reviews, warnings aur dependencies check karne mein help kar sakta hoon. Kya dekhna hai?", "clarify": f"{project} mein kya dekhna hai: progress, delays, reviews, warnings ya dependencies?", "dialogue": f"Hi! Main {project} ka PRAVAHA project assistant hoon. AI abhi available nahi hai, lekin project guidance neeche mil sakti hai."},
            "hi": {"private": "मैं PRAVAHA सुविधाएँ समझा सकता हूँ, लेकिन रहस्य, निजी प्रमाण-पत्र, कोड या आंतरिक कॉन्फ़िगरेशन नहीं दिखा सकता।", "scope": f"मैं PRAVAHA परियोजना सहायक हूँ। {project} की प्रगति, कार्य, समीक्षा, चेतावनी और निर्भरता समझने में मदद कर सकता हूँ। क्या देखना चाहेंगे?", "clarify": f"{project} में क्या देखना चाहेंगे: प्रगति, विलंब, समीक्षा, चेतावनी या निर्भरता?", "dialogue": f"नमस्ते! मैं {project} का PRAVAHA परियोजना सहायक हूँ। AI अभी उपलब्ध नहीं है, लेकिन परियोजना मार्गदर्शन नीचे उपलब्ध है।"},
        }
        return messages[language][intent]
    if intent in {"scope", "clarify"} or intent.endswith("_help"):
        return t[intent]
    records = [r for tool in tools for r in tool["records"]]
    if not records:
        return t["empty"]
    if intent == "pending":
        summary = next((r["data"] for r in records if r["kind"] == "pending_summary"), None)
        if summary is not None:
            return t["pending"].format(count=summary["pendingReviewCount"], project=project)
    return t["data"].format(project=project, topic=TOPICS[language].get(intent, intent))
