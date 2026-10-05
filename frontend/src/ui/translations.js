// Local interface copy only. Project records and assistant answers remain source content.
const messages = {
  "Secure account access": ["सुरक्षित खाते तक पहुँच", "Surakshit account access"],
  "Project Progress Monitoring System": ["परियोजना प्रगति निगरानी प्रणाली", "Project progress monitoring system"],
  "Connect field execution with project schedules and actual progress.": ["फ़ील्ड निष्पादन को परियोजना शेड्यूल और वास्तविक प्रगति से जोड़ें।", "Field execution ko project schedule aur actual progress se jodein."],
  "Get access through your organization administrator.": ["अपने संगठन के प्रशासक से पहुँच प्राप्त करें।", "Apne organization administrator se access paayein."],
  "Or continue with email": ["या ईमेल से जारी रखें", "Ya email se jaari rakhein"],
  "Continue with Google": ["Google से जारी रखें", "Google se jaari rakhein"],
  "Continue with GitHub": ["GitHub से जारी रखें", "GitHub se jaari rakhein"],
  "Schedule links": ["शेड्यूल लिंक", "Schedule links"],
  "Language": ["भाषा", "Bhasha"],
  "BRIDGING PLANNING AND EXECUTION": ["योजना और कार्यान्वयन को जोड़ते हुए", "Planning aur execution ko jodein"],
  "Field data capture and deterministic schedule linking for real-time infrastructure project progress tracking.": ["अवसंरचना परियोजनाओं की वास्तविक समय प्रगति के लिए फ़ील्ड डेटा संग्रह और नियम-आधारित कार्यसूची लिंक।", "Infrastructure projects ki real-time progress ke liye field data capture aur rule-based schedule linking."],
  "Data capture": ["डेटा संग्रह", "Data capture"],
  "Activity extraction": ["गतिविधि पहचान", "Activity extraction"],
  "L5/L6 schedule matching": ["L5/L6 कार्यसूची मिलान", "L5/L6 schedule matching"],
  "Actual progress": ["वास्तविक प्रगति", "Actual progress"],
  "Project intelligence": ["परियोजना अंतर्दृष्टि", "Project intelligence"],
  "Back to sign in": ["साइन इन पर वापस जाएँ", "Sign in par wapas jaayein"],
  "Transforming Infrastructure": ["अवसंरचना का बेहतर", "Infrastructure ka behtar"],
  "Project Management": ["परियोजना प्रबंधन", "Project management"],
  "with Field Data": ["फ़ील्ड डेटा के साथ", "Field data ke saath"],
  "A prototype view of field updates and schedule links. The figures shown here are illustrative demo values.": ["फ़ील्ड अपडेट और कार्यसूची लिंक का प्रोटोटाइप दृश्य। यहाँ दिखाए गए आँकड़े केवल डेमो उदाहरण हैं।", "Field updates aur schedule links ka prototype. Ye aankde sirf demo examples hain."],
  "Built for Site Teams, Planners & Project Stakeholders": ["साइट टीमों, योजनाकारों और परियोजना हितधारकों के लिए", "Site teams, planners aur project stakeholders ke liye"],
  "Illustrative demo progress": ["प्रगति का डेमो उदाहरण", "Progress ka demo example"],
  "Illustrative demo count": ["गिनती का डेमो उदाहरण", "Count ka demo example"],
  "Illustrative value, not measured accuracy": ["उदाहरण मान, मापी गई सटीकता नहीं", "Example value, measured accuracy nahi"],
  "Supervisor descriptions and progress": ["पर्यवेक्षक विवरण और प्रगति", "Supervisor details aur progress"],
  "Activities": ["गतिविधियाँ", "Activities"],
  "Overall Progress": ["कुल प्रगति", "Overall progress"],
  "Activities Tracked": ["ट्रैक की गई गतिविधियाँ", "Tracked activities"],
  "Demo Matching Score": ["डेमो मिलान स्कोर", "Demo matching score"],
  "Unmatched Items": ["बिना मिलान के रिकॉर्ड", "Unmatched items"],
  "Demo Project Overview": ["डेमो परियोजना सारांश", "Demo project overview"],
  "All Disciplines": ["सभी कार्य विभाग", "Sabhi disciplines"],
  "Last 30 Days": ["पिछले 30 दिन", "Pichhle 30 din"],
  "Schedule Progress (L5/L6)": ["कार्यसूची प्रगति (L5/L6)", "Schedule progress (L5/L6)"],
  "Today": ["आज", "Aaj"],
  "Recent Activity Updates": ["हाल के गतिविधि अपडेट", "Haal ke activity updates"],
  "View All →": ["सभी देखें →", "Sab dekhein →"],
  "Matched": ["मिलान हुआ", "Matched"],
  "Unmatched activity - Review required": ["गतिविधि का मिलान नहीं हुआ — समीक्षा आवश्यक", "Activity unmatched — review zaroori"],
  "Field Update Capture": ["फ़ील्ड अपडेट दर्ज करें", "Field update capture"],
  "Record field observations and progress details in a persistent project workflow.": ["परियोजना में फ़ील्ड अवलोकन और प्रगति विवरण सहेजें।", "Project workflow mein field observations aur progress details save karein."],
  "Deterministic Activity Linking": ["नियम-आधारित गतिविधि लिंक", "Rule-based activity linking"],
  "Fixed prototype rules suggest an L5/L6 schedule activity with a confidence score for Project Manager review.": ["निर्धारित प्रोटोटाइप नियम प्रबंधक समीक्षा के लिए विश्वास स्कोर सहित L5/L6 गतिविधि सुझाते हैं।", "Prototype rules PM review ke liye confidence score ke saath L5/L6 activity suggest karte hain."],
  "Schedule Reconciliation": ["कार्यसूची समायोजन", "Schedule reconciliation"],
  "Project Manager confirmation links field dates and progress to the schedule with an audit trail.": ["परियोजना प्रबंधक की पुष्टि फ़ील्ड तिथियों और प्रगति को ऑडिट रिकॉर्ड के साथ कार्यसूची से जोड़ती है।", "PM confirmation field dates aur progress ko audit trail ke saath schedule se jodti hai."],
  "Review Execution Patterns": ["कार्य पैटर्न की समीक्षा", "Execution patterns dekhein"],
  "Explore illustrative patterns from demo records. Verify project sources and dates before reusing them.": ["डेमो रिकॉर्ड के उदाहरण पैटर्न देखें। दोबारा उपयोग से पहले परियोजना स्रोत और तिथियाँ जाँचें।", "Demo records ke patterns dekhein. Reuse se pehle project sources aur dates check karein."],
  "BUILT FOR INFRASTRUCTURE PROJECT TEAMS": ["अवसंरचना परियोजना टीमों के लिए", "Infrastructure project teams ke liye"],
  "Turn field progress into": ["फ़ील्ड प्रगति को बदलें", "Field progress ko badlein"],
  "schedule intelligence.": ["कार्यसूची अंतर्दृष्टि में।", "Schedule intelligence mein."],
  "Capture. Understand. Link. Update.": ["दर्ज करें। समझें। जोड़ें। अपडेट करें।", "Capture. Samjhein. Jodein. Update karein."],
  "Build a smarter execution history with Pravaha.": ["Pravaha के साथ उपयोगी कार्य इतिहास बनाएँ।", "Pravaha ke saath behtar execution history banayein."],
  "Try Pravaha Prototype": ["Pravaha प्रोटोटाइप आज़माएँ", "Pravaha prototype try karein"],
  "Explore Dashboard": ["डैशबोर्ड देखें", "Dashboard dekhein"],
  "From Field Updates": ["फ़ील्ड अपडेट", "Field updates"],
  "to": ["से", "se"],
  "Smarter Schedules": ["बेहतर कार्यसूची तक", "Behtar schedules tak"],
  "Field data capture and deterministic schedule linking for": ["फ़ील्ड डेटा और नियम-आधारित कार्यसूची लिंक के साथ", "Field data capture aur rule-based schedule linking se"],
  "persistent infrastructure project progress tracking.": ["अवसंरचना परियोजना प्रगति की निरंतर निगरानी।", "Infrastructure project progress ki persistent tracking."],
  "Rule-Based Activity Matching": ["नियम-आधारित गतिविधि मिलान", "Rule-based activity matching"],
  "Persistent Schedule Updates": ["सहेजे गए कार्यसूची अपडेट", "Persistent schedule updates"],
  "Institutional Knowledge": ["संस्थागत ज्ञान", "Institutional knowledge"],
  "Try Prototype": ["प्रोटोटाइप आज़माएँ", "Prototype try karein"],
  "Watch Demo": ["डेमो देखें", "Demo dekhein"],
  "HOW PRAVAHA WORKS": ["PRAVAHA कैसे काम करता है", "PRAVAHA kaise kaam karta hai"],
  "From Site Data to": ["साइट डेटा से", "Site data se"],
  "Schedule Intelligence": ["कार्यसूची अंतर्दृष्टि", "Schedule intelligence"],
  "Pravaha connects fragmented field updates with the project schedule through a simple intelligent workflow.": ["Pravaha एक सरल कार्यप्रवाह से अलग-अलग फ़ील्ड अपडेट को परियोजना कार्यसूची से जोड़ता है।", "Pravaha simple workflow se field updates ko project schedule se jodta hai."],
  "Capture": ["दर्ज करें", "Capture karein"],
  "Record supervisor observations and progress as text updates in the project workspace.": ["परियोजना कार्यक्षेत्र में पर्यवेक्षक अवलोकन और प्रगति को टेक्स्ट अपडेट के रूप में दर्ज करें।", "Project workspace mein supervisor observations aur progress text mein record karein."],
  "Understand": ["समझें", "Samjhein"],
  "Prototype rules suggest activity, discipline and location for supported field descriptions.": ["प्रोटोटाइप नियम समर्थित फ़ील्ड विवरण के लिए गतिविधि, कार्य विभाग और स्थान सुझाते हैं।", "Prototype rules supported descriptions ke liye activity, discipline aur location suggest karte hain."],
  "Link": ["जोड़ें", "Jodein"],
  "Deterministic suggestions connect field descriptions to L5/L6 schedule activities for Project Manager confirmation.": ["नियम-आधारित सुझाव प्रबंधक पुष्टि के लिए फ़ील्ड विवरण को L5/L6 कार्यसूची गतिविधियों से जोड़ते हैं।", "Rule-based suggestions PM confirmation ke liye field descriptions ko L5/L6 activities se jodte hain."],
  "Update": ["अपडेट करें", "Update karein"],
  "Actual progress is reflected back into the schedule while maintaining an audit trail for every update.": ["हर अपडेट का ऑडिट रिकॉर्ड रखते हुए वास्तविक प्रगति कार्यसूची में दिखाई जाती है।", "Har update ka audit trail rakhte hue actual progress schedule mein dikhti hai."],
  "Match": ["मिलान", "Match"],
  "ONE PLATFORM. MULTIPLE DISCIPLINES.": ["एक प्लैटफ़ॉर्म। अनेक कार्य विभाग।", "Ek platform. Kai disciplines."],
  "Connect every part of": ["हर भाग को जोड़ें", "Har hissa jodein"],
  "project execution.": ["परियोजना कार्य का।", "Project execution ka."],
  "Different engineering teams describe progress in different ways. Pravaha creates a common layer between field language and structured project schedules.": ["अलग इंजीनियरिंग टीमें प्रगति को अलग तरह से बताती हैं। Pravaha फ़ील्ड की भाषा और संरचित कार्यसूची के बीच एक साझा कड़ी बनाता है।", "Engineering teams progress alag tarah batati hain. Pravaha field language aur structured schedules ke beech common link banata hai."],
  "Activity Intelligence": ["गतिविधि अंतर्दृष्टि", "Activity intelligence"],
  "Illustrative matching overview": ["मिलान का उदाहरण सारांश", "Matching ka demo overview"],
  "DEMO": ["डेमो", "Demo"],
  "15 activities require review": ["15 गतिविधियों की समीक्षा आवश्यक", "15 activities ka review zaroori"],
  "New or unmatched field descriptions": ["नए या बिना मिलान के फ़ील्ड विवरण", "Naye ya unmatched field descriptions"],
  "Review →": ["समीक्षा →", "Review →"],
  "PROJECT KNOWLEDGE": ["परियोजना ज्ञान", "Project knowledge"],
  "Every completed activity becomes": ["हर पूरी गतिविधि बनती है", "Har completed activity banti hai"],
  "reusable knowledge.": ["पुनः उपयोग योग्य ज्ञान।", "Reusable knowledge."],
  "Explore illustrative execution patterns from demo data. These example figures are not measured project results.": ["डेमो डेटा के कार्य पैटर्न देखें। ये उदाहरण आँकड़े मापे गए परियोजना परिणाम नहीं हैं।", "Demo data ke execution patterns dekhein. Ye examples measured project results nahi hain."],
  "Actual Durations": ["वास्तविक अवधि", "Actual durations"],
  "Understand how long activities actually took compared with the baseline schedule.": ["समझें कि मूल कार्यसूची की तुलना में गतिविधियों में वास्तव में कितना समय लगा।", "Baseline schedule ke muqable activities mein kitna samay laga, samjhein."],
  "Average actual duration": ["औसत वास्तविक अवधि", "Average actual duration"],
  "Recurring Delay Causes": ["बार-बार देरी के कारण", "Baar-baar delay ke causes"],
  "Build a structured record of recurring execution bottlenecks and delay patterns.": ["बार-बार आने वाली कार्य बाधाओं और देरी के पैटर्न का व्यवस्थित रिकॉर्ड बनाएँ।", "Recurring execution bottlenecks aur delays ka structured record banayein."],
  "Patterns identified": ["पहचाने गए पैटर्न", "Pehchane gaye patterns"],
  "Discipline Productivity": ["कार्य विभाग उत्पादकता", "Discipline productivity"],
  "Compare execution patterns across disciplines, contractors and project phases.": ["कार्य विभागों, ठेकेदारों और परियोजना चरणों के कार्य पैटर्न की तुलना करें।", "Disciplines, contractors aur project phases ke execution patterns compare karein."],
  "Productivity insight": ["उत्पादकता अंतर्दृष्टि", "Productivity insight"],
  "Home": ["होम", "Home"],
  "About": ["परिचय", "Parichay"],
  "Features": ["सुविधाएँ", "Features"],
  "Use Cases": ["उपयोग", "Upyog"],
  "Contact": ["संपर्क", "Sampark"],
  "Platform": ["प्लैटफ़ॉर्म", "Platform"],
  "Auto": ["स्वतः", "Auto"],
  "Light": ["लाइट", "Light"],
  "Dark": ["डार्क", "Dark"],
  "Switch to light mode": ["लाइट मोड चुनें", "Light mode chunein"],
  "Switch to dark mode": ["डार्क मोड चुनें", "Dark mode chunein"],
  "Sign in": ["साइन इन", "Sign in"],
  "Sign up": ["खाता बनाएँ", "Khata banayein"],
  "Sign out": ["साइन आउट", "Sign out"],
  "Signing in…": ["साइन इन हो रहा है…", "Sign in ho raha hai…"],
  "Close": ["बंद करें", "Band karein"],
  "Close sign in": ["साइन इन बंद करें", "Sign in band karein"],
  "Open navigation": ["नेविगेशन खोलें", "Navigation kholein"],
  "Close navigation": ["नेविगेशन बंद करें", "Navigation band karein"],
  "Main navigation": ["मुख्य नेविगेशन", "Main navigation"],
  "Profile": ["प्रोफ़ाइल", "Profile"],
  "Profile menu": ["प्रोफ़ाइल मेनू", "Profile menu"],
  "Profile Settings": ["प्रोफ़ाइल सेटिंग्स", "Profile settings"],
  "Settings": ["सेटिंग्स", "Settings"],
  "Help & Support": ["सहायता", "Madad aur support"],
  "Privacy": ["गोपनीयता", "Privacy"],
  "Terms": ["शर्तें", "Shartein"],
  "Connect": ["जुड़ें", "Judein"],
  "Resources": ["संसाधन", "Resources"],
  "Not configured": ["कॉन्फ़िगर नहीं है", "Configure nahi hai"],
  "Not published yet": ["अभी प्रकाशित नहीं है", "Abhi publish nahi hua"],
  "Project intelligence for infrastructure execution.": ["अवसंरचना कार्यों के लिए परियोजना अंतर्दृष्टि।", "Infrastructure execution ke liye project intelligence."],
  "SIH 2026 prototype · Synthetic demonstration data": ["SIH 2026 प्रोटोटाइप · कृत्रिम प्रदर्शन डेटा", "SIH 2026 prototype · Synthetic demo data"],
  "Management": ["प्रबंधन", "Management"],
  "Management portal": ["प्रबंधन पोर्टल", "Management portal"],
  "Team Leader / Supervisor": ["टीम लीडर / पर्यवेक्षक", "Team Leader / Supervisor"],
  "Team Leader": ["टीम लीडर", "Team Leader"],
  "Project Manager": ["परियोजना प्रबंधक", "Project Manager"],
  "Administrator": ["प्रशासक", "Administrator"],
  "Department account": ["विभागीय खाता", "Department account"],
  "Workspace": ["कार्यक्षेत्र", "Workspace"],
  "Sign in to PRAVAHA": ["PRAVAHA में साइन इन करें", "PRAVAHA mein sign in karein"],
  "Your server-assigned role and project access determine the workspace you can open.": ["आपकी निर्धारित भूमिका और परियोजना अनुमतियाँ आपका कार्यक्षेत्र तय करती हैं।", "Aapki assigned role aur project access se workspace tay hota hai."],
  "Work email or login ID": ["कार्य ईमेल या लॉगिन आईडी", "Work email ya login ID"],
  "Work email": ["कार्य ईमेल", "Work email"],
  "Password": ["पासवर्ड", "Password"],
  "Full name": ["पूरा नाम", "पूरा नाम"],
  "Confirm password": ["पासवर्ड की पुष्टि करें", "पासवर्ड की पुष्टि करें"],
  "Password strength": ["पासवर्ड की मज़बूती", "पासवर्ड की मज़बूती"],
  "Password requirements": ["पासवर्ड की आवश्यकताएँ", "पासवर्ड की आवश्यकताएँ"],
  "Weak": ["कमज़ोर", "कमज़ोर"],
  "Fair": ["ठीक", "ठीक"],
  "Good": ["अच्छा", "अच्छा"],
  "Strong": ["मज़बूत", "मज़बूत"],
  "At least 8 characters": ["कम से कम 8 अक्षर", "कम से कम 8 अक्षर"],
  "Uppercase letter": ["एक बड़ा अक्षर", "एक बड़ा अक्षर"],
  "Lowercase letter": ["एक छोटा अक्षर", "एक छोटा अक्षर"],
  "Number": ["एक संख्या", "एक संख्या"],
  "Special character": ["एक विशेष अक्षर", "एक विशेष अक्षर"],
  "Passwords match": ["पासवर्ड मेल खाते हैं", "पासवर्ड मेल खाते हैं"],
  "Passwords do not match": ["पासवर्ड मेल नहीं खाते", "पासवर्ड मेल नहीं खाते"],
  "Forgot password?": ["पासवर्ड भूल गए?", "पासवर्ड भूल गए?"],
  "Enter your full name": ["अपना पूरा नाम दर्ज करें", "अपना पूरा नाम दर्ज करें"],
  "Re-enter your password": ["पासवर्ड फिर से दर्ज करें", "पासवर्ड फिर से दर्ज करें"],
  "Create your PRAVAHA account": ["अपना PRAVAHA खाता बनाएँ", "अपना PRAVAHA खाता बनाएँ"],
  "Contact your organization administrator to create your account and assign your project or team.": ["खाता बनाने और प्रोजेक्ट या टीम सौंपने के लिए अपने संगठन व्यवस्थापक से संपर्क करें।", "खाता बनाने और प्रोजेक्ट या टीम सौंपने के लिए अपने संगठन व्यवस्थापक से संपर्क करें।"],
  "Contact your organization administrator to reset your password.": ["पासवर्ड रीसेट करने के लिए अपने संगठन व्यवस्थापक से संपर्क करें।", "पासवर्ड रीसेट करने के लिए अपने संगठन व्यवस्थापक से संपर्क करें।"],
  "Enter your password": ["अपना पासवर्ड दर्ज करें", "Apna password daalein"],
  "Show password": ["पासवर्ड दिखाएँ", "Password dikhayein"],
  "Hide password": ["पासवर्ड छिपाएँ", "Password chhupayein"],
  "Accounts are provisioned by your organization administrator.": ["आपके संगठन का प्रशासक खाते बनाता है।", "Aapki organization ka administrator accounts banata hai."],
  "Get access to PRAVAHA": ["PRAVAHA का ऐक्सेस पाएँ", "PRAVAHA ka access paayein"],
  "Contact your organization administrator to create your account and assign your project or team. Already have an account? Sign in below.": ["खाता बनाने और परियोजना या टीम का ऐक्सेस पाने के लिए अपने संगठन के प्रशासक से संपर्क करें। खाता पहले से है? नीचे साइन इन करें।", "Account banane aur project ya team access ke liye apne organization administrator se sampark karein. Account hai? Neeche sign in karein."],
  "Sign in could not be completed.": ["साइन इन पूरा नहीं हो सका।", "Sign in poora nahi ho saka."],
  "Email or password is incorrect.": ["ईमेल या पासवर्ड गलत है।", "Email ya password galat hai."],
  "Dashboard": ["डैशबोर्ड", "Dashboard"],
  "Projects": ["परियोजनाएँ", "Projects"],
  "Project": ["परियोजना", "Project"],
  "Project Managers": ["परियोजना प्रबंधक", "Project Managers"],
  "Teams": ["टीमें", "Teams"],
  "Organization": ["संगठन", "Organization"],
  "Organization Activity": ["संगठन गतिविधि", "Organization activity"],
  "Workers": ["कर्मचारी", "Workers"],
  "Assignments": ["आवंटन", "Assignments"],
  "Departments": ["विभाग", "Departments"],
  "Business": ["व्यवसाय", "Business"],
  "Materials": ["सामग्री", "Materials"],
  "People": ["लोग", "People"],
  "Quality": ["गुणवत्ता", "Quality"],
  "HSE": ["स्वास्थ्य, सुरक्षा और पर्यावरण", "HSE"],
  "Data & Imports": ["डेटा और आयात", "Data aur imports"],
  "Reports": ["रिपोर्ट", "Reports"],
  "Audit": ["ऑडिट", "Audit"],
  "Schedule": ["कार्यसूची", "Schedule"],
  "Field Updates": ["फ़ील्ड अपडेट", "Field updates"],
  "Activity Matching": ["गतिविधि मिलान", "Activity matching"],
  "Planner Review": ["योजनाकार समीक्षा", "Planner review"],
  "Analytics": ["विश्लेषण", "Analytics"],
  "Knowledge Base": ["ज्ञान भंडार", "Knowledge base"],
  "My Activities": ["मेरी गतिविधियाँ", "Meri activities"],
  "My Team": ["मेरी टीम", "Meri team"],
  "Notifications": ["सूचनाएँ", "Notifications"],
  "Organization overview": ["संगठन का सारांश", "Organization overview"],
  "Project detail": ["परियोजना विवरण", "Project detail"],
  "Organization access": ["संगठन ऐक्सेस", "Organization access"],
  "Demo organization data": ["संगठन का डेमो डेटा", "Demo organization data"],
  "Today's site work": ["आज का साइट कार्य", "Aaj ka site work"],
  "Good morning,": ["नमस्कार,", "Namaste,"],
  "Field execution": ["फ़ील्ड कार्य", "Field execution"],
  "Assigned work, quick reporting, and updates from your Project Manager.": ["आवंटित कार्य, त्वरित रिपोर्टिंग और आपके परियोजना प्रबंधक के अपडेट।", "Assigned kaam, quick reporting aur aapke Project Manager ke updates."],
  "Portfolio execution, project health, and field activity across the organization.": ["पूरे संगठन में परियोजना कार्य, स्थिति और फ़ील्ड गतिविधि।", "Organization bhar mein project execution, health aur field activity."],
  "Add field update": ["फ़ील्ड अपडेट जोड़ें", "Field update jodein"],
  "Submit field update": ["फ़ील्ड अपडेट भेजें", "Field update bhejein"],
  "Team workforce and support workflows": ["टीम कार्यबल और सहायता कार्य", "Team workforce aur support workflows"],
  "Search": ["खोजें", "Khojein"],
  "Search projects, activities": ["परियोजनाएँ, गतिविधियाँ खोजें", "Projects, activities khojein"],
  "Overview": ["सारांश", "Overview"],
  "Name": ["नाम", "Naam"],
  "Role": ["भूमिका", "Role"],
  "Initial password": ["प्रारंभिक पासवर्ड", "Initial password"],
  "Create account": ["खाता बनाएँ", "Account banayein"],
  "Unassigned": ["आवंटित नहीं", "Unassigned"],
  "Unassigned project": ["परियोजना आवंटित नहीं", "Unassigned project"],
  "Choose a project": ["परियोजना चुनें", "Project chunein"],
  "Schedule data and imports": ["कार्यसूची डेटा और आयात", "Schedule data aur imports"],
  "Data source": ["डेटा स्रोत", "Data source"],
  "Access model": ["ऐक्सेस मॉडल", "Access model"],
  "Organization configuration is managed by the backend environment.": ["संगठन कॉन्फ़िगरेशन बैकएंड परिवेश से प्रबंधित होता है।", "Organization configuration backend environment se manage hota hai."],
  "Loading PRAVAHA": ["PRAVAHA लोड हो रहा है", "PRAVAHA load ho raha hai"],
  "Checking your session and loading your assigned workspace.": ["आपका सत्र जाँचा जा रहा है और कार्यक्षेत्र लोड हो रहा है।", "Session check aur workspace load ho raha hai."],
  "Workspace unavailable": ["कार्यक्षेत्र उपलब्ध नहीं", "Workspace available nahi hai"],
  "Access restricted": ["ऐक्सेस सीमित है", "Access restricted"],
  "Try again": ["फिर कोशिश करें", "Phir koshish karein"],
  "Cancel": ["रद्द करें", "Cancel"],
  "Save": ["सहेजें", "Save"],
  "Status": ["स्थिति", "Status"],
  "Activity": ["गतिविधि", "Activity"],
  "Actions": ["कार्रवाई", "Actions"],
  "Details": ["विवरण", "Details"],
  "View": ["देखें", "Dekhein"],
  "Edit": ["बदलें", "Edit"],
  "Delete": ["हटाएँ", "Delete"],
  "Refresh": ["रीफ़्रेश", "Refresh"],
  "Previous": ["पिछला", "Pichhla"],
  "Next": ["अगला", "Agla"],
  "Loading…": ["लोड हो रहा है…", "Load ho raha hai…"],
  "No results": ["कोई परिणाम नहीं", "Koi result nahi"],
  "Location": ["स्थान", "Location"],
  "Discipline": ["कार्य विभाग", "Discipline"],
  "Description": ["विवरण", "Description"],
  "Review": ["समीक्षा", "Review"],
  "Pending": ["लंबित", "Pending"],
  "Approved": ["स्वीकृत", "Approved"],
  "Rejected": ["अस्वीकृत", "Rejected"],
  "Active": ["सक्रिय", "Active"],
  "Completed": ["पूरा हुआ", "Completed"],
  "In progress": ["जारी", "In progress"],
  "Progress": ["प्रगति", "Progress"],
  "Planned": ["नियोजित", "Planned"],
  "Actual": ["वास्तविक", "Actual"],
  "Variance": ["अंतर", "Variance"],
  "Feedback": ["प्रतिक्रिया", "Feedback"],
  "Evidence": ["साक्ष्य", "Evidence"],
  "Notes": ["टिप्पणियाँ", "Notes"],
  "Submit": ["भेजें", "Bhejein"],
  "Import": ["आयात", "Import"],
  "Preview": ["पूर्वावलोकन", "Preview"],
  "Versions": ["संस्करण", "Versions"],
  "Compare": ["तुलना", "Compare"],
};

