export const languages = { en: "English", hi: "हिन्दी" };
export const modernLabels = {
  en: { project: "Project", activity: "Activity", welcome: "Where should we focus?", intro: "Review execution, spot pending decisions, or explore the evidence behind your project.", more: "More", less: "Less", guidance: "Project guidance", unavailable: "AI response unavailable right now. You can still use the project guidance below.", retry: "Try again", notes: "Notes & next steps", thinking: "Analyzing project data…", send: "Send", enter: "Enter to send · Shift+Enter for a new line", chips: { overview: "Overview", delayed: "Delayed activities", pending: "Pending reviews", warnings: "Warnings", health: "Health change", changes: "This week", dependencies: "Dependencies", variance: "Progress & variance", submit_help: "Submit an update", review_help: "PM review" } },
  hi: { project: "परियोजना", activity: "गतिविधि", welcome: "किस विषय पर ध्यान दें?", intro: "काम की स्थिति, लंबित निर्णय और परियोजना के प्रमाण देखें।", more: "और", less: "कम", guidance: "परियोजना मार्गदर्शन", unavailable: "AI उत्तर अभी उपलब्ध नहीं है। नीचे परियोजना मार्गदर्शन देख सकते हैं।", retry: "फिर प्रयास करें", notes: "सीमाएँ और अगले कदम", thinking: "परियोजना डेटा का विश्लेषण…", send: "भेजें", enter: "Enter से भेजें · Shift+Enter से नई पंक्ति", chips: { overview: "सारांश", delayed: "विलंबित गतिविधियाँ", pending: "लंबित समीक्षा", warnings: "चेतावनियाँ", health: "स्वास्थ्य बदलाव", changes: "इस सप्ताह", dependencies: "निर्भरताएँ", variance: "प्रगति और अंतर", submit_help: "अपडेट जमा करें", review_help: "PM समीक्षा" } },
  "hi-Latn": { project: "Project", activity: "Activity", welcome: "Kis par dhyan dein?", intro: "Execution, pending decisions aur project evidence dekhein.", more: "Aur", less: "Kam", guidance: "Project guidance", unavailable: "AI jawab abhi available nahi hai. Neeche project guidance dekh sakte hain.", retry: "Phir koshish", notes: "Notes aur agle kadam", thinking: "Project data samajh rahe hain…", send: "Send", enter: "Enter se bhejein · Shift+Enter se nayi line", chips: { overview: "Overview", delayed: "Delay wala kaam", pending: "Pending reviews", warnings: "Warnings", health: "Health badlav", changes: "Is hafte", dependencies: "Dependencies", variance: "Progress aur variance", submit_help: "Update submit karein", review_help: "PM review" } },
};
export const detailLabels = {
  en: { activity: "Activity (optional)", all: "All authorized activities", more: "Load more projects" },
  hi: { activity: "गतिविधि (वैकल्पिक)", all: "सभी अधिकृत गतिविधियाँ", more: "और परियोजनाएँ" },
  "hi-Latn": { activity: "Activity (optional)", all: "Sab authorized activities", more: "Aur projects" },
};
export const catalogue = {
  en: { title: "Project assistant", open: "Open PRAVAHA project assistant", close: "Minimize project assistant", context: "Assistant context", language: "Language", question: "Project question", placeholder: "Ask about authorized project evidence", send: "Ask", cancel: "Cancel", retry: "Retry", reset: "New conversation", source: "Open source", ai: "AI answer", fallback: "Guided fallback - AI temporarily unavailable", thinking: "Retrieving evidence and requesting an explanation…", staticHelp: "Static help only: submit a field update with activity, location, date and observed progress. Your PM reviews and confirms actuals. Current project data is unavailable while the backend cannot be reached.", disabled: "External AI is disabled or not configured. Current authorized evidence and guided answers remain available.", sources: "Current authorized evidence", checked: "Data checked", partial: "Partial evidence page", cancelled: "Request cancelled.", greeting: "Ask about your project.", choose: "Choose a project", organization: "Organization summary", expired: "Session or access changed. Conversation cleared; sign in or select your current assignment.", interpretation: "AI interpretation — validate decisions against the source records." },
  hi: { title: "परियोजना सहायक", open: "PRAVAHA परियोजना सहायक खोलें", close: "सहायक छोटा करें", context: "सहायक का दायरा", language: "भाषा", question: "परियोजना प्रश्न", placeholder: "अधिकृत परियोजना साक्ष्य के बारे में पूछें", send: "पूछें", cancel: "रद्द करें", retry: "फिर प्रयास", reset: "नई बातचीत", source: "स्रोत खोलें", ai: "AI उत्तर", fallback: "निर्देशित विकल्प - AI अस्थायी रूप से अनुपलब्ध", thinking: "साक्ष्य और व्याख्या प्राप्त हो रहे हैं…", staticHelp: "केवल स्थिर सहायता: गतिविधि, स्थान, तारीख और देखी गई प्रगति के साथ फील्ड अपडेट जमा करें। PM समीक्षा और पुष्टि करता है। backend से संपर्क नहीं होने पर वर्तमान परियोजना डेटा अनुपलब्ध है।", disabled: "बाहरी AI बंद या कॉन्फ़िगर नहीं है। वर्तमान अधिकृत साक्ष्य और निर्देशित उत्तर उपलब्ध हैं।", sources: "वर्तमान अधिकृत साक्ष्य", checked: "डेटा जाँच", partial: "आंशिक साक्ष्य पृष्ठ", cancelled: "अनुरोध रद्द हुआ।", greeting: "अपनी परियोजना के बारे में पूछें।", choose: "परियोजना चुनें", organization: "संस्था सारांश", expired: "सत्र या पहुँच बदली है। बातचीत मिटाई गई; साइन इन करें या वर्तमान कार्य चुनें।", interpretation: "AI व्याख्या — निर्णय से पहले स्रोत रिकॉर्ड जाँचें।" },
  "hi-Latn": { title: "Project sahayak", open: "PRAVAHA project sahayak kholein", close: "Sahayak minimize karein", context: "Assistant ka scope", language: "Bhasha", question: "Project sawal", placeholder: "Authorized project evidence ke baare mein poochein", send: "Poochein", cancel: "Cancel", retry: "Phir koshish", reset: "Nayi baat", source: "Source kholein", ai: "AI jawab", fallback: "Guided fallback - AI abhi uplabdh nahi hai", thinking: "Evidence aur explanation aa rahe hain…", staticHelp: "Sirf static help: activity, location, date aur observed progress ke saath field update submit karein. PM review aur confirm karta hai. Backend unavailable hone par current project data nahi mil sakta.", disabled: "External AI disabled ya configured nahi hai. Current authorized evidence aur guided answers available hain.", sources: "Current authorized evidence", checked: "Data check", partial: "Partial evidence page", cancelled: "Request cancel hua.", greeting: "Apne project ka sawal poochein.", choose: "Project chunein", organization: "Organization summary", expired: "Session ya access badla. Conversation clear hui; sign in ya current assignment chunein.", interpretation: "AI interpretation — decisions se pehle source records dekhein." },
};
export const suggestions = {
  en: [["overview", "Show the project overview"], ["delayed", "Which activities are delayed?"], ["pending", "Which updates await PM review?"], ["warnings", "What warnings require attention?"], ["health", "Why has project health changed?"], ["changes", "What changed this week?"], ["dependencies", "Explain dependency exposure"], ["variance", "Show current progress and variance"], ["submit_help", "How do I submit a field update?"], ["review_help", "Explain the PM review process"]],
  hi: [["overview", "परियोजना का सारांश दिखाएँ"], ["delayed", "कौन सी गतिविधियाँ विलंबित हैं?"], ["pending", "कौन से अपडेट PM समीक्षा की प्रतीक्षा में हैं?"], ["warnings", "किन चेतावनियों पर ध्यान चाहिए?"], ["health", "परियोजना का स्वास्थ्य क्यों बदला?"], ["changes", "इस सप्ताह क्या बदला?"], ["dependencies", "निर्भरता प्रभाव समझाएँ"], ["variance", "वर्तमान प्रगति और विचलन दिखाएँ"], ["submit_help", "फील्ड अपडेट कैसे जमा करें?"], ["review_help", "PM समीक्षा प्रक्रिया समझाएँ"]],
  "hi-Latn": [["overview", "Project ka overview dikhao"], ["delayed", "Kaunsi activities delay ho rahi hain?"], ["pending", "Kaun se updates PM review ke liye baaki hain?"], ["warnings", "Kaunsi warnings par dhyan dena hai?"], ["health", "Project health kyun badla?"], ["changes", "Is hafte kya badla?"], ["dependencies", "Dependency impact samjhao"], ["variance", "Current progress aur variance dikhao"], ["submit_help", "Field update kaise submit karun?"], ["review_help", "PM review process samjhao"]],
};