// Operational labels share the same catalogue as the public shell.
const operationalCopy = `
Text|टेक्स्ट|Text
Field Update Input|फ़ील्ड अपडेट इनपुट|Field update input
Text Updates|टेक्स्ट अपडेट|Text updates
Observations|अवलोकन|Observations
Demo Rules|डेमो नियम|Demo rules
Matching|मिलान|Matching
Audit Trail|ऑडिट रिकॉर्ड|Audit trail
Demo Data|डेमो डेटा|Demo data
Civil & Structural|सिविल और संरचनात्मक|Civil aur structural
Piping & Mechanical|पाइपिंग और मैकेनिकल|Piping aur mechanical
Electrical|विद्युत|Electrical
Instrumentation|इंस्ट्रूमेंटेशन|Instrumentation
HSE & Site Operations|HSE और साइट कार्य|HSE aur site operations
Static / Rotating Equipment|स्थिर / घूमने वाले उपकरण|Static / rotating equipment
Civil Works|सिविल कार्य|Civil works
Piping|पाइपिंग|Piping
Equipment Erection|उपकरण स्थापना|Equipment erection
Illustrative value|उदाहरण मान|Example value
Employees|कर्मचारी|Employees
Allocated Workers|आवंटित कर्मचारी|Allocated workers
Save record|रिकॉर्ड सहेजें|Record save karein
Saving.|सहेजा जा रहा है…|Save ho raha hai…
Creating.|बनाया जा रहा है…|Create ho raha hai…
Execution detail is available in each project. These counts come from persisted organization and assignment records.|कार्य विवरण हर परियोजना में उपलब्ध है। ये गिनतियाँ सहेजे गए संगठन और आवंटन रिकॉर्ड से आती हैं।|Execution details har project mein hain. Ye counts saved organization aur assignment records se hain.
Select records, then save. Transfers close the prior allocation and preserve its history. Teams with execution history retain their project.|रिकॉर्ड चुनकर सहेजें। स्थानांतरण पुराने आवंटन को बंद करके उसका इतिहास रखते हैं। कार्य इतिहास वाली टीमों की परियोजना बनी रहती है।|Records select karke save karein. Transfers purana allocation close karte hain aur history rakhte hain. Execution history wali teams ka project bana rehta hai.
Designation and department membership do not grant application access. Confidential HR access is a separate, explicit responsibility.|पदनाम और विभाग सदस्यता से ऐप का ऐक्सेस नहीं मिलता। गोपनीय HR ऐक्सेस एक अलग, स्पष्ट ज़िम्मेदारी है।|Designation aur department membership se app access nahi milta. Confidential HR access alag responsibility hai.
· Access is enforced by the API.|· ऐक्सेस API से नियंत्रित है।|· Access API se enforce hota hai.
No departmental responsibilities have been granted. Contact your organization administrator.|विभागीय ज़िम्मेदारियाँ नहीं दी गई हैं। अपने संगठन प्रशासक से संपर्क करें।|Department responsibilities nahi di gayi hain. Organization administrator se sampark karein.
Confidential cases require explicitly granted HR access. Enter only the information needed for this workflow.|गोपनीय मामलों के लिए स्पष्ट HR अनुमति चाहिए। इस कार्य के लिए आवश्यक जानकारी ही दर्ज करें।|Confidential cases ke liye explicit HR access chahiye. Sirf zaroori information enter karein.
Recorded receipts minus site issues, grouped by material and store. Material movements connect warehouse locations to project/team execution sites.|सामग्री और भंडार के अनुसार दर्ज प्राप्तियाँ घटाकर साइट निर्गम। सामग्री आवागमन भंडार को परियोजना और टीम साइट से जोड़ता है।|Material aur store ke hisaab se receipts minus site issues. Material movements stores ko project aur team sites se jodte hain.
Persisted evidence · PM-confirmed actuals · Calendar-day variance|सहेजे साक्ष्य · PM-पुष्ट वास्तविक आँकड़े · कैलेंडर-दिन अंतर|Saved evidence · PM-confirmed actuals · Calendar-day variance
. Read views calculate current signals; refresh records warning changes.|. दृश्य वर्तमान संकेत गणना करते हैं; रीफ़्रेश चेतावनी बदलाव सहेजता है।|. Views current signals calculate karte hain; refresh warning changes save karta hai.
Showing the first 50 impacts. Narrow project scope for detailed inspection.|पहले 50 प्रभाव दिख रहे हैं। विवरण के लिए परियोजना दायरा सीमित करें।|Pehle 50 impacts dikh rahe hain. Detail ke liye project scope narrow karein.
Warnings describe evidence and potential exposure; they do not prove a cause.|चेतावनियाँ साक्ष्य और संभावित जोखिम बताती हैं; वे कारण सिद्ध नहीं करतीं।|Warnings evidence aur potential exposure batati hain; cause prove nahi karti.
Positive days indicate adverse variance. N/A means dates or confirmation are missing. Completion alone does not establish an actual finish date.|धनात्मक दिन प्रतिकूल अंतर बताते हैं। N/A का अर्थ है तिथियाँ या पुष्टि नहीं हैं। केवल पूर्णता वास्तविक समाप्ति तिथि तय नहीं करती।|Positive days adverse variance batate hain. N/A matlab dates ya confirmation missing hain. Sirf completion se actual finish date tay nahi hoti.
. Empty denominator = N/A.|. हर खाली होने पर N/A।|. Empty denominator = N/A.
persisted records found. Provisional reports and PM confirmations remain distinct.|सहेजे रिकॉर्ड मिले। अस्थायी रिपोर्ट और PM पुष्टि अलग रखी जाती हैं।|saved records mile. Provisional reports aur PM confirmations alag rehte hain.
This historical recommendation predates stored evidence.|यह पुराना सुझाव साक्ष्य सहेजने की सुविधा से पहले का है।|Ye purana recommendation evidence storage se pehle ka hai.
Confidence describes available match evidence. PM confirmation is required.|विश्वास उपलब्ध मिलान साक्ष्य बताता है। PM पुष्टि आवश्यक है।|Confidence available match evidence batata hai. PM confirmation zaroori hai.
No relevant candidates were found in this project's L5/L6 schedule.|इस परियोजना की L5/L6 कार्यसूची में संबंधित विकल्प नहीं मिले।|Is project ke L5/L6 schedule mein relevant candidates nahi mile.
Calculated from persisted updates in your assigned scope. Confidence is a match score, not measured accuracy.|आपके आवंटित दायरे के सहेजे अपडेट से गणना। विश्वास एक मिलान स्कोर है, मापी गई सटीकता नहीं।|Aapke assigned scope ke saved updates se calculate hota hai. Confidence match score hai, measured accuracy nahi.
Raw source text remains available alongside the extracted activity and its current plan link.|मूल टेक्स्ट निकाली गतिविधि और वर्तमान योजना लिंक के साथ उपलब्ध रहता है।|Raw source text extracted activity aur current plan link ke saath available rehta hai.
Inspect the field report, proposed L5/L6 link, and actual data before recording a decision.|निर्णय दर्ज करने से पहले फ़ील्ड रिपोर्ट, सुझाया L5/L6 लिंक और वास्तविक डेटा देखें।|Decision record karne se pehle field report, proposed L5/L6 link aur actual data dekhein.
Recorded schedule state can include provisional TL actions. PM-confirmed variance and completion are shown in Execution intelligence.|दर्ज कार्यसूची में अस्थायी TL कार्रवाइयाँ हो सकती हैं। PM-पुष्ट अंतर और पूर्णता कार्य अंतर्दृष्टि में दिखते हैं।|Schedule mein provisional TL actions ho sakte hain. PM-confirmed variance aur completion execution intelligence mein hain.
Actual dates are drawn from confirmed or reported field execution.|वास्तविक तिथियाँ पुष्ट या रिपोर्ट किए फ़ील्ड कार्य से आती हैं।|Actual dates confirmed ya reported field execution se hain.
Choose a current project to scope its schedule and execution analytics.|कार्यसूची और कार्य विश्लेषण देखने के लिए वर्तमान परियोजना चुनें।|Schedule aur execution analytics ke liye current project chunein.
Confirmed activity actuals available in execution intelligence|पुष्ट गतिविधि आँकड़े कार्य अंतर्दृष्टि में उपलब्ध|Confirmed activity actuals execution intelligence mein available
No assigned projects. Ask an administrator to assign a project to this Project Manager.|कोई परियोजना आवंटित नहीं। इस प्रबंधक को परियोजना देने के लिए प्रशासक से कहें।|Koi assigned project nahi. Administrator se is PM ko project assign karne ko kahein.
Operational configuration is read-only for Project Managers.|परियोजना प्रबंधक परिचालन कॉन्फ़िगरेशन केवल पढ़ सकते हैं।|Project Managers operational configuration sirf dekh sakte hain.
Compare the field description with the current schedule link. Recommendations are calculated from stored L5/L6 activities and need PM confirmation.|फ़ील्ड विवरण को वर्तमान कार्यसूची लिंक से मिलाएँ। सुझाव सहेजी L5/L6 गतिविधियों से बनते हैं और PM पुष्टि चाहिए।|Field description ko current schedule link se compare karein. Recommendations stored L5/L6 activities se hain aur PM confirmation chahiye.
Team Leader will see this note as Action Required.|टीम लीडर को यह टिप्पणी कार्रवाई आवश्यक के रूप में दिखेगी।|Team Leader ko ye note Action Required ke roop mein dikhega.
CSV or XLSX, up to 2,000 activities. Dates: YYYY-MM-DD or native Excel dates. Dependencies: ActivityID:FS:lagDays. Existing field evidence and actuals are preserved.|CSV या XLSX, अधिकतम 2,000 गतिविधियाँ। तिथियाँ: YYYY-MM-DD या Excel तिथियाँ। निर्भरता: ActivityID:FS:lagDays। मौजूदा साक्ष्य और वास्तविक आँकड़े सुरक्षित रहते हैं।|CSV ya XLSX, 2,000 activities tak. Dates: YYYY-MM-DD ya Excel dates. Dependencies: ActivityID:FS:lagDays. Existing evidence aur actuals preserve hote hain.
(configuration only; live inference is checked separately).|(केवल कॉन्फ़िगरेशन; लाइव अनुमान अलग जाँचा जाता है)।|(sirf configuration; live inference alag check hota hai).
. Restore verification is an operator responsibility.|. पुनर्स्थापन जाँचना ऑपरेटर की ज़िम्मेदारी है।|. Restore verification operator ki responsibility hai.
Open intelligence for confirmed activity actuals|पुष्ट गतिविधि आँकड़ों के लिए अंतर्दृष्टि खोलें|Confirmed activity actuals ke liye intelligence kholein
At least 12 characters with uppercase, lowercase, number and special character. Assign the account to a project or team after creating it.|कम से कम 12 अक्षर, बड़े-छोटे अक्षर, संख्या और विशेष चिह्न सहित। खाता बनाने के बाद परियोजना या टीम आवंटित करें।|Kam se kam 12 characters, uppercase, lowercase, number aur special character ke saath. Account banakar project ya team assign karein.
Voice transcription and OCR are not configured. WAV recordings may be attached as evidence; enter the observation text for matching.|वॉइस ट्रांसक्रिप्शन और OCR कॉन्फ़िगर नहीं हैं। WAV रिकॉर्डिंग साक्ष्य में जोड़ सकते हैं; मिलान के लिए अवलोकन टेक्स्ट दर्ज करें।|Voice transcription aur OCR configured nahi hain. WAV evidence attach kar sakte hain; matching ke liye observation text enter karein.
Team staffing is provided for site context. Organization and user administration are managed by authorized roles.|टीम स्टाफ़ साइट संदर्भ के लिए है। संगठन और उपयोगकर्ता प्रबंधन अधिकृत भूमिकाएँ करती हैं।|Team staffing site context ke liye hai. Organization aur user administration authorized roles manage karti hain.
days|दिन|din
Start|आरंभ|Shuru
End|समाप्ति|Ant
of|में से|mein se
Team|टीम|Team
Record type|रिकॉर्ड प्रकार|Record type
FIELD INPUT|फ़ील्ड इनपुट|Field input
EXTRACTED ACTIVITY|निकाली गई गतिविधि|Extracted activity
records|रिकॉर्ड|records
All statuses|सभी स्थितियाँ|Sabhi statuses
Unmatched|मिलान नहीं हुआ|Unmatched
Confirm match|मिलान की पुष्टि करें|Match confirm karein
Submitted|भेजा गया|Submitted
activities|गतिविधियाँ|activities
Choose version|संस्करण चुनें|Version chunein
Create project|परियोजना बनाएँ|Project banayein
TEAM ON SITE|साइट पर टीम|Site par team
Capability|क्षमता|Capability
Choose capability|क्षमता चुनें|Capability chunein
No|नहीं|Nahi
Yes|हाँ|Haan
Workforce assignment history|कार्यबल आवंटन इतिहास|Workforce assignment history
Load history|इतिहास लोड करें|History load karein
Explicit organization assignments|संगठन के स्पष्ट आवंटन|Organization assignments
Department responsibilities|विभागीय ज़िम्मेदारियाँ|Department responsibilities
View explicit grants|दी गई अनुमतियाँ देखें|Granted access dekhein
Loading organization…|संगठन लोड हो रहा है…|Organization load ho rahi hai…
ORGANIZATION HEALTH ·|संगठन की स्थिति ·|Organization health ·
Portfolio and workforce allocation|परियोजनाएँ और कार्यबल आवंटन|Portfolio aur workforce allocation
Attention required|ध्यान देना आवश्यक|Dhyan zaroori
No recorded attention items.|ध्यान देने योग्य कोई रिकॉर्ड नहीं।|Koi attention item record nahi hai.
Loading permissions…|अनुमतियाँ लोड हो रही हैं…|Permissions load ho rahi hain…
Workflow|कार्यप्रवाह|Workflow
Create|बनाएँ|Banayein
Site / location|साइट / स्थान|Site / location
Choose|चुनें|Chunein
Inactive|निष्क्रिय|Inactive
Create record|रिकॉर्ड बनाएँ|Record banayein
records ·|रिकॉर्ड ·|records ·
Retry|फिर कोशिश करें|Phir koshish karein
Record details|रिकॉर्ड विवरण|Record details
Close details|विवरण बंद करें|Details band karein
Loading records…|रिकॉर्ड लोड हो रहे हैं…|Records load ho rahe hain…
No records found.|कोई रिकॉर्ड नहीं मिला।|Koi record nahi mila.
Inventory balances|भंडार शेष|Inventory balances
Search stock|स्टॉक खोजें|Stock khojein
Store|भंडार|Store
Material|सामग्री|Material
Unit|इकाई|Unit
Available|उपलब्ध|Available
No receipts or issues recorded.|कोई प्राप्ति या निर्गम दर्ज नहीं है।|Koi receipt ya issue record nahi hai.
Previous stock|पिछला स्टॉक|Pichhla stock
balances|शेष|balances
Next stock|अगला स्टॉक|Agla stock
Loading stock…|स्टॉक लोड हो रहा है…|Stock load ho raha hai…
Select project|परियोजना चुनें|Project chunein
Refresh intelligence|अंतर्दृष्टि रीफ़्रेश करें|Intelligence refresh karein
No permitted projects are assigned.|कोई अधिकृत परियोजना आवंटित नहीं है।|Koi authorized project assigned nahi hai.
Loading execution evidence…|कार्य साक्ष्य लोड हो रहे हैं…|Execution evidence load ho raha hai…
Evaluated|मूल्यांकन|Evaluated
Portfolio execution overview|परियोजना कार्य सारांश|Portfolio execution overview
complete ·|पूरा ·|complete ·
activities awaiting review · Linkage|समीक्षा की प्रतीक्षा में गतिविधियाँ · लिंक|Activities review mein · Linkage
Inspect project|परियोजना देखें|Project dekhein
Previous projects|पिछली परियोजनाएँ|Pichhle projects
Next projects|अगली परियोजनाएँ|Agle projects
Project health — contributing signals|परियोजना स्थिति — योगदान देने वाले संकेत|Project health — contributing signals
Dependency impact|निर्भरता प्रभाव|Dependency impact
· depth|· गहराई|· depth
· potential|· संभावित|· potential
Attention and early warnings|ध्यान और शुरुआती चेतावनियाँ|Attention aur early warnings
No current warning conditions were found.|अभी कोई चेतावनी स्थिति नहीं मिली।|Abhi koi warning condition nahi mili.
Why this warning?|यह चेतावनी क्यों?|Ye warning kyun?
First generated|पहली बार बना|Pehli baar bana
Why not matched?|मिलान क्यों नहीं हुआ?|Match kyun nahi hua?
Acknowledge|स्वीकार करें|Acknowledge karein
Close match evidence|मिलान साक्ष्य बंद करें|Match evidence band karein
Schedule variance and confirmed execution|कार्यसूची अंतर और पुष्ट कार्य|Schedule variance aur confirmed execution
State / timing|स्थिति / समय|State / timing
Confirmed progress|पुष्ट प्रगति|Confirmed progress
Start variance|आरंभ अंतर|Start variance
Finish variance|समाप्ति अंतर|Finish variance
Duration variance|अवधि अंतर|Duration variance
Potential downstream impact|अगली गतिविधियों पर संभावित प्रभाव|Potential downstream impact
Previous activities / warnings|पिछली गतिविधियाँ / चेतावनियाँ|Pichhli activities / warnings
activities,|गतिविधियाँ,|activities,
warnings|चेतावनियाँ|warnings
Next activities / warnings|अगली गतिविधियाँ / चेतावनियाँ|Agli activities / warnings
Execution data health|कार्य डेटा स्थिति|Execution data health
Institutional memory / what changed?|संस्थागत स्मृति / क्या बदला?|Institutional memory / kya badla?
Search persisted records|सहेजे रिकॉर्ड खोजें|Saved records khojein
All records|सभी रिकॉर्ड|Sabhi records
Activity timeline|गतिविधि समयरेखा|Activity timeline
Project timeline|परियोजना समयरेखा|Project timeline
Search memory|स्मृति खोजें|Memory khojein
Recorded details|दर्ज विवरण|Recorded details
Previous records|पिछले रिकॉर्ड|Pichhle records
Next records|अगले रिकॉर्ड|Agle records
Structured details and attachments|संरचित विवरण और संलग्नक|Structured details aur attachments
Load attachments|संलग्नक लोड करें|Attachments load karein
No persisted attachments.|कोई संलग्नक सहेजा नहीं गया।|Koi attachment save nahi hua.
bytes|बाइट|bytes
Uploaded|अपलोड किया गया|Uploaded
· checksum|· चेकसम|· checksum
Request|अनुरोध|Request
Match evidence|मिलान साक्ष्य|Match evidence
PRAVAHA recommendation|PRAVAHA सुझाव|PRAVAHA recommendation
· Generated|· बनाया गया|· Generated
Candidate activities|संभावित गतिविधियाँ|Candidate activities
Why did PRAVAHA suggest this?|PRAVAHA ने यह क्यों सुझाया?|PRAVAHA ne ye kyun suggest kiya?
Evidence for|इसके साक्ष्य|Iske evidence
Why not automatically matched?|स्वतः मिलान क्यों नहीं हुआ?|Auto match kyun nahi hua?
Matching health|मिलान स्थिति|Matching health
open reviews|खुली समीक्षाएँ|open reviews
Field updates captured|दर्ज फ़ील्ड अपडेट|Captured field updates
Records in assigned scope|आवंटित दायरे के रिकॉर्ड|Assigned scope ke records
Linked to schedule|कार्यसूची से जुड़ा|Schedule se linked
Confirmed by planner|योजनाकार ने पुष्टि की|Planner confirmed
Pending review|समीक्षा लंबित|Pending review
Human decision required|मानवीय निर्णय आवश्यक|Human decision zaroori
Unmatched activities|बिना मिलान की गतिविधियाँ|Unmatched activities
Schedule link not confirmed|कार्यसूची लिंक की पुष्टि नहीं|Schedule link unconfirmed
Actual:|वास्तविक:|Actual:
SUGGESTED SCHEDULE LINK|सुझाया कार्यसूची लिंक|Suggested schedule link
Captured field records|दर्ज फ़ील्ड रिकॉर्ड|Captured field records
Low confidence|कम विश्वास|Low confidence
Review required|समीक्षा आवश्यक|Review zaroori
No field updates match these filters.|इन फ़िल्टर से कोई फ़ील्ड अपडेट नहीं मिला।|In filters se koi field update nahi mila.
Field observations|फ़ील्ड अवलोकन|Field observations
Select a captured update to inspect its match.|मिलान देखने के लिए दर्ज अपडेट चुनें।|Match dekhne ke liye captured update chunein.
Field-to-plan match|फ़ील्ड से योजना मिलान|Field-to-plan match
· submitted by|· भेजने वाला|· submitted by
Full activity details|पूरी गतिविधि का विवरण|Full activity details
FIELD OBSERVATION|फ़ील्ड अवलोकन|Field observation
Actual dates:|वास्तविक तिथियाँ:|Actual dates:
extracted|निकाला गया|extracted
Source retained in audit trail|स्रोत ऑडिट रिकॉर्ड में सुरक्षित|Source audit trail mein saved
SCHEDULE ACTIVITY|कार्यसूची गतिविधि|Schedule activity
Select an activity|गतिविधि चुनें|Activity chunein
Confirmed by|पुष्टि करने वाला|Confirmed by
View audit|ऑडिट देखें|Audit dekhein
Create review item|समीक्षा रिकॉर्ड बनाएँ|Review item banayein
Review context|समीक्षा संदर्भ|Review context
No schedule link selected|कार्यसूची लिंक नहीं चुना गया|Koi schedule link selected nahi
Field Update Review|फ़ील्ड अपडेट समीक्षा|Field update review
updates|अपडेट|updates
Open review|समीक्षा खोलें|Review kholein
Needs Review|समीक्षा चाहिए|Review chahiye
Action Required|कार्रवाई आवश्यक|Action zaroori
Reviewed|समीक्षा हुई|Reviewed
Processing|प्रक्रिया जारी|Processing
All projects|सभी परियोजनाएँ|Sabhi projects
All disciplines|सभी कार्य विभाग|Sabhi disciplines
Confidence|विश्वास|Confidence
Any confidence|कोई भी विश्वास स्तर|Koi bhi confidence
High · 80%+|उच्च · 80%+|High · 80%+
Medium · 60–79%|मध्यम · 60–79%|Medium · 60–79%
Low · below 60%|कम · 60% से नीचे|Low · 60% se neeche
EXTRACTED / SUGGESTED|निकाला गया / सुझाया गया|Extracted / suggested
Review update|अपडेट की समीक्षा|Update review karein
Level|स्तर|Level
Planned dates|नियोजित तिथियाँ|Planned dates
Actual dates|वास्तविक तिथियाँ|Actual dates
Field link|फ़ील्ड लिंक|Field link
No confirmed field link|कोई पुष्ट फ़ील्ड लिंक नहीं|Koi confirmed field link nahi
Assigned project portfolio|आवंटित परियोजनाएँ|Assigned project portfolio
assigned|आवंटित|assigned
· Disciplines:|· कार्य विभाग:|· Disciplines:
Workspace environment|कार्यक्षेत्र परिवेश|Workspace environment
Persistent API data|सहेजा गया API डेटा|Persistent API data
Project data source|परियोजना डेटा स्रोत|Project data source
Activity hierarchy|गतिविधि संरचना|Activity hierarchy
L5 / L6 schedule activities|L5 / L6 कार्यसूची गतिविधियाँ|L5 / L6 schedule activities
Match decisions|मिलान निर्णय|Match decisions
Authentication|प्रमाणीकरण|Authentication
FIELD UPDATE REVIEW ·|फ़ील्ड अपडेट समीक्षा ·|Field update review ·
Field update|फ़ील्ड अपडेट|Field update
Project / team|परियोजना / टीम|Project / team
Submitted by|भेजने वाला|Submitted by
Source|स्रोत|Source
Observation / blocker|अवलोकन / बाधा|Observation / blocker
Extracted information|निकाली गई जानकारी|Extracted information
Detected discipline|पहचाना कार्य विभाग|Detected discipline
Detected location|पहचाना स्थान|Detected location
Identifiers|पहचानकर्ता|Identifiers
Action|कार्रवाई|Action
Date references|तिथि संदर्भ|Date references
Actual start|वास्तविक आरंभ|Actual start
Actual end|वास्तविक समाप्ति|Actual end
Suggested schedule match|सुझाया कार्यसूची मिलान|Suggested schedule match
% confidence|% विश्वास|% confidence
No confident schedule match found|विश्वसनीय कार्यसूची मिलान नहीं मिला|Confident schedule match nahi mila
Baseline|मूल कार्यसूची|Baseline
Schedule variance|कार्यसूची अंतर|Schedule variance
Search schedule activities|कार्यसूची गतिविधियाँ खोजें|Schedule activities khojein
Suggested activity|सुझाई गतिविधि|Suggested activity
Select an L5/L6 activity|L5/L6 गतिविधि चुनें|L5/L6 activity chunein
Save changed match|बदला मिलान सहेजें|Changed match save karein
PM feedback to Team Leader|टीम लीडर के लिए PM प्रतिक्रिया|Team Leader ke liye PM feedback
Request information|जानकारी माँगें|Jankari maangein
Reason|कारण|Karan
PM note (optional)|PM टिप्पणी (वैकल्पिक)|PM note (optional)
Confirm unmatched|बिना मिलान की पुष्टि करें|Unmatched confirm karein
Reviewed by|समीक्षा करने वाला|Reviewed by
Last PM feedback|पिछली PM प्रतिक्रिया|Last PM feedback
Review history|समीक्षा इतिहास|Review history
Mark unmatched|बिना मिलान चिह्नित करें|Unmatched mark karein
Search project records|परियोजना रिकॉर्ड खोजें|Project records khojein
Search records|रिकॉर्ड खोजें|Records khojein
permitted records|अधिकृत रिकॉर्ड|permitted records
Previous results|पिछले परिणाम|Pichhle results
Next results|अगले परिणाम|Agle results
Schedule import and versions|कार्यसूची आयात और संस्करण|Schedule import aur versions
Schedule file|कार्यसूची फ़ाइल|Schedule file
Preview schedule|कार्यसूची पूर्वावलोकन|Schedule preview
Column mapping|कॉलम मिलान|Column mapping
Preserve unsupported column|असमर्थित कॉलम सुरक्षित रखें|Unsupported column preserve karein
accepted ·|स्वीकृत ·|accepted ·
rejected|अस्वीकृत|rejected
Row|पंक्ति|Row
Preview rows and changes|पंक्तियों और बदलावों का पूर्वावलोकन|Rows aur changes ka preview
Import validated schedule|मान्य कार्यसूची आयात करें|Validated schedule import karein
Persisted versions|सहेजे संस्करण|Saved versions
activities ·|गतिविधियाँ ·|activities ·
Compare from|इससे तुलना|Compare from
Compare to|इससे तुलना करें|Compare to
Compare versions|संस्करणों की तुलना|Versions compare karein
Previous versions|पिछले संस्करण|Pichhle versions
Next versions|अगले संस्करण|Agle versions
System health|सिस्टम स्थिति|System health
Database:|डेटाबेस:|Database:
· Migrations:|· माइग्रेशन:|· Migrations:
· Rate limiting:|· अनुरोध सीमा:|· Rate limiting:
OCR:|OCR:|OCR:
· Speech:|· वाणी:|· Speech:
· Advanced AI:|· उन्नत AI:|· Advanced AI:
Assistant chat:|सहायक चैट:|Assistant chat:
Backup status:|बैकअप स्थिति:|Backup status:
Project name|परियोजना नाम|Project naam
Project location|परियोजना स्थान|Project location
‹ All projects|‹ सभी परियोजनाएँ|‹ Sabhi projects
· PROJECT DETAIL|· परियोजना विवरण|· Project detail
Overall weighted progress unavailable|कुल भारित प्रगति उपलब्ध नहीं|Overall weighted progress unavailable
PROJECT MANAGER|परियोजना प्रबंधक|Project Manager
Assigned teams|आवंटित टीमें|Assigned teams
teams ·|टीमें ·|teams ·
Team Leaders|टीम लीडर|Team Leaders
No teams assigned.|कोई टीम आवंटित नहीं।|Koi team assigned nahi.
sample projects|नमूना परियोजनाएँ|sample projects
Recorded project status|दर्ज परियोजना स्थिति|Recorded project status
Actual progress|वास्तविक प्रगति|Actual progress
PM profiles|PM प्रोफ़ाइल|PM profiles
Manager|प्रबंधक|Manager
Assigned projects|आवंटित परियोजनाएँ|Assigned projects
Active teams|सक्रिय टीमें|Active teams
Last activity|पिछली गतिविधि|Last activity
demo teams|डेमो टीमें|demo teams
Project / site|परियोजना / साइट|Project / site
Members|सदस्य|Members
on leave|अवकाश पर|chhutti par
Persistent audit events|सहेजी ऑडिट घटनाएँ|Persistent audit events
No organization activity has been recorded.|संगठन गतिविधि दर्ज नहीं हुई।|Koi organization activity record nahi hui.
WORKSPACE|कार्यक्षेत्र|Workspace
Authenticated administrator|प्रमाणित प्रशासक|Authenticated administrator
· ORGANIZATION VIEW|· संगठन दृश्य|· Organization view
Project workforce and support workflows|परियोजना कार्यबल और सहायता कार्य|Project workforce aur support workflows
SITE WORKSPACE|साइट कार्यक्षेत्र|Site workspace
Team Leader ·|टीम लीडर ·|Team Leader ·
FIELD CAPTURE|फ़ील्ड रिकॉर्ड|Field capture
What happened at site?|साइट पर क्या हुआ?|Site par kya hua?
Describe the work in your own words. Activity linking can be reviewed later.|कार्य अपने शब्दों में बताएँ। गतिविधि लिंक की समीक्षा बाद में हो सकती है।|Kaam apne shabdon mein batayein. Activity linking baad mein review ho sakti hai.
Field observation|फ़ील्ड अवलोकन|Field observation
Required|आवश्यक|Zaroori
activity details|गतिविधि विवरण|activity details
Optional|वैकल्पिक|Optional
Activity (optional)|गतिविधि (वैकल्पिक)|Activity (optional)
Let the planner link this update|योजनाकार इस अपडेट को लिंक करे|Planner ko update link karne dein
Discipline (optional)|कार्य विभाग (वैकल्पिक)|Discipline (optional)
Select discipline|कार्य विभाग चुनें|Discipline chunein
Location (optional)|स्थान (वैकल्पिक)|Location (optional)
Observation|अवलोकन|Observation
Source / attachment|स्रोत / संलग्नक|Source / attachment
Submitted as|इस रूप में भेजा गया|Submitted as
· Team Leader / Supervisor|· टीम लीडर / पर्यवेक्षक|· Team Leader / Supervisor
Started|शुरू हुआ|Started
Ended|समाप्त हुआ|Ended
Complete|पूरा करें|Complete karein
Mark blocked|अवरुद्ध चिह्नित करें|Blocked mark karein
Observation (optional)|अवलोकन (वैकल्पिक)|Observation (optional)
Save field update|फ़ील्ड अपडेट सहेजें|Field update save karein
Reason this work is blocked|काम रुकने का कारण|Kaam rukne ka karan
Record blocked activity|अवरुद्ध गतिविधि दर्ज करें|Blocked activity record karein
Detected:|पहचाना गया:|Detected:
Waiting for PM review|PM समीक्षा की प्रतीक्षा|PM review ka intezar
Execution coverage for the current shift.|वर्तमान पाली के कार्य का विवरण।|Current shift ka execution coverage.
Team members|टीम सदस्य|Team members
Active on site|साइट पर सक्रिय|Site par active
On leave|अवकाश पर|Chhutti par
Other assignment|अन्य आवंटन|Other assignment
SITE NOTIFICATIONS|साइट सूचनाएँ|Site notifications
Updates that need your attention|ध्यान देने योग्य अपडेट|Dhyan dene wale updates
TODAY'S WORK|आज का कार्य|Aaj ka kaam
Work assigned to|कार्य आवंटित|Kaam assigned to
· select a quick action to report site progress.|· साइट प्रगति बताने के लिए कार्रवाई चुनें।|· Site progress batane ke liye action chunein.
FIELD REPORTING|फ़ील्ड रिपोर्टिंग|Field reporting
Field observations are sent for schedule linking and Project Manager review.|फ़ील्ड अवलोकन कार्यसूची लिंक और परियोजना प्रबंधक समीक्षा के लिए भेजे जाते हैं।|Field observations schedule linking aur PM review ke liye bheje jaate hain.
View all|सभी देखें|Sab dekhein
SHIFT SUMMARY|पाली सारांश|Shift summary
Today's execution|आज का कार्य|Aaj ka execution
Assigned|आवंटित|Assigned
Blocked|अवरुद्ध|Blocked
Updates submitted|भेजे अपडेट|Submitted updates
members active|सक्रिय सदस्य|active members
· TODAY|· आज|· Aaj
Field execution ·|फ़ील्ड कार्य ·|Field execution ·
`;
for (const line of operationalCopy.trim().split("\n")) {
  const [key, hi, hinglish] = line.split("|");
  messages[key] = [hi, hinglish];
}