export const conversationLabels = {
  en: { welcome: "Hey", intro: "Your project companion. What should we check?", more: "More suggestions", less: "Fewer suggestions", assistant: "PRAVAHA assistant", unavailable: "Looks like the AI services are unavailable right now.", useGuidance: "Use project guidance", copy: "Copy response", copied: "Copied", copyFailed: "Couldn't copy this response. Select the text to copy it.", thinking: "Checking authorized project data…", sourceLoading: "Checking the source…", preference: "Language preference", auto: "Auto" },
  hi: { welcome: "नमस्ते", intro: "आपका परियोजना साथी। क्या देखना चाहेंगे?", more: "और सुझाव", less: "कम सुझाव", assistant: "PRAVAHA सहायक", unavailable: "AI सेवाएँ अभी उपलब्ध नहीं हैं।", useGuidance: "परियोजना मार्गदर्शन देखें", copy: "उत्तर कॉपी करें", copied: "कॉपी हुआ", copyFailed: "उत्तर कॉपी नहीं हुआ। पाठ चुनकर कॉपी करें।", thinking: "अधिकृत परियोजना डेटा देख रहे हैं…", sourceLoading: "स्रोत जाँच रहे हैं…", preference: "भाषा की पसंद", auto: "अपने आप" },
  "hi-Latn": { welcome: "Hey", intro: "Aapka project companion. Kya check karein?", more: "Aur suggestions", less: "Kam suggestions", assistant: "PRAVAHA assistant", unavailable: "AI services abhi available nahi hain.", useGuidance: "Project guidance dekhein", copy: "Jawab copy karein", copied: "Copy hua", copyFailed: "Jawab copy nahi hua. Text select karke copy karein.", thinking: "Authorized project data check kar rahe hain…", sourceLoading: "Source check kar rahe hain…", preference: "Bhasha ki pasand", auto: "Auto" },
};