const registrationCopy = {
  "Signup category": "पंजीकरण श्रेणी",
  "At least 12 characters": "कम से कम 12 अक्षर",
  "Registration requires administrator approval before sign in.": "साइन इन से पहले पंजीकरण के लिए व्यवस्थापक की स्वीकृति आवश्यक है।",
  "Authorized Management email": "अधिकृत प्रबंधन ईमेल",
  "Authorized Supervisor email": "अधिकृत पर्यवेक्षक ईमेल",
  "Please use your authorized PRAVAHA Management email.": "कृपया अपना अधिकृत PRAVAHA प्रबंधन ईमेल उपयोग करें।",
  "Please use your authorized PRAVAHA Supervisor email.": "कृपया अपना अधिकृत PRAVAHA पर्यवेक्षक ईमेल उपयोग करें।",
  "Please use your authorized PRAVAHA work email.": "कृपया अपना अधिकृत PRAVAHA कार्य ईमेल उपयोग करें।",
  "This email domain is not valid for the selected role.": "यह ईमेल डोमेन चुनी गई भूमिका के लिए मान्य नहीं है।",
  "Full name is required.": "पूरा नाम आवश्यक है।",
  "Work email is required.": "कार्य ईमेल आवश्यक है।",
  "Password is required.": "पासवर्ड आवश्यक है।",
  "Email address is invalid.": "ईमेल पता अमान्य है।",
  "Password must be 12-128 characters and include uppercase, lowercase, number, and special character.": "पासवर्ड 12–128 अक्षरों का होना चाहिए और उसमें बड़ा अक्षर, छोटा अक्षर, संख्या और विशेष चिह्न होना चाहिए।",
  "If an account or registration already exists for this email, please contact your organization administrator.": "यदि इस ईमेल से खाता या पंजीकरण पहले से मौजूद है, तो अपने संगठन व्यवस्थापक से संपर्क करें।",
  "Your registration request has been submitted for administrator approval. If an account or registration already exists for this email, please contact your organization administrator.": "आपका पंजीकरण अनुरोध व्यवस्थापक की स्वीकृति के लिए जमा किया गया है। यदि इस ईमेल से खाता या पंजीकरण पहले से मौजूद है, तो अपने संगठन व्यवस्थापक से संपर्क करें।",
  "Your registration request has been submitted for administrator approval.": "आपका पंजीकरण अनुरोध व्यवस्थापक की स्वीकृति के लिए जमा किया गया है।",
  "Your account has been approved. You can now sign in.": "आपका खाता स्वीकृत हो गया है। अब आप साइन इन कर सकते हैं।",
  "Your registration request was not approved. Please contact your organization administrator.": "आपका पंजीकरण अनुरोध स्वीकृत नहीं हुआ। कृपया अपने संगठन व्यवस्थापक से संपर्क करें।",
  "Submitting…": "जमा किया जा रहा है…",
  "Pending registration": "पंजीकरण लंबित",
  "Too many registration attempts. Try again later.": "पंजीकरण के बहुत अधिक प्रयास हुए हैं। बाद में फिर प्रयास करें।",
  "Registration could not be completed. Please try again later.": "पंजीकरण पूरा नहीं हो सका। बाद में फिर प्रयास करें।",
  "Unable to connect. Please try again.": "कनेक्शन नहीं हो सका। फिर प्रयास करें।",
  "Please check the registration details.": "कृपया पंजीकरण विवरण जाँचें।",
  "Registrations": "पंजीकरण",
  "Registration requests": "पंजीकरण अनुरोध",
  "Administrator approval": "व्यवस्थापक की स्वीकृति",
  "Admin approval": "व्यवस्थापक की स्वीकृति",
  "Account activated": "खाता सक्रिय",
  "Requested category": "अनुरोधित श्रेणी",
  "Email domain": "ईमेल डोमेन",
  "Created date": "निर्माण तिथि",
  "Approved": "स्वीकृत",
  "Rejected": "अस्वीकृत",
  "All statuses": "सभी स्थितियाँ",
  "Refresh": "ताज़ा करें",
  "Loading registration requests.": "पंजीकरण अनुरोध लोड हो रहे हैं।",
  "No registration requests match this status.": "इस स्थिति में कोई पंजीकरण अनुरोध नहीं है।",
  "Approval assigns this account to your organization.": "स्वीकृति से यह खाता आपके संगठन को सौंपा जाएगा।",
  "Final role": "अंतिम भूमिका",
  "Approve": "स्वीकृत करें",
  "Reject": "अस्वीकार करें",
  "Reviewing.": "समीक्षा हो रही है।",
  "Rejection reason": "अस्वीकृति का कारण",
  "Give a short reason for the decision.": "निर्णय का संक्षिप्त कारण दें।",
  "Confirm rejection": "अस्वीकृति की पुष्टि करें",
  "Registration approved. The account can now sign in.": "पंजीकरण स्वीकृत है। अब खाते से साइन इन किया जा सकता है।",
  "Registration rejected. No account was activated.": "पंजीकरण अस्वीकृत है। कोई खाता सक्रिय नहीं किया गया।",
  "Registration requests could not be loaded. Please try again.": "पंजीकरण अनुरोध लोड नहीं हो सके। फिर प्रयास करें।",
  "The registration could not be reviewed. Please try again.": "पंजीकरण की समीक्षा नहीं हो सकी। फिर प्रयास करें।",
  "This registration has already been reviewed. Refresh the list.": "इस पंजीकरण की समीक्षा पहले ही हो चुकी है। सूची ताज़ा करें।",
  "You do not have access to review registration requests.": "आपको पंजीकरण अनुरोधों की समीक्षा की अनुमति नहीं है।",
  "Previous": "पिछला",
  "Next": "अगला",
  "Total requests": "कुल अनुरोध",
  "Registration review saved. Refresh the workspace if the account is not visible yet.": "पंजीकरण समीक्षा सहेजी गई है। खाता न दिखने पर कार्यक्षेत्र ताज़ा करें।",
};
for (const [key, hi] of Object.entries(registrationCopy)) messages[key] = [hi, hi];