const roleIntents = {
  PROJECT_MANAGER: ["overview", "delayed", "pending", "warnings", "priorities", "health", "variance", "dependencies", "changes", "review_help"],
  TEAM_LEADER: ["overview", "pending", "submit_help", "warnings", "changes", "delayed", "variance", "dependencies"],
  ADMIN: ["overview", "health", "warnings", "changes", "variance", "dependencies", "priorities"],
};
const contextualPrompts = {
  en: {
    overview: ["What's the current project status?", "Current status"],
    priorities: ["Give me a concise project brief based on current execution evidence", "Project brief"],
    changes: ["What changed in the latest execution updates?", "Latest changes"],
    dialogue: ["What can you help me with in PRAVAHA?", "What can you do?"],
    organization: ["Show my authorized organization and project overview", "Organization overview"],
    team_overview: ["Summarize my team's assigned activities and execution status", "Assigned activities"],
    team_pending: ["Which of my team's updates await PM review or feedback?", "Pending updates"],
    team_changes: ["What changed in my team's latest execution updates?", "Latest team updates"],
  },
  hi: {
    overview: ["परियोजना की वर्तमान स्थिति बताइए", "वर्तमान स्थिति"],
    priorities: ["वर्तमान कार्य साक्ष्य के आधार पर परियोजना का संक्षिप्त सार बताइए", "संक्षिप्त सार"],
    changes: ["हाल के काम के अपडेट में क्या बदला?", "हाल के बदलाव"],
    dialogue: ["PRAVAHA में आप मेरी क्या मदद कर सकते हैं?", "आप क्या कर सकते हैं?"],
    organization: ["मेरे अधिकृत संगठन और परियोजनाओं का सार बताइए", "संगठन सार"],
    team_overview: ["मेरी टीम की सौंपे गए गतिविधियों और काम की स्थिति बताइए", "सौंपे गए काम"],
    team_pending: ["मेरी टीम के कौन से अपडेट PM समीक्षा या फ़ीडबैक के लिए लंबित हैं?", "लंबित अपडेट"],
    team_changes: ["मेरी टीम के हाल के काम के अपडेट में क्या बदला?", "टीम के हाल के अपडेट"],
  },
  "hi-Latn": {
    overview: ["Project ka current status kya hai?", "Current status"],
    priorities: ["Current execution evidence ke hisaab se ek short project brief do", "Project brief"],
    changes: ["Latest execution updates mein kya badla?", "Latest changes"],
    dialogue: ["PRAVAHA mein meri kya help kar sakte ho?", "Kya help kar sakte ho?"],
    organization: ["Mere authorized organization aur projects ka overview dikhao", "Organization overview"],
    team_overview: ["Meri team ki assigned activities aur execution status batao", "Assigned activities"],
    team_pending: ["Meri team ke kaunse updates PM review ya feedback ke liye pending hain?", "Pending updates"],
    team_changes: ["Meri team ke latest execution updates mein kya badla?", "Latest team updates"],
  },
};

export function getSuggestions(role, language, projectId) {
  const localized = suggestions[language] || suggestions.en;
  const labels = modernLabels[language] || modernLabels.en;
  const prompts = contextualPrompts[language] || contextualPrompts.en;
  if (role === "ADMIN" && !projectId) return [["overview", ...prompts.organization], ["dialogue", ...prompts.dialogue]];
  return (roleIntents[role] || []).map((intent) => {
    const teamKey = role === "TEAM_LEADER" && ["overview", "pending", "changes"].includes(intent) ? `team_${intent}` : null;
    return [intent, ...(prompts[teamKey || intent] || [localized.find(([key]) => key === intent)[1], labels.chips[intent]])];
  });
}