const dashboardAnalyticsCopy = {
  "Project Progress Overview": "परियोजना प्रगति अवलोकन",
  "Planned vs actual completion across the portfolio": "परियोजनाओं में नियोजित और वास्तविक पूर्णता",
  "Planned": "नियोजित", "Actual": "वास्तविक", "Cumulative activity completion": "संचयी गतिविधि पूर्णता",
  "Percentage of all scheduled activities with planned or confirmed finish dates. Future actuals are not forecast.": "सभी अनुसूचित गतिविधियों में नियोजित या पुष्ट समाप्ति तिथियों का प्रतिशत। भविष्य के वास्तविक परिणामों का पूर्वानुमान नहीं है।",
  "Schedule dates unavailable": "अनुसूची की तिथियाँ उपलब्ध नहीं हैं",
  "Import a dated schedule to compare planned and confirmed completions.": "नियोजित और पुष्ट पूर्णता की तुलना के लिए तिथियों वाली अनुसूची आयात करें।",
  "Not available": "उपलब्ध नहीं", "Dated schedule coverage": "तिथियों वाली अनुसूची कवरेज",
  "Confirmed finish dates": "पुष्ट समाप्ति तिथियाँ",
  "Current schedule snapshot; not historical weighted progress.": "वर्तमान अनुसूची का सारांश; ऐतिहासिक भारित प्रगति नहीं।",
  "Total activities": "कुल गतिविधियाँ", "No records available yet.": "अभी कोई रिकॉर्ड उपलब्ध नहीं है।",
  "Analytics could not be loaded.": "विश्लेषण लोड नहीं हो सका।",
  "Your organization records are still available in the navigation above.": "संगठन के रिकॉर्ड ऊपर दिए नेविगेशन में उपलब्ध हैं।",
  "Loading organization analytics": "संगठन का विश्लेषण लोड हो रहा है",
  "Refresh analytics": "विश्लेषण ताज़ा करें", "As of": "स्थिति समय",
  "Total projects": "कुल परियोजनाएँ", "Organization portfolio": "संगठन की परियोजनाएँ",
  "Confirmed progress": "पुष्ट प्रगति", "activities with progress": "गतिविधियों की प्रगति उपलब्ध",
  "Delayed activities": "विलंबित गतिविधियाँ", "Confirmed delay signals": "पुष्ट विलंब संकेत",
  "Current schedule evidence": "वर्तमान अनुसूची के साक्ष्य", "Supervised teams": "पर्यवेक्षक वाली टीमें",
  "total teams": "कुल टीमें", "Workforce": "कार्यबल", "active allocations": "सक्रिय आवंटन",
  "Discipline Progress": "कार्य क्षेत्र की प्रगति", "Mean confirmed activity progress": "पुष्ट गतिविधि प्रगति का औसत",
  "No scheduled disciplines yet.": "अभी अनुसूचित कार्य क्षेत्र नहीं हैं।",
  "Unweighted mean of known progress. Missing evidence is excluded, not treated as zero.": "ज्ञात प्रगति का अभारित औसत। अनुपलब्ध साक्ष्य को शून्य नहीं माना गया है।",
  "Project Portfolio": "परियोजना पोर्टफोलियो", "Recorded project status and confirmed execution": "दर्ज परियोजना स्थिति और पुष्ट निष्पादन",
  "All projects": "सभी परियोजनाएँ", "Location unavailable": "स्थान उपलब्ध नहीं",
  "Limited evidence": "सीमित साक्ष्य", "No delay signal": "विलंब का संकेत नहीं", "At risk": "जोखिम में",
  "with evidence": "साक्ष्य उपलब्ध", "Recorded status": "दर्ज स्थिति",
  "No projects available. Create a project to begin.": "कोई परियोजना उपलब्ध नहीं है। शुरू करने के लिए परियोजना बनाएँ।",
  "Recent Field Updates": "हाल के स्थल अपडेट", "Latest reports on the current schedule": "वर्तमान अनुसूची की नवीनतम रिपोर्ट",
  "No field updates recorded yet.": "अभी कोई स्थल अपडेट दर्ज नहीं है।",
  "Schedule Matching": "अनुसूची मिलान", "Accepted links and review backlog": "स्वीकृत लिंक और लंबित समीक्षा",
  "Matched means a reviewed, accepted schedule link.": "मिलान का अर्थ समीक्षा के बाद स्वीकृत अनुसूची लिंक है।",
  "Activity Status": "गतिविधि स्थिति", "Authoritative execution evidence": "प्रामाणिक निष्पादन साक्ष्य",
  "Unknown means confirmed actuals are unavailable.": "अज्ञात का अर्थ पुष्ट वास्तविक आँकड़े उपलब्ध नहीं हैं।",
  "Unknown": "अज्ञात", "Pending review": "समीक्षा लंबित", "Low confidence": "कम विश्वास",
  "Key Alerts": "प्रमुख चेतावनियाँ", "Existing execution intelligence": "मौजूदा निष्पादन विश्लेषण",
  "High priority": "उच्च प्राथमिकता", "Requires attention": "ध्यान आवश्यक", "Review evidence": "साक्ष्यों की समीक्षा करें",
  "No current execution alerts.": "अभी निष्पादन की कोई चेतावनी नहीं है।", "View execution report": "निष्पादन रिपोर्ट देखें",
  "Organization attention": "संगठन में ध्यान योग्य विषय", "Ownership, workforce and access": "जिम्मेदारी, कार्यबल और पहुँच",
  "Pending registrations": "लंबित पंजीकरण", "Employees": "कर्मचारी", "PM not assigned": "परियोजना प्रबंधक नियुक्त नहीं है",
  "Recorded execution risk": "दर्ज निष्पादन जोखिम", "Schedule variance": "अनुसूची विचलन",
  "Approaching planned finish": "नियोजित समाप्ति निकट है", "Stale execution evidence": "पुराने निष्पादन साक्ष्य",
  "Incomplete field reports": "अधूरी स्थल रिपोर्ट", "Schedule data quality": "अनुसूची डेटा गुणवत्ता",
  "Unmatched field updates": "बिना मिलान के स्थल अपडेट", "PM review required": "परियोजना प्रबंधक की समीक्षा आवश्यक",
  "Schedule version changed": "अनुसूची संस्करण बदला", "Schedule link quality": "अनुसूची लिंक गुणवत्ता",
  "Dependency exposure": "निर्भरता जोखिम", "Negative schedule float": "ऋणात्मक अनुसूची फ्लोट",
};
for (const [key, hi] of Object.entries(dashboardAnalyticsCopy)) messages[key] = [hi, hi];

export function resolveLocale(language, browserLanguage = "en") {
  return language === "auto" ? (browserLanguage.toLowerCase().startsWith("hi") ? "hi" : "en") : language;
}

export function translate(text, locale) {
  if (typeof text !== "string" || locale === "en") return text;
  const key = text.trim().replace(/\s+/g, " ");
  const entry = messages[key] ?? normalizedMessages.get(key.toLowerCase());
  return entry ? text.replace(text.trim(), entry[locale === "hi" ? 0 : 1]) : text;
}

const normalizedMessages = new Map(Object.entries(messages).map(([key, value]) => [key.toLowerCase(), value]));
export const translationKeys = new Set(Object.keys(messages));
