"""
KisanMitra Grounded Agricultural Knowledge Base & Extension Engine
==================================================================
Curated from official Indian agricultural institutions:
- Indian Council of Agricultural Research (ICAR institutes: IIHR, CRIDA, IARI)
- State Agricultural Universities (ANGRAU, PJTSAU, TNAU, PAU)
- Central Insecticides Board & Registration Committee (CIBRC) Label Guidelines
- Krishi Vigyan Kendra (KVK) Extension Protocols

Covers 11 major Indian crops:
Chilli, Tomato, Cotton, Paddy (Rice), Onion, Maize, Turmeric, Potato, Groundnut, Wheat, Gram (Pulses).
"""

from typing import Dict, Any, Optional, Tuple, List
import re

# Comprehensive Verified Agricultural Extension Knowledge Base
AGRI_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "Chilli": {
        "name": {"en": "Chilli", "te": "మిర్చి", "hi": "मिर्च"},
        "suitable_seasons": {"en": "Kharif (June–July nursery, July–Aug transplanting), Rabi (Sept–Oct)", "te": "ఖరీఫ్ (జూన్–జూలై నారు, జూలై–ఆగస్టు నాట్లు), రబీ (సెప్టెంబర్–అక్టోబర్)", "hi": "खरीफ (जून-जुलाई पौध), रबी (सितंबर-अक्टूबर)"},
        "suitable_soils": {"en": "Well-drained black clay or fertile red loamy soils (pH 6.0–7.5). Avoid waterlogged soils.", "te": "మురుగు నీటి పారుదల గల నల్లరేగడి లేదా ఎర్ర నేలలు (pH 6.0–7.5). నీరు నిలిచే నేలలు పనికిరావు.", "hi": "अच्छी जल निकासी वाली काली या लाल दोमट मिट्टी (pH 6.0–7.5)। जलभराव वाली मिट्टी से बचें।"},
        "fertilizer_guide": {
            "title": {"en": "Fertilizer & Nutrient Schedule for Chilli", "te": "మిర్చి సమగ్ర ఎరువుల యాజమాన్యం", "hi": "मिर्च के लिए संतुलित खाद एवं उर्वरक प्रबंधन"},
            "happening": {
                "en": "Chilli requires balanced basal nutrition (NPK) followed by split nitrogen doses and micronutrients (Boron, Zinc) during flowering and fruit setting to prevent flower drop.",
                "te": "మిర్చిలో పూత మరియు పిందె నిలవడానికి సమతుల్య ఎరువులు, సమయానికి నత్రజని మరియు బోరాన్, జింక్ వంటి సూక్ష్మపోషకాలు అవసరం.",
                "hi": "मिर्च की अच्छी पैदावार और फूल झड़ने से रोकने के लिए संतुलित एनपीके और सूक्ष्म पोषक तत्वों (बोरॉन, जिंक) की आवश्यकता होती है।"
            },
            "check": {
                "en": "Check soil moisture before application. Inspect crop growth stage (vegetative, flowering, or fruit enlargement).",
                "te": "ఎరువులు వేసే ముందు నేలలో తగినంత తేమ ఉందో లేదో చూడండి. పంట దశను గమనించండి.",
                "hi": "खाद देने से पहले मिट्टी में नमी की जांच करें और फसल की अवस्था (वृद्धि, फूल या फल) देखें।"
            },
            "actions": {
                "en": "• Basal: Well-decomposed FYM @ 10 tonnes/acre + 20 kg P2O5 (SSP) + 15 kg K2O (MOP).\n• Vegetative stage: Top-dress Urea @ 15 kg/acre with adequate moisture.\n• Flowering stage: Foliar spray of 0:52:34 @ 5 g/L + Boron (20%) @ 1 g/L to reduce flower drop.\n• Fruit development: Spray Potassium Nitrate (13:0:45) @ 5 g/L + Calcium Nitrate @ 2 g/L for fruit firmness.",
                "te": "• ఆఖరి దుక్కిలో: ఎకరానికి 10 టన్నుల పశువుల ఎరువు + సింగిల్ సూపర్ ఫాస్ఫేట్ 100 కిలోలు + పొటాష్ 25 కిలోలు.\n• శాఖీయ దశలో: ఎకరానికి 15–20 కిలోల యూరియాను తేమ ఉన్నప్పుడు వేయండి.\n• పూత దశలో: పూత రాలకుండా 0:52:34 లీటరు నీటికి 5 గ్రాములు + బోరాన్ 1 గ్రాము కలిపి పిచికారీ చేయండి.\n• కాయ దశలో: 13:0:45 ఎరువు 5 గ్రా/లీ + కాల్షియం నైట్రేట్ 2 గ్రా/లీ కలిపి పిచికారీ చేయండి.",
                "hi": "• बुवाई के समय: 10 टन गोबर की खाद + सिंगल सुपर फॉस्फेट + पोटाश डालें।\n• वृद्धि अवस्था: पर्याप्त नमी में 15-20 किग्रा यूरिया प्रति एकड़ दें।\n• फूल आने पर: फूल झड़ने से रोकने हेतु 0:52:34 (5 ग्राम/लीटर) + बोरॉन (1 ग्राम/लीटर) का छिड़काव करें।\n• फल विकास: 13:0:45 (5 ग्राम/लीटर) + कैल्शियम नाइट्रेट (2 ग्राम/लीटर) का छिड़काव करें।"
            },
            "precautions": {
                "en": "Never spray foliar fertilizers under intense afternoon sunlight. Always test soil before heavy fertilizer application.",
                "te": "ఎండ తీవ్రత ఎక్కువగా ఉన్నప్పుడు ఎరువులు స్ప్రే చేయవద్దు. చల్లని వేళల్లో మాత్రమే పిచికారీ చేయండి.",
                "hi": "कड़ी धूप में छिड़काव न करें। हमेशा मिट्टी परीक्षण के आधार पर ही संतुलित उर्वरक दें।"
            },
            "source": "ICAR-IIHR & ANGRAU Crop Production Guidelines"
        },
        "irrigation_guide": {
            "title": {"en": "Irrigation Management for Chilli", "te": "మిర్చి నీటి యాజమాన్యం", "hi": "मिर्च में सिंचाई प्रबंधन"},
            "happening": {
                "en": "Chilli is sensitive to both water stagnation and drought stress. Critical moisture periods are transplanting, flowering, and fruit development.",
                "te": "మిర్చికి నీరు నిలవడం మరియు బెట్ట రెండూ నష్టపరుస్తాయి. నాట్లు వేసినప్పుడు, పూత మరియు కాయ దశల్లో క్రమం తప్పకుండా తేలికపాటి తడులు అవసరం.",
                "hi": "मिर्च में जलभराव और सूखे दोनों से नुकसान होता है। फूल और फल बनने के समय नियमित हल्की सिंचाई आवश्यक है।"
            },
            "check": {
                "en": "Check soil moisture at 5–10 cm depth. Observe if plants show mid-day temporary wilting.",
                "te": "నేలలో 5–10 సెం.మీ లోతులో తేమను గమనించండి. మధ్యాహ్నం వేళ మొక్కలు వాలిపోతున్నాయా చూడండి.",
                "hi": "जड़ के पास 5-10 सेमी गहराई पर मिट्टी की नमी जांचें।"
            },
            "actions": {
                "en": "• Provide light, frequent irrigations (every 5–7 days in black soils, 3–4 days in light soils, or daily through drip).\n• Maintain good drainage channels to prevent root rot during heavy rains.\n• Avoid heavy flood irrigation during flowering to prevent flower drop.",
                "te": "• నల్లరేగడి నేలల్లో 5–7 రోజులకు, తేలికపాటి నేలల్లో 3–4 రోజులకు లేదా డ్రిప్ ద్వారా రోజూ తేలికపాటి తడులు ఇవ్వండి.\n• వర్షాలు పడినప్పుడు నీరు నిలవకుండా మురుగు కాలువలు తీయండి.\n• పూత దశలో అధికంగా నీరు పెట్టవద్దు.",
                "hi": "• ड्रिप द्वारा या 5-7 दिन के अंतराल पर हल्की सिंचाई करें।\n• बारिश के दिनों में खेत में पानी न रुकने दें।\n• फूल आने पर आवश्यकता से अधिक पानी न दें।"
            },
            "precautions": {
                "en": "Excessive irrigation triggers collar rot and viral wilt in chilli fields.",
                "te": "అధిక తేమ వల్ల వేరుకుళ్లు, మొదలుకుళ్లు తెగుళ్లు ఆశిస్తాయి.",
                "hi": "अधिक जलभराव से जड़ सड़न और उकठा रोग का खतरा बढ़ जाता है।"
            },
            "source": "ICAR-CRIDA Water Management Advisory"
        },
        "symptoms": {
            "leaf_curl": {
                "title": {"en": "Leaf Curl & Sucking Pests (Thrips & Mites)", "te": "ఆకుముడత & రసం పీల్చే పురుగులు (నల్ల తామర & నల్లి)", "hi": "पत्ती मरोड़ एवं रस चूसक कीट (थ्रिप्स और माइट्स)"},
                "happening": {
                    "en": "Upward leaf curling (boat shape) is caused by thrips (Scirtothrips dorsalis / Thrips parvispinus). Downward curling and brittle leaves indicate yellow mites. They suck cell sap from tender foliage.",
                    "te": "ఆకులు పైకి ముడుచుకుని పడవ ఆకారంలో మారడం తామర పురుగుల (నల్ల తామర) వల్ల, కిందికి ముడుచుకుపోవడం నల్లి పురుగుల వల్ల సంభవిస్తుంది. ఇవి లేత ఆకుల రసం పీల్చి నష్టం కలిగిస్తాయి.",
                    "hi": "पत्तियों का ऊपर की ओर मुड़ना थ्रिप्स के कारण और नीचे की ओर मुड़ना माइट्स (मकड़ी) के कारण होता है। ये कीट पत्तियों का रस चूसकर पौधे को कमजोर करते हैं।"
                },
                "check": {
                    "en": "Inspect the undersides of tender leaves with a 10x lens for tiny yellow/black nymphs, bronze streaks, or fine webbing.",
                    "te": "లేత ఆకుల అడుగు భాగాన్ని 10x లెన్స్ తో పరిశీలించండి. సన్నటి తామర పురుగులు లేదా గోధుమ రంగు గీతలు కనిపిస్తాయి.",
                    "hi": "10x लेंस से पत्तियों की निचली सतह की जांच करें। बारीक पीले/काले कीट या पत्तियों के नीचे खुरदुरे निशान दिखाई देंगे।"
                },
                "actions": {
                    "en": "• Install 15–20 blue sticky traps per acre for thrips and yellow traps for whiteflies.\n• Spray bio-pesticide Neem oil (10,000 ppm) @ 2 ml/L or Verticillium lecanii @ 5 g/L.\n• For severe verified infestation exceeding economic threshold, consult local AO/KVK for CIBRC-approved formulations such as Fipronil 5% SC @ 2 ml/L or Acetamiprid 20% SP @ 0.5 g/L.",
                    "te": "• ఎకరానికి 15–20 నీలి రంగు జిగురు అట్టలు (తామర పురుగులకు), పసుపు అట్టలు (తెల్లదోమకు) అమర్చండి.\n• నివారణకు వేపనూనె (10,000 ppm) లీటరు నీటికి 2 మి.లీ లేదా వర్టిసిల్లియం లెకాని 5 గ్రా/లీ పిచికారీ చేయండి.\n• ఉధృతి ఎక్కువగా ఉంటే వ్యవసాయాధికారి సలహాతో ఫిప్రోనిల్ 5% SC 2 మి.లీ/లీటరు లేదా ఎసిటామిప్రిడ్ 20% SP 0.5 గ్రా/లీ పిచికారీ చేయండి.",
                    "hi": "• प्रति एकड़ 15-20 नीले चिपचिपे ट्रैप (थ्रिप्स हेतु) और पीले ट्रैप लगाएं।\n• रोकथाम के लिए नीम तेल (10,000 ppm) 2 मिली प्रति लीटर या वर्टिसिलियम लेकानी 5 ग्राम/लीटर का छिड़काव करें।\n• अधिक प्रकोप होने पर कृषि विशेषज्ञ की सलाह से फिप्रोनिल 5% SC 2 मिली/लीटर या एसिटामिप्रिड 20% SP 0.5 ग्राम/लीटर का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Avoid tank-mixing unverified chemical cocktails. Spray in the cool morning or late afternoon with protective gear.",
                    "te": "రసాయనాలను విచక్షణారహితంగా కలపవద్దు. చల్లని వేళల్లో మాత్రమే పిచికారీ చేయండి.",
                    "hi": "अनावश्यक रासायनिक कीटनाशकों का मिश्रण न बनाएं। छिड़काव हमेशा सुबह या शाम के ठंडे समय में सुरक्षा उपकरणों के साथ करें।"
                },
                "source": "ICAR-IIHR (Indian Institute of Horticultural Research) & ANGRAU IPM Protocol"
            },
            "yellowing_lower": {
                "title": {"en": "Lower Leaf Yellowing (Nitrogen Deficiency or Waterlogging)", "te": "కింది ఆకులు పసుపుబారడం (నత్రజని లోపం లేదా నీరు నిలవడం)", "hi": "निचली पत्तियों का पीलापन (नाइट्रोजन की कमी या जलभराव)"},
                "happening": {
                    "en": "Gradual uniform yellowing starting from bottom/older leaves indicates mobile nitrogen deficiency or root asphyxiation from stagnant water.",
                    "te": "మొక్క కింది భాగంలోని పాత ఆకులు మొదట పసుపు రంగులోకి మారి పైకి వ్యాపిస్తే అది నత్రజని లోపం లేదా వేర్ల వద్ద నీరు నిలవడం వల్ల జరిగిన నష్టం కావచ్చు.",
                    "hi": "पौधे के नीचे के पुराने पत्तों का पीला होना मुख्य रूप से नाइट्रोजन की कमी या जड़ों के पास पानी रुकने के कारण होता है।"
                },
                "check": {
                    "en": "Check if veins and leaf blades are uniformly pale yellow without dark fungal spots. Inspect root zone for excess moisture.",
                    "te": "ఆకు మొత్తం సమానంగా లేత పసుపు రంగులో ఉందో లేదో చూడండి. పొలంలో నీరు నిలిచి వేర్లు కుళ్లుతున్నాయా అనేది పరిశీలించండి.",
                    "hi": "जांचें कि क्या पत्तियां बिना धब्बों के पूरी तरह पीली हैं। खेत में जलभराव या जड़ सड़न की जांच करें।"
                },
                "actions": {
                    "en": "• Ensure field drainage channels are clear to drain stagnant moisture.\n• Apply foliar spray of 19:19:19 (Water Soluble NPK) @ 4–5 g/L for rapid uptake.\n• Top-dress balanced Urea @ 15–20 kg/acre if crop is in vegetative phase with adequate soil moisture.",
                    "te": "• మడిలో నీరు నిలబడకుండా వెంటనే మురుగు కాలువల ద్వారా బయటకు పంపండి.\n• తక్షణ రికవరీ కోసం 19:19:19 నీటిలో కరిగే ఎరువును లీటరు నీటికి 4-5 గ్రాములు కలిపి పిచికారీ చేయండి.\n• నేలలో తగినంత తేమ ఉన్నప్పుడు సిఫార్సు చేసిన మోతాదులో యూరియాను అందించండి.",
                    "hi": "• खेत से अतिरिक्त पानी निकालने की व्यवस्था करें।\n• त्वरित पोषण हेतु 19:19:19 (घुलनशील एनपीके) 4-5 ग्राम प्रति लीटर पानी में मिलाकर पर्णीय छिड़काव करें।\n• मिट्टी में पर्याप्त नमी होने पर ही नाइट्रोजन युक्त संतुलित खाद दें।"
                },
                "precautions": {
                    "en": "Do not apply excessive nitrogen during flowering as it drops flowers and invites sucking pests.",
                    "te": "పూత మరియు కాయ దశలో అధికంగా యూరియా వాడవద్దు, దీనివల్ల పూత రాలిపోవడం జరుగుతుంది.",
                    "hi": "फूल आने के समय अधिक यूरिया न डालें, इससे फूल झड़ने की समस्या हो सकती है।"
                },
                "source": "ICAR-CRIDA Soil & Nutrient Advisory Bulletin"
            },
            "yellowing_upper": {
                "title": {"en": "Top / Young Leaf Yellowing (Micronutrient Iron or Zinc Deficiency)", "te": "పై లేత ఆకులు పసుపుబారడం (జింక్ లేదా ఐరన్ లోపం)", "hi": "ऊपरी नई पत्तियों का पीलापन (जिंक या आयरन की कमी)"},
                "happening": {
                    "en": "Interveinal chlorosis (yellow tissue with dark green veins) on top young leaves indicates immobile micronutrient deficiency (Iron or Zinc) in high pH or calcareous soils.",
                    "te": "పై లేత ఆకులలో ఈనెలు ఆకుపచ్చగా ఉండి మధ్య భాగం పసుపు రంగులోకి మారడం ఐరన్ లేదా జింక్ సూక్ష్మపోషక లోపం వల్ల జరుగుతుంది.",
                    "hi": "ऊपरी नई पत्तियों में नसों का हरा रहना और बीच का भाग पीला पड़ना जिंक या आयरन पोषक तत्व की कमी का संकेत है।"
                },
                "check": {
                    "en": "Look closely at the newest growth flush. If only young terminal leaves are yellow while bottom leaves are green, it is micronutrient deficiency.",
                    "te": "కొత్తగా వస్తున్న లేత ఆకులను గమనించండి. కింది ఆకులు ఆకుపచ్చగా ఉండి పై లేత ఆకులు మాత్రమే పసుపుగా ఉంటే అది సూక్ష్మపోషకాల లోపమే.",
                    "hi": "पौधे के ऊपरी नए पत्तों को देखें। यदि पुराने पत्ते हरे हैं और केवल नई पत्तियां पीली हैं, तो यह सूक्ष्म पोषक तत्वों की कमी है।"
                },
                "actions": {
                    "en": "• Spray Chelated Zinc (Zn-EDTA 12%) @ 1–1.5 g/L or Zinc Sulphate @ 2 g/L with 1 g/L slaked lime.\n• For iron chlorosis, spray Ferrous Sulphate (FeSO4) @ 5 g/L + Citric acid @ 1 g/L in 1 liter water.\n• Apply well-rotted organic manure enriched with micronutrients.",
                    "te": "• చీలేటెడ్ జింక్ (Zn-EDTA 12%) లీటరు నీటికి 1–1.5 గ్రాములు కలిపి పిచికారీ చేయండి.\n• ఐరన్ లోపం ఉంటే అన్నభేది (ఫెర్రస్ సల్ఫేట్) 5 గ్రా/లీ + నిమ్మ ఉప్పు 1 గ్రా/లీ కలిపి పిచికారీ చేయండి.",
                    "hi": "• चिलेटेड जिंक (Zn-EDTA) 1-1.5 ग्राम प्रति लीटर पानी में मिलाकर छिड़काव करें।\n• आयरन की कमी होने पर फेरस सल्फेट 5 ग्राम + 1 ग्राम साइट्रिक एसिड प्रति लीटर पानी में मिलाकर छिड़कें।"
                },
                "precautions": {
                    "en": "Do not mix zinc sulfate directly with phosphatic fertilizers (DAP/SSP) in the same tank as it precipitates insoluble zinc phosphate.",
                    "te": "జింక్ ఎరువును డిఎపి లేదా సింగిల్ సూపర్ ఫాస్ఫేట్ తో కలిపి నేరుగా వాడవద్దు.",
                    "hi": "जिंक सल्फेट को डीएपी या फॉस्फोरस वाली खाद के साथ मिलाकर न डालें।"
                },
                "source": "ICAR-IARI Division of Soil Science Advisory"
            },
            "borer": {
                "title": {"en": "Fruit Borer & Caterpillar Damage", "te": "కాయతొలుచు పురుగు (హెలికోవెర్పా / లద్దెపురుగు)", "hi": "फल छेदक कीट एवं इल्ली का प्रकोप"},
                "happening": {
                    "en": "Helicoverpa armigera and Spodoptera larvae bore into flower buds and green fruits, leaving hollowed fruits with entry holes.",
                    "te": "కాయతొలుచు పురుగులు పూమొగ్గలు మరియు కాయలకు రంధ్రాలు చేసి లోపలి భాగాన్ని తిని నష్టం కలిగిస్తాయి.",
                    "hi": "फल छेदक कीट की इल्लियां फूल और फलों में छेद करके अंदर का भाग खाती हैं, जिससे फल खराब होकर गिर जाते हैं।"
                },
                "check": {
                    "en": "Look for bore holes on fruits, dropped flowers, and frass (caterpillar excreta) near the calyx.",
                    "te": "కాయలపై రంధ్రాలు, రాలిపోయిన పూలు, మరియు పురుగుల మల విసర్జనను గమనించండి.",
                    "hi": "फलों पर छेद, गिरे हुए फूल और फल के पास इल्ली का मल देखें।"
                },
                "actions": {
                    "en": "• Install pheromone traps @ 5/acre for moth monitoring.\n• Spray Bacillus thuringiensis (Bt) @ 2 g/L or Neem formulation @ 2 ml/L.\n• For economic threshold breach, apply Emamectin Benzoate 5% SG @ 0.4 g/L or Chlorantraniliprole 18.5% SC @ 0.3 ml/L strictly following label rates.",
                    "te": "• లింగాకర్షక బుట్టలు ఎకరానికి 5 అమర్చి పురుగుల ఉధృతిని గమనించండి.\n• నివారణకు బి.టి (Bt) 2 గ్రా/లీ లేదా వేప నూనె 2 మి.లీ/లీ పిచికారీ చేయండి.\n• ఉధృతి ఎక్కువగా ఉంటే ఇమామెక్టిన్ బెంజోయేట్ 5% SG 0.4 గ్రా/లీ లేదా క్లోరాంట్రానిలిప్రోల్ 18.5% SC 0.3 మి.లీ/లీ పిచికారీ చేయండి.",
                    "hi": "• प्रति एकड़ 5 फेरोमोन ट्रैप लगाएं।\n• रोकथाम के लिए बीटी (Bt) 2 ग्राम/लीटर या नीम तेल 2 मिली/लीटर का छिड़काव करें।\n• अधिक प्रकोप होने पर इमामेक्टिन बेंजोएट 5% SG 0.4 ग्राम/लीटर या क्लोरेंट्रानिलिप्रोल 18.5% SC 0.3 मिली/लीटर का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Observe pre-harvest interval (PHI) before picking fruits. Never spray when honeybees are actively pollinating.",
                    "te": "కాయ కోతకు ముందు నిర్దేశిత కాల వ్యవధి (PHI) పాటించండి. తేనెటీగలు తిరిగే వేళల్లో స్ప్రే చేయవద్దు.",
                    "hi": "तुड़ाई से पहले प्रतीक्षा अवधि (PHI) का ध्यान रखें। परागण के समय दिन में छिड़काव न करें।"
                },
                "source": "ICAR-CRIDA IPM Technical Bulletin & State Agricultural University Guidelines"
            },
            "blight_spots": {
                "title": {"en": "Dieback, Anthracnose & Leaf Spot", "te": "కొమ్మ ఎండు తెగులు, ఆకుమచ్చ & కాయకుళ్లు తెగులు", "hi": "एंथ्रेक्नोज (डाइबैक) एवं पत्ती धब्बा रोग"},
                "happening": {
                    "en": "Fungal pathogens (Colletotrichum / Cercospora) cause circular dark brown spots with concentric rings on leaves and twig dieback from tip downwards.",
                    "te": "శిలీంధ్రాల వల్ల ఆకులపై నల్లటి వలయాలతో కూడిన మచ్చలు ఏర్పడటం మరియు కొమ్మ పైనుండి కిందికి ఎండిపోవడం (కొమ్మ ఎండు తెగులు) జరుగుతుంది.",
                    "hi": "फफूंद के कारण पत्तियों पर गोल भूरे-काले धब्बे बनते हैं और टहनियां ऊपर से नीचे की ओर सूखने लगती हैं।"
                },
                "check": {
                    "en": "Check for sunken circular spots on fruits and blackened drying twigs starting from top tips.",
                    "te": "కాయలపై గుండ్రటి నల్లటి మచ్చలు మరియు పై కొమ్మలు ఎండిపోవడం గమనించండి.",
                    "hi": "फलों पर धंसे हुए काले धब्बे और टहनियों के ऊपरी सिरे का सूखना जांचें।"
                },
                "actions": {
                    "en": "• Prune and burn infected dried twigs.\n• Spray Trichoderma viride @ 5 g/L as bio-preventive.\n• For disease outbreak, apply Copper Oxychloride 50% WP @ 2.5–3 g/L or Mancozeb 75% WP @ 2.5 g/L on complete foliage.",
                    "te": "• ఎండిపోయిన కొమ్మలను కత్తిరించి నాశనం చేయండి.\n• నివారణకు కాపర్ ఆక్సీక్లోరైడ్ 50% WP 3 గ్రా/లీ లేదా మ్యాంకోజెబ్ 75% WP 2.5 గ్రా/లీ పిచికారీ చేయండి.",
                    "hi": "• सूखी टहनियों को काटकर नष्ट करें।\n• रोकथाम के लिए कॉपर ऑक्सीक्लोराइड 50% WP 3 ग्राम/लीटर या मैंकोजेब 75% WP 2.5 ग्राम/लीटर का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Ensure complete canopy coverage. Do not spray right before rain; wait until foliage dries.",
                    "te": "మొక్క మొత్తం తడిసేలా పిచికారీ చేయండి. వర్షం పడే ముందు స్ప్రే చేయవద్దు.",
                    "hi": "पत्तियों के दोनों तरफ छिड़काव करें। बारिश से ठीक पहले छिड़काव न करें।"
                },
                "source": "ICAR-IARI Plant Pathology Advisory"
            }
        }
    },

    "Tomato": {
        "name": {"en": "Tomato", "te": "టమోటా", "hi": "टमाटर"},
        "suitable_seasons": {"en": "Kharif (June–July), Rabi (October–November), Summer (Jan–Feb with irrigation)", "te": "ఖరీఫ్ (జూన్–జూలై), రబీ (అక్టోబర్–నవంబర్), వేసవి (జనవరి–ఫిబ్రవరి నీటి వసతితో)", "hi": "खरीफ (जून-जुलाई), रबी (अक्टूबर-नवंबर), जायद (जनवरी-फरवरी)"},
        "suitable_soils": {"en": "Deep, well-drained sandy loam or clay loam rich in organic matter (pH 6.0–7.0)", "te": "సేంద్రీయ పదార్థం సమృద్ధిగా ఉన్న ఇసుక నేలలు లేదా గరప నేలలు (pH 6.0–7.0)", "hi": "जीवांश युक्त बलुई दोमट या दोमट मिट्टी (pH 6.0–7.0)"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Tomato", "te": "టమోటా ఎరువుల యాజమాన్యం", "hi": "टमाटर के लिए पोषक तत्व एवं खाद प्रबंधन"},
            "happening": {
                "en": "Tomato requires steady nitrogen and phosphorus during vegetative phase, high potassium and calcium during fruit development to prevent blossom end rot and fruit cracking.",
                "te": "టమోటా పంటకు మొదట్లో నత్రజని, భాస్వరం మరియు కాయ ఊరే దశలో పొటాషియం, కాల్షియం ఎంతో ముఖ్యం. ఇవి కాయ నాణ్యతను పెంచి కాయ పగుళ్లు, మచ్చలు రాకుండా చేస్తాయి.",
                "hi": "टमाटर में अच्छी बढ़वार के लिए एनपीके और फलों के विकास के समय पोटाश तथा कैल्शियम की आवश्यकता होती है।"
            },
            "check": {
                "en": "Inspect fruit bottoms for dark sunken patches (calcium deficiency) and leaves for pale yellowing.",
                "te": "కాయల అడుగు భాగాన నల్లటి మచ్చలు (కాల్షియం లోపం) మరియు ఆకులు పసుపుబారడాన్ని గమనించండి.",
                "hi": "फलों के निचले हिस्से पर काले धब्बे (कैल्शियम की कमी) और पत्तियों का पीलापन जांचें।"
            },
            "actions": {
                "en": "• Basal: 10 tonnes FYM/acre + 50 kg DAP + 25 kg MOP.\n• Vegetative stage: Apply 19:19:19 @ 4–5 g/L foliar spray.\n• Flowering & Fruit Set: Spray 0:52:34 @ 5 g/L + Boron @ 1 g/L to enhance fruit set.\n• Fruit Enlargement: Foliar spray of Calcium Nitrate @ 2 g/L + Potassium Nitrate @ 5 g/L for fruit firmness.",
                "te": "• ఆఖరి దుక్కిలో: ఎకరానికి 10 టన్నుల పశువుల ఎరువు + 50 కిలోల డీఏపీ + 25 కిలోల పొటాష్.\n• పెరుగుదల దశలో: 19:19:19 ఎరువు 5 గ్రా/లీ పిచికారీ చేయండి.\n• పూత మరియు పిందె దశలో: 0:52:34 (5 గ్రా/లీ) + బోరాన్ (1 గ్రా/లీ) పిచికారీ చేయండి.\n• కాయ దశలో: కాల్షియం నైట్రేట్ 2 గ్రా/లీ + 13:0:45 (5 గ్రా/లీ) పిచికారీ చేయండి.",
                "hi": "• बुवाई के समय: 10 टन सड़ी गोबर की खाद + डीएपी + पोटाश दें।\n• वृद्धि अवस्था: 19:19:19 घुलनशील खाद 5 ग्राम/लीटर का छिड़काव करें।\n• फूल व फल बनते समय: 0:52:34 (5 ग्राम/लीटर) + बोरॉन (1 ग्राम/लीटर) दें।\n• फल विकास: कैल्शियम नाइट्रेट 2 ग्राम/लीटर का छिड़काव करें।"
            },
            "precautions": {
                "en": "Maintain uniform soil moisture. Erratic watering causes blossom end rot and fruit cracking.",
                "te": "నేలలో తేమ హెచ్చుతగ్గులు లేకుండా క్రమపద్ధతిలో నీరు అందించండి, లేకుంటే కాయలు పగులుతాయి.",
                "hi": "सिंचाई में नियमितता रखें, अनियमित पानी देने से फल फटने की समस्या आती है।"
            },
            "source": "ICAR-IIHR Tomato Production Technology"
        },
        "symptoms": {
            "leaf_curl": {
                "title": {"en": "Tomato Leaf Curl Virus (TYLCV) & Whiteflies", "te": "టమోటా ఆకుముడత వైరస్ తెగులు & తెల్లదోమ", "hi": "टमाटर पत्ती मरोड़ विषाणु (लीफ कर्ल) एवं सफेद मक्खी"},
                "happening": {
                    "en": "Tomato Leaf Curl Virus (transmitted by Whitefly, Bemisia tabaci) causes severe upward curling, stunted bushy growth, and thick yellow chlorotic leaves with flower dropping.",
                    "te": "తెల్లదోమ ద్వారా వ్యాపించే జెమిని వైరస్ వల్ల ఆకులు పైకి ముడుచుకుని, మొక్క గిడసబారిపోయి గుబురుగా మారుతుంది. పూత రాలిపోతుంది.",
                    "hi": "सफेद मक्खी द्वारा फैलने वाले लीफ कर्ल वायरस के कारण पत्तियां ऊपर मुड़ जाती हैं, पौधा छोटा रह जाता है और फूल नहीं बनते।"
                },
                "check": {
                    "en": "Shake the upper canopy gently to see tiny white fluttering flies. Inspect leaves for upward cupping and yellow vein netting.",
                    "te": "పై కొమ్మలను కదిపితే తెల్లటి చిన్న పురుగులు ఎగరడం గమనించవచ్చు. ఆకులు పైకి గిన్నెలా ముడుచుకుంటాయి.",
                    "hi": "पौधे को हिलाने पर छोटी सफेद मक्खियां उड़ती दिखेंगी और पत्तियां ऊपर की तरफ कटोरीनुमा मुड़ जाती हैं।"
                },
                "actions": {
                    "en": "• Install 15–20 yellow sticky traps per acre to trap whitefly vectors.\n• Spray Neem oil (10,000 ppm) @ 2 ml/L on lower leaf surfaces.\n• For vector control, apply Imidacloprid 17.8% SL @ 0.5 ml/L or Cyantraniliprole 10.26% OD @ 1.8 ml/L strictly following product label.\n• Rogue out and bury severely infected stunted plants early.",
                    "te": "• ఎకరానికి 15–20 పసుపు రంగు జిగురు అట్టలు అమర్చి తెల్లదోమను అరికట్టండి.\n• నివారణకు వేపనూనె (10,000 ppm) 2 మి.లీ/లీటరు పిచికారీ చేయండి.\n• ఉధృతి ఎక్కువగా ఉంటే ఇమిడాక్లోప్రిడ్ 17.8% SL 0.5 మి.లీ/లీ పిచికారీ చేయండి.\n• బాగా ముదిరిన వైరస్ సోకిన మొక్కలను పీకి నాశనం చేయండి.",
                    "hi": "• सफेद मक्खी की रोकथाम हेतु प्रति एकड़ 15-20 पीले चिपचिपे ट्रैप लगाएं।\n• रोकथाम के लिए नीम तेल 2 मिली/लीटर का छिड़काव करें।\n• अधिक प्रकोप होने पर इमिडाक्लोप्रिड 17.8% SL (0.5 मिली/लीटर) का छिड़काव करें।\n• गंभीर रूप से ग्रसित पौधों को उखाड़कर नष्ट कर दें।"
                },
                "precautions": {
                    "en": "Insecticide kills the whitefly vector but cannot cure already infected virus plants. Focus on early vector suppression.",
                    "te": "కీటకనాశిని తెల్లదోమను మాత్రమే చంపుతుంది కానీ వైరస్ సోకిన మొక్కను బాగు చేయలేదు. ప్రారంభంలోనే జాగ్రత్తలు తీసుకోండి.",
                    "hi": "दवा केवल सफेद मक्खी को मारती है, वायरस लगे पौधे को ठीक नहीं करती। शुरुआत में ही नियंत्रण करें।"
                },
                "source": "ICAR-IIHR Tomato Disease Management Advisory"
            },
            "blight_spots": {
                "title": {"en": "Early Blight & Late Blight", "te": "ముందస్తు & ఆలస్యపు ఆకుమచ్చ / మాడ తెగులు", "hi": "टमाटर का अगेती एवं पछेती झुलसा रोग"},
                "happening": {
                    "en": "Early blight (Alternaria solani) causes target-board concentric circular dark brown spots on lower leaves. Late blight (Phytophthora infestans) causes water-soaked dark lesions during cool humid weather.",
                    "te": "ఆల్టర్నేరియా శిలీంధ్రం వల్ల కింది ఆకులపై గుండ్రటి వలయాలతో కూడిన నల్లటి మచ్చలు ఏర్పడతాయి. తేమ వాతావరణంలో తెగులు వేగంగా వ్యాపిస్తుంది.",
                    "hi": "अगेती झुलसा में पत्तियों पर छल्लेदार गोल भूरे धब्बे बनते हैं और पछेती झुलसा में ठंडे नम मौसम में पत्तियां झुलस कर काली पड़ जाती हैं।"
                },
                "check": {
                    "en": "Inspect lower leaves for concentric circular spots ('target board' pattern) and dark water-soaked patches on fruits.",
                    "te": "కింది ఆకులపై గుండ్రటి వలయాల మచ్చలు మరియు కాయలపై నల్లటి మచ్చలు ఉన్నాయో లేదో పరిశీలించండి.",
                    "hi": "निचली पत्तियों पर गोल छल्लेदार धब्बे और फलों पर काले धब्बे देखें।"
                },
                "actions": {
                    "en": "• Remove and destroy infected lower foliage touching the soil.\n• Spray bio-agent Trichoderma viride @ 5 g/L as a preventive.\n• Apply Mancozeb 75% WP @ 2.5 g/L or Copper Oxychloride 50% WP @ 2.5–3 g/L covering complete plant canopy.",
                    "te": "• నేలను తాకుతున్న తెగులు సోకిన కింది ఆకులను తుంచి నాశనం చేయండి.\n• నివారణకు మ్యాంకోజెబ్ 75% WP 2.5 గ్రా/లీ లేదా కాపర్ ఆక్సీక్లోరైడ్ 3 గ్రా/లీ కలిపి పిచికారీ చేయండి.",
                    "hi": "• नीचे की रोगग्रस्त पत्तियों को तोड़कर नष्ट कर दें।\n• रोकथाम के लिए मैंकोजेब 75% WP (2.5 ग्राम/लीटर) या कॉपर ऑक्सीक्लोराइड (3 ग्राम/लीटर) का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Avoid overhead sprinkler irrigation during cloudy weather as wet foliage accelerates fungal spore germination.",
                    "te": "మబ్బు వాతావరణంలో పైనుండి నీరు చిమ్మవద్దు, తేమ వల్ల శిలీంధ్రం వేగంగా వ్యాపిస్తుంది.",
                    "hi": "फव्वारा विधि से पानी न दें, पत्तियों पर नमी रहने से फफूंद तेजी से फैलती है।"
                },
                "source": "ICAR-IARI Division of Plant Pathology Bulletin"
            },
            "borer": {
                "title": {"en": "Tomato Fruit Borer (Helicoverpa armigera)", "te": "టమోటా కాయతొలుచు పురుగు", "hi": "टमाटर का फल छेदक कीट"},
                "happening": {
                    "en": "Stout greenish-brown caterpillars bore circular holes into green and ripe fruits, keeping half their body outside while feeding.",
                    "te": "ఆకుపచ్చ-గోధుమ రంగు లద్దెపురుగులు కాయలకు గుండ్రటి రంధ్రాలు చేసి సగం శరీరాన్ని బయట ఉంచి కాయ లోపలి గుజ్జును తింటాయి.",
                    "hi": "इल्लियां टमाटर के हरे और पके फलों में गोल छेद करके अंदर का गूदा खाती हैं।"
                },
                "check": {
                    "en": "Look for bore holes on fruits, premature fruit rotting, and caterpillars near flower trusses.",
                    "te": "కాయలపై రంధ్రాలు, కుళ్లిన కాయలు, పూమొగ్గల వద్ద పురుగులను గమనించండి.",
                    "hi": "फलों पर छेद और सड़े हुए फल की जांच करें।"
                },
                "actions": {
                    "en": "• Install 5 pheromone traps (Helilure) per acre for moth monitoring.\n• Plant African marigold (1 row for every 16 rows of tomato) as a trap crop.\n• Spray Bacillus thuringiensis (Bt) @ 2 g/L or Neem seed extract (NSKE 5%).\n• In severe damage, apply Emamectin Benzoate 5% SG @ 0.4 g/L or Chlorantraniliprole 18.5% SC @ 0.3 ml/L.",
                    "te": "• ఎకరానికి 5 లింగాకర్షక బుట్టలు అమర్చండి.\n• ఎరపంటగా ప్రతి 16 వరుసల టమోటాకు ఒక వరుస బంతిని నాటండి.\n• నివారణకు బి.టి 2 గ్రా/లీ లేదా వేప నూనె 2 మి.లీ/లీ పిచికారీ చేయండి.\n• ఉధృతి ఎక్కువగా ఉంటే ఇమామెక్టిన్ బెంజోయేట్ 5% SG 0.4 గ్రా/లీ లేదా క్లోరాంట్రానిలిప్రోల్ 0.3 మి.లీ/లీ పిచికారీ చేయండి.",
                    "hi": "• प्रति एकड़ 5 फेरोमोन ट्रैप लगाएं।\n• ट्रैप फसल के रूप में गेंदा का पौधा लगाएं।\n• रोकथाम के लिए बीटी (2 ग्राम/लीटर) या नीम तेल का छिड़काव करें।\n• अधिक प्रकोप पर इमामेक्टिन बेंजोएट 5% SG (0.4 ग्राम/लीटर) का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Collect and destroy all bored fallen fruits to break the pest life cycle. Respect pre-harvest intervals.",
                    "te": "రంధ్రాలు పడిన కాయలను ఏరి నాశనం చేయండి. కోతకు ముందు నిర్దేశిత గడువు పాటించండి.",
                    "hi": "कीट लगे फलों को इकट्ठा करके नष्ट कर दें ताकि कीट आगे न फैले।"
                },
                "source": "ICAR-IIHR Vegetable Pest Management Guide"
            }
        }
    },

    "Cotton": {
        "name": {"en": "Cotton", "te": "పత్తి", "hi": "कपास"},
        "suitable_seasons": {"en": "Kharif (May–July sowing)", "te": "ఖరీఫ్ (మే–జూలై విత్తే సమయం)", "hi": "खरीफ (मई-जुलाई)"},
        "suitable_soils": {"en": "Deep black cotton soils (Vertisols) with good water retention and pH 7.0–8.0", "te": "తేమను నిలుపుకునే నల్లరేగడి నేలలు (pH 7.0–8.0)", "hi": "गहरी काली कपास मिट्टी (वर्टिसोल) जिसमें नमी रोकने की क्षमता हो (pH 7.0–8.0)"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Cotton", "te": "పత్తి సమగ్ర ఎరువుల యాజమాన్యం", "hi": "कपास के लिए संतुलित उर्वरक प्रबंधन"},
            "happening": {
                "en": "Cotton is a heavy feeder requiring balanced NPK in splits to support vegetative growth, square formation, and boll development without triggering vegetative rank growth.",
                "te": "పత్తి పంటకు బ్యాలెన్స్డ్ ఎరువులు అవసరం. పూత, కాయ దశలలో సరైన పోషకాలు అందిస్తే కాయలు రాలకుండా అధిక దిగుబడి వస్తుంది.",
                "hi": "कपास में वानस्पतिक वृद्धि और टिंडों के विकास के लिए संतुलित एनपीके और मैग्नीशियम की आवश्यकता होती है।"
            },
            "check": {
                "en": "Inspect plant growth stage (squaring at 35 DAS, flowering at 60 DAS). Check for reddening of leaves (magnesium deficiency).",
                "te": "పూత మొగ్గ దశ మరియు ఆకులు ఎర్రబడటం (మెగ్నీషియం లోపం) ఉన్నాయో లేదో గమనించండి.",
                "hi": "फूल आने की अवस्था और पत्तियों का लाल होना (मैग्नीशियम की कमी) जांचें।"
            },
            "actions": {
                "en": "• Basal: FYM @ 5 tonnes/acre + 25 kg DAP + 20 kg MOP + 10 kg Zinc Sulphate.\n• Square formation (35 DAS): Top dress Urea @ 25 kg/acre.\n• Flowering & Boll development (60-75 DAS): Top dress Urea @ 25 kg/acre + 15 kg MOP.\n• Foliar spray: Spray 2% DAP or Potassium Nitrate (13:0:45) @ 10 g/L + Magnesium Sulphate @ 10 g/L to prevent leaf reddening.",
                "te": "• ఆఖరి దుక్కిలో: ఎకరానికి 5 టన్నుల పశువుల ఎరువు + 25 కిలోల డీఏపీ + 20 కిలోల పొటాష్ + 10 కిలోల జింక్ సల్ఫేట్.\n• 35 రోజుల వద్ద: ఎకరానికి 25 కిలోల యూరియా వేయండి.\n• పూత, కాయ దశలో: 25 కిలోల యూరియా + 15 కిలోల పొటాష్ వేయండి.\n• ఆకులు ఎర్రబడకుండా 13:0:45 (10 గ్రా/లీ) + మెగ్నీషియం సల్ఫేట్ (10 గ్రా/లీ) పిచికారీ చేయండి.",
                "hi": "• बुवाई के समय: 5 टन गोबर खाद + 25 किग्रा डीएपी + 20 किग्रा पोटाश प्रति एकड़ दें।\n• 35 दिन पर: 25 किग्रा यूरिया प्रति एकड़ दें।\n• फूल व टिंडे बनते समय: 25 किग्रा यूरिया + 15 किग्रा पोटाश दें।\n• पत्ते लाल होने से रोकने हेतु 13:0:45 (10 ग्राम/लीटर) + मैग्नीशियम सल्फेट (10 ग्राम/लीटर) का छिड़काव करें।"
            },
            "precautions": {
                "en": "Never apply excess nitrogen under cloudy skies, as it causes excessive vegetative growth (rank growth) and attracts sucking pests.",
                "te": "మబ్బు వాతావరణంలో యూరియా ఎక్కువ వేయవద్దు, దీనివల్ల మొక్క ఏపుగా పెరిగి పురుగులు ఎక్కువవుతాయి.",
                "hi": "बादल छाए रहने पर अधिक यूरिया न दें, इससे वानस्पतिक वृद्धि अधिक होती है और कीट बढ़ते हैं।"
            },
            "source": "ICAR-CICR Nagpur & ANGRAU Cotton Production Guidelines"
        },

        "symptoms": {
            "leaf_curl": {
                "title": {"en": "Cotton Sucking Pests (Whitefly, Jassids & Thrips)", "te": "పత్తిలో రసం పీల్చే పురుగులు (తెల్లదోమ, పచ్చదోమ, తామర పురుగులు)", "hi": "कपास के रस चूसक कीट (सफेद मक्खी, हरा तेला, थ्रिप्स)"},
                "happening": {
                    "en": "Whiteflies and jassids suck sap from the lower leaf surface, causing downward leaf cupping ('hopper burn') and yellow leaf margins.",
                    "te": "పచ్చదోమ, తెల్లదోమ ఆకుల అడుగునుండి రసం పీల్చడం వల్ల ఆకుల అంచులు పసుపుబారి, దోనెల్లా కిందికి ముడుచుకుపోతాయి.",
                    "hi": "सफेद मक्खी और हरा तेला पत्तियों की निचली सतह से रस चूसते हैं, जिससे पत्तियां नीचे की ओर मुड़ जाती हैं और किनारे पीले पड़ जाते हैं।"
                },
                "check": {
                    "en": "Examine 20 leaves across the field. If jassids exceed 2 per leaf or whiteflies exceed 6–8 adults per leaf, threshold is breached.",
                    "te": "పొలంలో ఆకుల అడుగు భాగాన్ని పరిశీలించండి. ఆకుకు 2 పచ్చదోమలు లేదా 6–8 తెల్లదోమలు కనిపిస్తే నివారణ చర్యలు చేపట్టాలి.",
                    "hi": "पत्तियों की निचली सतह पर सफेद मक्खी और हरे तेले की संख्या जांचें।"
                },
                "actions": {
                    "en": "• Install 15 yellow sticky traps per acre for whitefly.\n• Spray Neem oil (10,000 ppm) @ 2 ml/L or NSKE 5%.\n• Apply Flonicamid 50% WG @ 0.3 g/L or Diafenthiuron 50% WP @ 1.2 g/L adhering strictly to CIBRC label.",
                    "te": "• ఎకరానికి 15 పసుపు రంగు జిగురు అట్టలు అమర్చండి.\n• నివారణకు వేపనూనె 2 మి.లీ/లీటరు పిచికారీ చేయండి.\n• ఉధృతి ఎక్కువగా ఉంటే ఫ్లోనికామిడ్ 50% WG 0.3 గ్రా/లీ లేదా డయాఫెంథియురాన్ 1.2 గ్రా/లీ పిచికారీ చేయండి.",
                    "hi": "• प्रति एकड़ 15 पीले चिपचिपे ट्रैप लगाएं।\n• रोकथाम हेतु नीम तेल 2 मिली/लीटर का छिड़काव करें।\n• अधिक प्रकोप होने पर फ्लोनिकामाइड 50% WG (0.3 ग्राम/लीटर) का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Avoid synthetic pyrethroids in early vegetative stage as they trigger massive whitefly resurgence.",
                    "te": "ప్రారంభ దశలో సింథటిక్ పైరెథ్రాయిడ్ మందులు వాడవద్దు, దీనివల్ల తెల్లదోమ విపరీతంగా పెరుగుతుంది.",
                    "hi": "शुरुआती अवस्था में पाइरेथ्रोइड कीटनाशकों का प्रयोग न करें।"
                },
                "source": "ICAR-CICR (Central Institute for Cotton Research) IPM Advisory"
            },
            "borer": {
                "title": {"en": "Pink Bollworm (Pectinophora gossypiella)", "te": "గులాబీ రంగు కాయతొలుచు పురుగు", "hi": "गुलाबी सुंडी (पिंक बॉलवर्म)"},
                "happening": {
                    "en": "Pink bollworm larvae enter developing bolls directly through the carpel wall, feeding on seeds and staining lint.",
                    "te": "గులాబీ రంగు పురుగులు లేత కాయలను తొలిచి లోపలి గింజలను తింటూ దూదిని పాడుచేస్తాయి.",
                    "hi": "गुलाबी सुंडी के लार्वा कपास के टिंडों (बॉल्स) में घुसकर बीजों को खाते हैं और कपास की रुई को खराब करते हैं।"
                },
                "check": {
                    "en": "Inspect flowers for 'rosette flower' symptom (petals twisted closed). Cut open 20 green bolls; look for pinkish caterpillars inside.",
                    "te": "పువ్వులు ముడుచుకుపోయి 'రోసెట్' ఆకారంలో ఉండటం గమనించండి. లేత కాయలను కోసి చూస్తే లోపల గులాబీ రంగు పురుగులు కనిపిస్తాయి.",
                    "hi": "गुलाब जैसे मुड़े हुए फूल और टिंडों को काटकर अंदर गुलाबी रंग की इल्लियां देखें।"
                },
                "actions": {
                    "en": "• Install 5 pheromone traps (Pectino-lure) per acre for monitoring.\n• Release egg parasitoid Trichogramma bactrae @ 60,000/acre at 60–90 DAS.\n• For economic threshold (8 moths/trap/night for 3 consecutive days), apply Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Emamectin Benzoate 5% SG @ 0.4 g/L.",
                    "te": "• ఎకరానికి 5 లింగాకర్షక బుట్టలు అమర్చండి.\n• ట్రైకోగ్రామా పరాన్నజీవులను విడుదల చేయండి.\n• ఉధృతి ఎక్కువగా ఉంటే క్లోరాంట్రానిలిప్రోల్ 0.3 మి.లీ/లీ లేదా ఇమామెక్టిన్ బెంజోయేట్ 0.4 గ్రా/లీ పిచికారీ చేయండి.",
                    "hi": "• प्रति एकड़ 5 फेरोमोन ट्रैप लगाएं।\n• ट्राइकोग्रामा परजीवी छोड़ें।\n• अधिक प्रकोप होने पर क्लोरेंट्रानिलिप्रोल (0.3 मिली/लीटर) या इमामेक्टिन बेंजोएट (0.4 ग्राम/लीटर) का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Do not extend the crop beyond 150–160 days. Grazing sheep after final picking breaks the carryover cycle.",
                    "te": "పంట కాలాన్ని అనవసరంగా పొడిగించవద్దు. చివరి కోత తర్వాత పశువులను లేదా గొర్రెలను పొలంలో మేపడం మంచిది.",
                    "hi": "फसल चक्र को अनावश्यक रूप से लंबा न खींचें।"
                },
                "source": "ICAR-CICR Pink Bollworm Management Strategy"
            }
        }
    },

    "Paddy": {
        "name": {"en": "Paddy / Rice", "te": "వరి", "hi": "धान"},
        "suitable_seasons": {"en": "Kharif (June–July sowing), Rabi (Nov–Dec sowing)", "te": "ఖరీఫ్ (జూన్–జూలై), రబీ (నవంబర్–డిసెంబర్)", "hi": "खरीफ (जून-जुलाई), रबी (नवंबर-दिसंबर)"},
        "suitable_soils": {"en": "Heavy clay or clay loams with high water retention capacity (pH 5.5–7.5)", "te": "తేమను నిలిపి ఉంచే బరువైన నల్లరేగడి లేదా బంకమట్టి నేలలు", "hi": "अधिक जल धारण क्षमता वाली चिकनी या दोमट मिट्टी"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Paddy (Rice)", "te": "వరి సమగ్ర ఎరువుల యాజమాన్యం", "hi": "धान (चावल) के लिए संतुलित उर्वरक प्रबंधन"},
            "happening": {
                "en": "Paddy requires split nitrogen application, basal phosphorus, and split potassium to promote tillering, strong culms, and filled grains without lodging.",
                "te": "వరిలో ఎక్కువ పిలకలు రావడానికి, గింజ గట్టిపడటానికి మరియు పైరు పడిపోకుండా ఉండటానికి సమయానికి ఎరువులు వేయడం ముఖ్యం.",
                "hi": "धान में अधिक कल्ले फूटने और भरपूर दाना भरने के लिए नाइट्रोजन का तीन बार में और पोटाश का दो बार में उपयोग आवश्यक है।"
            },
            "check": {
                "en": "Check tillering stage (20-25 DAT) and panicle initiation (40-45 DAT). Observe leaf color using Leaf Color Chart (LCC).",
                "te": "పిలకల దశ (20-25 రోజులు) మరియు చిరుపొట్ట దశ (40-45 రోజులు) గమనించండి.",
                "hi": "कल्ले निकलने की अवस्था (20-25 दिन) और बालियां बनने की अवस्था (40-45 दिन) जांचें।"
            },
            "actions": {
                "en": "• Basal (Last Puddling): 50 kg SSP (or 25 kg DAP) + 20 kg MOP + 10 kg Zinc Sulphate per acre.\n• Active Tillering (20-25 DAT): Top-dress Urea @ 25 kg/acre.\n• Panicle Initiation (40-45 DAT): Top-dress Urea @ 20 kg/acre + 15 kg MOP.\n• Grain filling: Foliar spray of 13:0:45 @ 5 g/L to improve grain weight.",
                "te": "• ఆఖరి దమ్ము లో: ఎకరానికి 50 కిలోల సింగిల్ సూపర్ ఫాస్ఫేట్ + 20 కిలోల పొటాష్ + 10 కిలోల జింక్ సల్ఫేట్.\n• పిలక దశలో: ఎకరానికి 25 కిలోల యూరియా వేయండి.\n• చిరుపొట్ట దశలో: ఎకరానికి 20 కిలోల యూరియా + 15 కిలోల పొటాష్ వేయండి.\n• గింజ పాలుపోసుకునే దశలో 13:0:45 ఎరువు 5 గ్రా/లీ పిచికారీ చేయండి.",
                "hi": "• अंतिम जुताई पर: 50 किग्रा एसएसपी + 20 किग्रा पोटाश + 10 किग्रा जिंक सल्फेट प्रति एकड़ डालें।\n• कल्ले फूटते समय: 25 किग्रा यूरिया प्रति एकड़ दें।\n• बालियां निकलते समय: 20 किग्रा यूरिया + 15 किग्रा पोटाश दें।\n• दाना भरते समय 13:0:45 (5 ग्राम/लीटर) का छिड़काव करें।"
            },
            "precautions": {
                "en": "Drain standing water before top dressing fertilizers and irrigate lightly 24 hours later. Never apply zinc with DAP simultaneously.",
                "te": "యూరియా వేసే ముందు పొలంలో నీటిని తీసివేసి, మరుసటి రోజు పలుచగా నీరు పెట్టండి. జింక్ మరియు డిఎపి కలిపి వేయవద్దు.",
                "hi": "उर्वरक डालते समय खेत से पानी निकाल दें और 24 घंटे बाद हल्की सिंचाई करें।"
            },
            "source": "ICAR-NRRI Cuttack & CRIDA Rice Production Protocols"
        },

        "symptoms": {
            "borer": {
                "title": {"en": "Yellow Stem Borer (Scirpophaga incertulas)", "te": "వరి కాండం తొలుచు పురుగు", "hi": "धान का तना छेदक कीट"},
                "happening": {
                    "en": "Larvae bore into the central leaf sheath causing 'Deadheart' (drying of central tiller) in vegetative stage and 'White earhead' (empty chaffy grains) at heading stage.",
                    "te": "పురుగు కాండంలోనికి తొలిచి తినడం వల్ల పిలక దశలో 'ఎండిన మొవ్వు' (డెడ్ హార్ట్), ఈనిన దశలో 'తెల్ల కంకి' ఏర్పడతాయి.",
                    "hi": "कीट के लार्वा तने के अंदर घुसकर खाते हैं, जिससे कल्ले सूख जाते हैं (डेड हार्ट) और बाली आने पर सफेद बालियां (खोखली) निकलती हैं।"
                },
                "check": {
                    "en": "Pull central shoots gently; if they detach easily and show a chewed base, it is stem borer.",
                    "te": "ఎండిన మొవ్వును పైకి లాగితే తేలికగా వచ్చేస్తుంది, మొదలు వద్ద పురుగు తొలచిన రంధ్రాలు కనిపిస్తాయి.",
                    "hi": "सूखे कल्ले को खींचने पर वह आसानी से बाहर निकल आता है और तने पर छेद दिखता है।"
                },
                "actions": {
                    "en": "• Clip seedling tips before transplanting to destroy egg masses.\n• Install pheromone traps @ 5/acre.\n• Apply Cartap Hydrochloride 4G @ 8–10 kg/acre in standing water or spray Chlorantraniliprole 18.5% SC @ 0.3 ml/L strictly following label.",
                    "te": "• నాట్లు వేసేముందు నారు కొనలను తుంచి గుడ్ల సముదాయాలను నాశనం చేయండి.\n• ఎకరానికి 5 లింగాకర్షక బుట్టలు పెట్టండి.\n• పొలంలో పలుచటి నీరు ఉంచి కార్టాప్ హైడ్రోక్లోరైడ్ 4G గుళికలు ఎకరానికి 8–10 కిలోలు వేయండి లేదా క్లోరాంట్రానిలిప్రోల్ 0.3 మి.లీ/లీ పిచికారీ చేయండి.",
                    "hi": "• रोपाई से पहले पौध के ऊपरी सिरे को काट दें ताकि अंडों के गुच्छे नष्ट हो जाएं।\n• प्रति एकड़ 5 फेरोमोन ट्रैप लगाएं।\n• खेत में पानी रखकर कार्टाप हाइड्रोक्लोराइड 4G (8-10 किग्रा/एकड़) डालें या क्लोरेंट्रानिलिप्रोल का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Maintain standing water of 2–3 cm during granular insecticide application.",
                    "te": "గుళికలు చల్లేటప్పుడు మడిలో 2–3 సెం.మీ నీరు ఉండేలా చూడండి.",
                    "hi": "दानेदार कीटनाशक डालते समय खेत में 2-3 सेमी पानी होना चाहिए।"
                },
                "source": "ICAR-IIRR (Indian Institute of Rice Research) Advisory"
            },
            "blight_spots": {
                "title": {"en": "Rice Blast & Bacterial Leaf Blight", "te": "వరి అగ్గితెగులు & ఎండ తెగులు", "hi": "धान का झुलसा (ब्लास्ट) एवं जीवाणु पत्ती झुलसा"},
                "happening": {
                    "en": "Blast (Magnaporthe oryzae) causes spindle-shaped eye-like lesions with ash-grey centers. Bacterial blight causes yellow water-soaked wavy lesions starting from leaf margins.",
                    "te": "అగ్గితెగులు వల్ల ఆకులపై కంటి ఆకారంలో బూడిద రంగు మచ్చలు ఏర్పడతాయి. ఎండ తెగులు వల్ల ఆకుల అంచుల నుండి పసుపు రంగులోకి మారి ఎండిపోతాయి.",
                    "hi": "ब्लास्ट रोग में पत्तियों पर आंख की आकृति के धब्बे बनते हैं, जबकि जीवाणु झुलसा में पत्तियों के किनारे पीले होकर सूखते हैं।"
                },
                "check": {
                    "en": "Look for spindle-shaped lesions on leaves and brownish discoloration at the node or neck of the earhead.",
                    "te": "ఆకులపై కంటి ఆకారపు మచ్చలు మరియు కంకి మెడ వద్ద నల్లటి మచ్చలు ఉన్నాయో లేదో చూడండి.",
                    "hi": "पत्तियों पर धब्बे और बाली की गर्दन के पास कालापन जांचें।"
                },
                "actions": {
                    "en": "• Avoid excessive nitrogen application.\n• Spray Tricyclazole 75% WP @ 0.6 g/L or Isoprothiolane 40% EC @ 1.5 ml/L for blast prevention.\n• For bacterial blight, apply Copper Oxychloride @ 2.5 g/L with valid extension guidance.",
                    "te": "• అధికంగా నత్రజని వాడకాన్ని తగ్గించండి.\n• అగ్గితెగులు నివారణకు ట్రైసైక్లాజోల్ 75% WP 0.6 గ్రా/లీ లేదా ఐసోప్రోథియోలేన్ 1.5 మి.లీ/లీ పిచికారీ చేయండి.",
                    "hi": "• नाइट्रोजन की अधिक मात्रा न दें।\n• ब्लास्ट की रोकथाम हेतु ट्राइसाइक्लाजोल 75% WP (0.6 ग्राम/लीटर) का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Do not drain floodwater from diseased plots into healthy plots.",
                    "te": "రోగం సోకిన మడిలోని నీటిని ఆరోగ్యంగా ఉన్న ఇతర మడులలోకి పోనివ్వకండి.",
                    "hi": "बीमारी वाले खेत का पानी स्वस्थ खेत में न जाने दें।"
                },
                "source": "ICAR-NRRI (National Rice Research Institute) Protocol"
            }
        }
    },

    "Onion": {
        "name": {"en": "Onion", "te": "ఉల్లిపాయ", "hi": "प्याज"},
        "suitable_seasons": {"en": "Kharif (May–June), Late Kharif (Aug–Sept), Rabi (Oct–Nov)", "te": "ఖరీఫ్ (మే–జూన్), ఆలస్య ఖరీఫ్ (ఆగస్టు–సెప్టెంబర్), రబీ (అక్టోబర్–నవంబర్)", "hi": "खरीफ (मई-जून), पछेती खरीफ (अगस्त-सितंबर), रबी (अक्टूबर-नवंबर)"},
        "suitable_soils": {"en": "Fertile, friable sandy loam rich in organic matter with excellent drainage (pH 6.5–7.5)", "te": "మురుగునీరు నిలవని సారవంతమైన ఇసుక గరప నేలలు (pH 6.5–7.5)", "hi": "उत्तम जल निकासी वाली बलुई दोमट मिट्टी (pH 6.5–7.5)"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Onion", "te": "ఉల్లిపాయ సమగ్ర ఎరువుల యాజమాన్యం", "hi": "प्याज के लिए संतुलित उर्वरक प्रबंधन"},
            "happening": {
                "en": "Onion requires high potassium and sulphur for bulb pungency, firmness, and storage shelf-life, with nitrogen restricted before maturity.",
                "te": "ఉల్లిపాయలో గడ్డ ఊరడానికి, ఘాటు మరియు నిల్వ సామర్థ్యం పెరగడానికి పొటాషియం మరియు గంధకం ఎంతో ముఖ్యం.",
                "hi": "प्याज में कंद के आकार, तीखेपन और भंडारण क्षमता बढ़ाने के लिए पोटाश और सल्फर का विशेष महत्व है।"
            },
            "check": {
                "en": "Check bulb development stage (45-60 DAT). Avoid excess nitrogen late in season.",
                "te": "గడ్డ ఊరే దశ (45-60 రోజులు) గమనించండి.",
                "hi": "कंद बनने की अवस्था (45-60 दिन) की जांच करें।"
            },
            "actions": {
                "en": "• Basal: FYM @ 10 tonnes/acre + 40 kg DAP + 25 kg MOP + 15 kg Sulphur.\n• 30 DAT: Top dress Urea @ 25 kg/acre.\n• 45 DAT (Bulb enlargement): Foliar spray of Potassium Nitrate (13:0:45) @ 5 g/L.\n• Stop nitrogen 30 days before harvest to prevent neck rot in storage.",
                "te": "• ఆఖరి దుక్కిలో: ఎకరానికి 10 టన్నుల పశువుల ఎరువు + 40 కిలోల డీఏపీ + 25 కిలోల పొటాష్ + 15 కిలోల సల్ఫర్.\n• 30 రోజుల వద్ద: ఎకరానికి 25 కిలోల యూరియా వేయండి.\n• 45 రోజుల వద్ద: 13:0:45 ఎరువు 5 గ్రా/లీ పిచికారీ చేయండి.\n• కోతకు నెల రోజుల ముందు నత్రజని ఎరువులు ఆపివేయండి.",
                "hi": "• बुवाई/रोपाई पर: 10 टन गोबर खाद + 40 किग्रा डीएपी + 25 किग्रा पोटाश + 15 किग्रा सल्फर दें।\n• 30 दिन पर: 25 किग्रा यूरिया प्रति एकड़ दें।\n• 45 दिन पर: 13:0:45 (5 ग्राम/लीटर) का छिड़काव करें।\n• खुदाई से 30 दिन पूर्व यूरिया देना बंद कर दें।"
            },
            "precautions": {
                "en": "Excessive late nitrogen produces thick-necked bulbs that rot rapidly during storage.",
                "te": "చివర్లో యూరియా ఎక్కువ వేస్తే మెడ లావెక్కి ఉల్లిపాయలు నిల్వ ఉండవు.",
                "hi": "अंतिम अवस्था में यूरिया देने से कंद की गर्दन मोटी हो जाती है और भंडारण में सड़न बढ़ती है।"
            },
            "source": "ICAR-DOGR Rajgurunagar Onion Production Package"
        },

        "symptoms": {
            "leaf_curl": {
                "title": {"en": "Onion Thrips (Thrips tabaci)", "te": "ఉల్లిలో తామర పురుగులు", "hi": "प्याज के थ्रिप्स"},
                "happening": {
                    "en": "Tiny thrips rasp tender leaf tissue and suck sap, causing silvery white blotches and distorted twisting leaves.",
                    "te": "సన్నటి తామర పురుగులు ఆకుల రసాన్ని పీల్చడం వల్ల ఆకులపై వెండి రంగు మచ్చలు ఏర్పడి ఆకులు మెలితిరిగిపోతాయి.",
                    "hi": "थ्रिप्स पत्तियों का रस चूसते हैं, जिससे पत्तियों पर सफेद-चांदी जैसे धब्बे पड़ते हैं और पत्तियां मुड़ जाती हैं।"
                },
                "check": {
                    "en": "Part the central leaf sheaths at the base and check for small elongated yellowish nymphs.",
                    "te": "ఆకుల మొదలు భాగంలో లోపల పరిశీలిస్తే సన్నటి పసుపు రంగు పురుగులు కనిపిస్తాయి.",
                    "hi": "पत्तियों के जोड़ के पास अंदर देखें, बारीक पीले कीट दिखाई देंगे।"
                },
                "actions": {
                    "en": "• Install 15 blue sticky traps per acre.\n• Spray Neem oil (10,000 ppm) @ 2 ml/L.\n• If severe, spray Fipronil 5% SC @ 2 ml/L or Acetamiprid 20% SP @ 0.5 g/L strictly following label.",
                    "te": "• ఎకరానికి 15 నీలి రంగు జిగురు అట్టలు అమర్చండి.\n• నివారణకు వేపనూనె 2 మి.లీ/లీ పిచికారీ చేయండి.\n• ఉధృతి ఎక్కువగా ఉంటే ఫిప్రోనిల్ 2 మి.లీ/లీ పిచికారీ చేయండి.",
                    "hi": "• प्रति एकड़ 15 नीले चिपचिपे ट्रैप लगाएं।\n• नीम तेल 2 मिली/लीटर का छिड़काव करें।\n• अधिक प्रकोप पर फिप्रोनिल 5% SC (2 मिली/लीटर) का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Add sticking agent (sandovit or soap @ 0.5 ml/L) as onion leaves have a waxy surface that repels spray droplets.",
                    "te": "ఉల్లి ఆకులకు మైనపు పూత ఉండటం వల్ల స్ప్రే ద్రావణంలో తప్పనిసరిగా జిగురు (స్టిక్కర్) కలపాలి.",
                    "hi": "प्याज की पत्तियों पर मोमी परत होने के कारण छिड़काव के घोल में स्टीकर (चिपकाने वाला पदार्थ) जरूर मिलाएं।"
                },
                "source": "ICAR-DOGR (Directorate of Onion and Garlic Research) Advisory"
            }
        }
    },

    "Maize": {
        "name": {"en": "Maize", "te": "మొక్కజొన్న", "hi": "मक्का"},
        "suitable_seasons": {"en": "Kharif (June–July), Rabi (Oct–Nov)", "te": "ఖరీఫ్ (జూన్–జూలై), రబీ (అక్టోబర్–నవంబర్)", "hi": "खरीफ (जून-जुलाई), रबी (अक्टूबर-नवंबर)"},
        "suitable_soils": {"en": "Well-drained deep loamy and clayey soils (pH 6.5–7.5)", "te": "మురుగునీరు నిలవని సారవంతమైన నల్లరేగడి లేదా గరప నేలలు", "hi": "अच्छी जल निकासी वाली दोमट और भारी मिट्टी"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Maize", "te": "మొక్కజొన్న సమగ్ర ఎరువుల యాజమాన్యం", "hi": "मक्का के लिए संतुलित उर्वरक प्रबंधन"},
            "happening": {
                "en": "Maize is an exhaustive crop requiring balanced NPK and Zinc in split applications matching vegetative growth and cob formation.",
                "te": "మొక్కజొన్న వేగంగా పెరిగే పైరు. కంకి బాగా నిండటానికి, నత్రజనిని మూడు దఫాలుగా మరియు జింక్ ను తప్పనిసరిగా వేయాలి.",
                "hi": "मक्का एक अधिक पोषक तत्व चाहने वाली फसल है। भुट्टे में भरपूर दाना भरने के लिए नाइट्रोजन का तीन बार में प्रयोग जरूरी है।"
            },
            "check": {
                "en": "Inspect knee-high stage (30 DAS) and tasseling/silking stages (50-55 DAS).",
                "te": "మోకాలి ఎత్తు దశ (30 రోజులు) మరియు పూత దశ (50-55 రోజులు) గమనించండి.",
                "hi": "घुटने तक ऊंचाई की अवस्था (30 दिन) और नर-मंजरी आने की अवस्था (50-55 दिन) देखें।"
            },
            "actions": {
                "en": "• Basal: FYM @ 5 tonnes/acre + 40 kg DAP + 20 kg MOP + 10 kg Zinc Sulphate.\n• Knee-high stage (30 DAS): Top dress Urea @ 35 kg/acre.\n• Tasseling stage (50-55 DAS): Top dress Urea @ 25 kg/acre with adequate moisture.\n• Cob development: Spray 0:52:34 @ 5 g/L to enhance kernel size.",
                "te": "• ఆఖరి దుక్కిలో: ఎకరానికి 5 టన్నుల పశువుల ఎరువు + 40 కిలోల డీఏపీ + 20 కిలోల పొటాష్ + 10 కిలోల జింక్ సల్ఫేట్.\n• మోకాలి ఎత్తు దశలో (30 రోజులు): ఎకరానికి 35 కిలోల యూరియా వేయండి.\n• పూత/కంకి దశలో (50-55 రోజులు): ఎకరానికి 25 కిలోల యూరియా వేయండి.\n• కంకి గింజ దశలో 0:52:34 ఎరువు 5 గ్రా/లీ పిచికారీ చేయండి.",
                "hi": "• बुवाई पर: 5 टन गोबर खाद + 40 किग्रा डीएपी + 20 किग्रा पोटाश + 10 किग्रा जिंक सल्फेट दें।\n• घुटने की ऊंचाई पर (30 दिन): 35 किग्रा यूरिया प्रति एकड़ दें।\n• मंजर आते समय (50-55 दिन): 25 किग्रा यूरिया दें।\n• दाना बनते समय 0:52:34 (5 ग्राम/लीटर) का छिड़काव करें।"
            },
            "precautions": {
                "en": "Never let the field suffer water stress during tasseling and silking, as drought causes poor pollination and empty cobs.",
                "te": "కంకి మరియు పూత దశలో తేమ కొరత రాకుండా చూడండి, లేకుంటే కంకిలో గింజ నిండదు.",
                "hi": "मंजर और भुट्टा बनते समय पानी की कमी न होने दें, अन्यथा दाने नहीं भरेंगे।"
            },
            "source": "ICAR-IIMR Ludhiana Maize Production Technology"
        },

        "symptoms": {
            "borer": {
                "title": {"en": "Fall Armyworm (Spodoptera frugiperda)", "te": "కత్తెర పురుగు", "hi": "फॉल आर्मीवर्म (सैनिक कीट)"},
                "happening": {
                    "en": "Aggressive caterpillars feed inside the central whorl, creating ragged oblong holes and large piles of sawdust-like frass.",
                    "te": "పురుగులు సుడులలో చేరి లేత ఆకులను కొరికి తిని, చెక్కపొట్టు లాంటి మలాన్ని వదిలివేస్తాయి.",
                    "hi": "इल्लियां पौधे के मुख्य तने/गोभ में घुसकर पत्तियों को बुरी तरह छलनी कर देती हैं और बुरादे जैसा मल छोड़ती हैं।"
                },
                "check": {
                    "en": "Look inside the central whorl for caterpillars with 4 distinct black dots arranged in a square on the 8th abdominal segment.",
                    "te": "సుడులను విప్పి చూడండి. పురుగు వెనుక భాగంలో 4 నల్లటి చుక్కలు చతురస్రాకారంలో ఉంటాయి.",
                    "hi": "पौधे के गोभ में देखें, इल्ली के पिछले हिस्से पर चार काले बिंदु चौकोर आकार में दिखेंगे।"
                },
                "actions": {
                    "en": "• Apply sand + lime mixture (9:1) or dry soil inside central whorls to kill early larvae.\n• Spray Bacillus thuringiensis (Bt) @ 2 g/L or Metarhizium anisopliae @ 5 g/L.\n• In severe damage, apply Chlorantraniliprole 18.5% SC @ 0.4 ml/L or Emamectin Benzoate 5% SG @ 0.4 g/L directed into whorls.",
                    "te": "• సుడులలో ఇసుక + సున్నం మిశ్రమాన్ని వేయండి.\n• నివారణకు బి.టి 2 గ్రా/లీ లేదా మెటారైజియం 5 గ్రా/లీ పిచికారీ చేయండి.\n• ఉధృతి ఎక్కువగా ఉంటే క్లోరాంట్రానిలిప్రోల్ 0.4 మి.లీ/లీ సుడులు తడిసేలా పిచికారీ చేయండి.",
                    "hi": "• गोभ में रेत और राख का मिश्रण डालें।\n• रोकथाम के लिए बीटी (2 ग्राम/लीटर) का छिड़काव करें।\n• अधिक प्रकोप होने पर क्लोरेंट्रानिलिप्रोल (0.4 मिली/लीटर) सीधे गोभ के अंदर छिड़कें।"
                },
                "precautions": {
                    "en": "Spray nozzle must be aimed directly into the plant whorl, not broadcast over the canopy.",
                    "te": "మందు ద్రావణం నేరుగా సుడిలో పడేలా పిచికారీ చేయాలి.",
                    "hi": "छिड़काव का नोजल सीधे पौधे के गोभ की तरफ रखकर दवा डालें।"
                },
                "source": "ICAR-IIMR (Indian Institute of Maize Research) Advisory"
            }
        }
    },

    "Turmeric": {
        "name": {"en": "Turmeric", "te": "పసుపు", "hi": "हल्दी"},
        "suitable_seasons": {"en": "Kharif (May–June planting)", "te": "ఖరీఫ్ (మే–జూన్ నాటు సమయం)", "hi": "खरीफ (मई-जून)"},
        "suitable_soils": {"en": "Deep, fertile, well-drained sandy loam or clay loam rich in humus (pH 6.0–7.5)", "te": "మురుగునీరు నిలవని సారవంతమైన ఇసుక గరప లేదా ఎర్ర నేలలు", "hi": "अच्छी जल निकासी वाली जीवांश युक्त दोमट मिट्टी"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Turmeric", "te": "పసుపు సమగ్ర ఎరువుల యాజమాన్యం", "hi": "हल्दी के लिए संतुलित उर्वरक प्रबंधन"},
            "happening": {
                "en": "Turmeric requires heavy organic manure, basal phosphorus, and split potassium applications to promote vigorous rhizome development and high curcumin content.",
                "te": "పసుపులో దుంప ఊరడానికి మరియు పసుపు రంగు (కుర్కుమిన్) బాగా రావడానికి సేంద్రీయ ఎరువులు, పొటాష్ ఎంతో ముఖ్యం.",
                "hi": "हल्दी में कंदों की अच्छी वृद्धि और करक्यूमिन की मात्रा बढ़ाने के लिए जीवांश खाद और पोटाश का समय पर प्रयोग जरूरी है।"
            },
            "check": {
                "en": "Check vegetative growth at 45 and 90 DAP; inspect rhizome enlargement at 120 DAP.",
                "te": "45 మరియు 90 రోజుల వద్ద పెరుగుదలను, 120 రోజుల వద్ద దుంప ఎదుగుదలను గమనించండి.",
                "hi": "45, 90 और 120 दिन पर फसल की बढ़वार और कंद विकास जांचें।"
            },
            "actions": {
                "en": "• Basal: FYM @ 10 tonnes/acre + Neem cake @ 200 kg/acre + 50 kg SSP + 25 kg MOP.\n• 45 DAP: Top dress Urea @ 25 kg/acre + MOP @ 20 kg/acre with earthing up.\n• 90 DAP: Top dress Urea @ 25 kg/acre + MOP @ 20 kg/acre with 2nd earthing up.\n• Foliar spray: Spray 19:19:19 @ 5 g/L at 60 DAP and Potassium Schoenite @ 5 g/L at 120 DAP.",
                "te": "• ఆఖరి దుక్కిలో: ఎకరానికి 10 టన్నుల పశువుల ఎరువు + 200 కిలోల వేపపిండి + 50 కిలోల సూపర్ ఫాస్ఫేట్ + 25 కిలోల పొటాష్.\n• 45 రోజుల వద్ద: ఎకరానికి 25 కిలోల యూరియా + 20 కిలోల పొటాష్ వేసి మట్టి ఎగదోయండి.\n• 90 రోజుల వద్ద: 25 కిలోల యూరియా + 20 కిలోల పొటాష్ వేసి రెండోసారి మట్టి ఎగదోయండి.\n• దుంప ఊరే దశలో పొటాషియం షోనైట్ 5 గ్రా/లీ పిచికారీ చేయండి.",
                "hi": "• बुवाई पर: 10 टन गोबर खाद + 200 किग्रा नीम खली + 50 किग्रा एसएसपी + 25 किग्रा पोटाश दें।\n• 45 दिन पर: 25 किग्रा यूरिया + 20 किग्रा पोटाश देकर मिट्टी चढ़ाएं।\n• 90 दिन पर: 25 किग्रा यूरिया + 20 किग्रा पोटाश देकर दोबारा मिट्टी चढ़ाएं।"
            },
            "precautions": {
                "en": "Earthing up must accompany fertilizer application to provide loose soil around developing rhizomes and prevent exposure to sunlight.",
                "te": "ఎరువులు వేసిన వెంటనే తప్పనిసరిగా మట్టి ఎగదోయాలి, దుంపలు ఎండకు తగలకూడదు.",
                "hi": "खाद डालने के बाद मिट्टी जरूर चढ़ाएं ताकि कंद धूप में न खुलें।"
            },
            "source": "ICAR-IISR Calicut & ANGRAU Turmeric Guidelines"
        },

        "symptoms": {
            "blight_spots": {
                "title": {"en": "Rhizome Rot & Leaf Spot", "te": "దుంపకుళ్లు & ఆకుమచ్చ తెగులు", "hi": "प्रकंद सड़न (कंद सड़न) एवं पत्ती धब्बा रोग"},
                "happening": {
                    "en": "Pythium causes collar rotting and soft decay of rhizomes with foul smell. Colletotrichum causes brown elliptical spots on leaves.",
                    "te": "తేమ ఎక్కువైతే దుంపలు మెత్తబడి కుళ్లిపోతాయి (దుంపకుళ్లు). ఆకులపై గోధుమ రంగు మచ్చలు ఏర్పడతాయి.",
                    "hi": "अधिक नमी से कंद सड़ने लगते हैं और पत्तियों पर भूरे धब्बे बनते हैं।"
                },
                "check": {
                    "en": "Check for yellowing lower leaves that pull out easily from the collar with rotten foul-smelling rhizomes.",
                    "te": "మొక్క మొదలు మెత్తబడి తేలికగా ఊడివస్తుందా, దుంపలు కుళ్ళి వాసన వస్తున్నాయా చూడండి.",
                    "hi": "पौधे के नीचे का भाग सड़कर आसानी से उखड़ जाता है और कंद से बदबू आती है।"
                },
                "actions": {
                    "en": "• Ensure broad beds and furrows (BBF) to prevent standing water.\n• Drench root zone with Trichoderma viride enriched FYM.\n• In disease patches, drench with Copper Oxychloride 50% WP @ 3 g/L or Metalaxyl + Mancozeb @ 2 g/L.",
                    "te": "• పొలంలో నీరు నిలవకుండా ఎత్తైన బోదెలు ఏర్పాటు చేయండి.\n• మొదళ్ళ వద్ద ట్రైకోడెర్మా కలిపిన పశువుల ఎరువును వేయండి.\n• నివారణకు కాపర్ ఆక్సీక్లోరైడ్ 3 గ్రా/లీ ద్రావణాన్ని మొదళ్ల వద్ద తడపండి.",
                    "hi": "• खेत में मेड़ बनाकर बुवाई करें ताकि पानी न रुके।\n• ट्राइकोडर्मा युक्त गोबर की खाद डालें।\n• कंद के पास कॉपर ऑक्सीक्लोराइड (3 ग्राम/लीटर) का घोल डालकर जड़ क्षेत्र को भिगोएं।"
                },
                "precautions": {
                    "en": "Never take rhizome seed from an infected field. Treat seed rhizomes before planting.",
                    "te": "తెగులు సోకిన పంట నుండి విత్తన దుంపలను వాడవద్దు. విత్తన శుద్ధి తప్పనిసరి.",
                    "hi": "रोगग्रस्त खेत के कंदों को बीज के रूप में न लगाएं।"
                },
                "source": "ICAR-IISR (Indian Institute of Spices Research) Protocol"
            }
        }
    },

    "Potato": {
        "name": {"en": "Potato", "te": "బంగాళాదుంప", "hi": "आलू"},
        "suitable_seasons": {"en": "Rabi (October–November planting)", "te": "రబీ (అక్టోబర్–నవంబర్)", "hi": "रबी (अक्टूबर-नवंबर)"},
        "suitable_soils": {"en": "Well-drained loose, friable sandy loam rich in humus (pH 5.5–6.5)", "te": "తేలికపాటి ఇసుక గరప నేలలు", "hi": "हल्की भुरभुरी बलुई दोमट मिट्टी"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Potato", "te": "బంగాళాదుంప సమగ్ర ఎరువుల యాజమాన్యం", "hi": "आलू के लिए संतुलित उर्वरक प्रबंधन"},
            "happening": {
                "en": "Potato is a quick-growing shallow-rooted crop requiring abundant organic matter, full basal phosphorus, and split nitrogen and potassium.",
                "te": "బంగాళాదుంపలో దుంప సైజు పెరగడానికి పశువుల ఎరువు, సమతుల్య నత్రజని మరియు పొటాష్ అవసరం.",
                "hi": "आलू में कंदों का आकार बढ़ाने और अच्छी पैदावार के लिए संतुलित एनपीके और मिट्टी चढ़ाना अत्यंत आवश्यक है।"
            },
            "check": {
                "en": "Check earthing-up stage at 30-35 DAS and tuber bulking at 50-60 DAS.",
                "te": "30-35 రోజుల వద్ద మట్టి ఎగదోసే దశ మరియు దుంప ఊరే దశను గమనించండి.",
                "hi": "30-35 दिन पर मिट्टी चढ़ाने की अवस्था और 50-60 दिन पर कंद बनने की अवस्था देखें।"
            },
            "actions": {
                "en": "• Basal: FYM @ 10 tonnes/acre + 50 kg DAP + 35 kg MOP + 25 kg Urea.\n• Earthing up (30-35 DAS): Top dress Urea @ 30 kg/acre followed by earthing up.\n• Tuber Bulking (50-55 DAS): Spray 0:52:34 @ 5 g/L + Boron @ 1 g/L to prevent hollow heart.",
                "te": "• నాటే సమయంలో: ఎకరానికి 10 టన్నుల పశువుల ఎరువు + 50 కిలోల డీఏపీ + 35 కిలోల పొటాష్ + 25 కిలోల యూరియా.\n• 30-35 రోజుల వద్ద: ఎకరానికి 30 కిలోల యూరియా వేసి మట్టి ఎగదోయండి.\n• దుంప ఊరే దశలో: 0:52:34 ఎరువు 5 గ్రా/లీ + బోరాన్ 1 గ్రా/లీ పిచికారీ చేయండి.",
                "hi": "• बुवाई पर: 10 टन गोबर खाद + 50 किग्रा डीएपी + 35 किग्रा पोटाश + 25 किग्रा यूरिया दें।\n• 30-35 दिन पर: 30 किग्रा यूरिया देकर मिट्टी चढ़ाएं।\n• कंद फूलते समय 0:52:34 (5 ग्राम/लीटर) + बोरॉन (1 ग्राम/लीटर) का छिड़काव करें।"
            },
            "precautions": {
                "en": "Keep developing tubers covered with soil. Exposed tubers turn green with bitter solanine and become unmarketable.",
                "te": "దుంపలు బయటకు కనిపించకుండా మట్టితో కప్పాలి, లేకుంటే పచ్చబడి పనికిరావు.",
                "hi": "कंदों को मिट्टी से ढका रखें, धूप लगने पर आलू हरे पड़ जाते हैं जो खाने योग्य नहीं रहते।"
            },
            "source": "ICAR-CPRI Shimla Potato Production Technology"
        },

        "symptoms": {
            "blight_spots": {
                "title": {"en": "Late Blight of Potato (Phytophthora infestans)", "te": "ఆలస్యపు మాడ తెగులు", "hi": "आलू का पछेती झुलसा रोग"},
                "happening": {
                    "en": "Destructive fungal-like pathogen causes rapid water-soaked blackening of foliage and white cottony growth on leaf reverse in cool cloudy weather.",
                    "te": "చల్లని తేమ వాతావరణంలో ఆకులపై నల్లటి నీటి మచ్చలు ఏర్పడి మొక్క మొత్తం మాడిపోయినట్లు అవుతుంది.",
                    "hi": "ठंडे और नम मौसम में पत्तियों पर पानी से भीगे काले धब्बे बनते हैं और पौधे तेजी से झुलस जाते हैं।"
                },
                "check": {
                    "en": "Check undersides of affected leaves during morning hours for white fuzzy mildew growth at the edge of dark lesions.",
                    "te": "ఉదయం వేళల్లో ఆకుల అడుగున తెల్లటి బూజు లాంటి పొర కనిపిస్తుంది.",
                    "hi": "सुबह के समय धब्बों के किनारों पर पत्तियों के नीचे सफेद फफूंद देखें।"
                },
                "actions": {
                    "en": "• Spray preventive Mancozeb 75% WP @ 2.5 g/L before foggy weather.\n• On first symptom appearance, apply Cymoxanil + Mancozeb @ 2 g/L or Dimethomorph @ 1 g/L.",
                    "te": "• నివారణకు ముందస్తుగా మ్యాంకోజెబ్ 2.5 గ్రా/లీ పిచికారీ చేయండి.\n• తెగులు కనిపిస్తే సైమోక్సానిల్ + మ్యాంకోజెబ్ 2 గ్రా/లీ పిచికారీ చేయండి.",
                    "hi": "• लक्षण दिखने से पहले मैंकोजेब (2.5 ग्राम/लीटर) का छिड़काव करें।\n• बीमारी दिखने पर साइमोक्सानिल + मैंकोजेब (2 ग्राम/लीटर) का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Ensure complete coverage of upper and lower leaf surfaces. Repeat every 7–10 days under continuous fog.",
                    "te": "మొక్క మొత్తం తడిసేలా పిచికారీ చేయండి. పొగమంచు ఎక్కువగా ఉంటే వారం వ్యవధిలో మళ్ళీ చేయాలి.",
                    "hi": "पत्तियों की दोनों सतहों पर दवा अच्छी तरह पहुंचे। लगातार कोहरे में 7-10 दिन बाद दोहराएं।"
                },
                "source": "ICAR-CPRI (Central Potato Research Institute) Advisory"
            }
        }
    },

    "Groundnut": {
        "name": {"en": "Groundnut", "te": "వేరుశనగ", "hi": "मूंगफली"},
        "suitable_seasons": {"en": "Kharif (June–July), Rabi/Summer (Nov–Jan)", "te": "ఖరీఫ్ (జూన్–జూలై), రబీ/వేసవి (నవంబర్–జనవరి)", "hi": "खरीफ (जून-जुलाई), रबी (नवंबर-दिसंबर)"},
        "suitable_soils": {"en": "Well-drained red sandy loam or light alluvial soils (pH 6.5–7.5)", "te": "మురుగునీరు నిలవని తేలికపాటి ఎర్ర నేలలు లేదా ఇసుక గరప నేలలు", "hi": "अच्छी जल निकासी वाली हल्की बलुई दोमट मिट्टी"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Groundnut", "te": "వేరుశనగ సమగ్ర ఎరువుల యాజమాన్యం", "hi": "मूंगफली के लिए संतुलित खाद एवं उर्वरक प्रबंधन"},
            "happening": {
                "en": "Groundnut is a legume that fixes nitrogen, but requires high phosphorus for root nodulation and calcium/sulphur (Gypsum) for pod development and kernel filling.",
                "te": "వేరుశనగలో కాయలు బాగా ఊరడానికి, పొల్లు కాయలు లేకుండా గింజ బరువు పెరగడానికి కాల్షియం, గంధకం (జిప్సం) ఎంతో కీలకం.",
                "hi": "मूंगफली में दाना भरने और तेल की मात्रा बढ़ाने के लिए फॉस्फोरस और कैल्शियम/सल्फर (जिप्सम) की सबसे अधिक आवश्यकता होती है।"
            },
            "check": {
                "en": "Check pegging stage (40-45 DAS). Observe if leaves show yellowing between veins (iron chlorosis) or hollow pods ('pops').",
                "te": "ఊడలు దిగే దశ (40-45 రోజులు) గమనించండి. కాయల్లో గింజ సరిగ్గా ఊరుతుందో లేదో చూడండి.",
                "hi": "सूंइयां (पेगिंग) बनते समय (40-45 दिन) मिट्टी की जांच करें।"
            },
            "actions": {
                "en": "• Basal: FYM @ 4 tonnes/acre + Single Super Phosphate (SSP) @ 100 kg/acre + MOP @ 25 kg/acre + Urea @ 10 kg/acre.\n• Pegging Stage (40-45 DAS): Apply Gypsum @ 200 kg/acre near root zone and incorporate lightly into soil.\n• Micronutrients: Foliar spray of Ferrous Sulphate @ 5 g/L + Citric acid @ 1 g/L if iron yellowing occurs.",
                "te": "• ఆఖరి దుక్కిలో: ఎకరానికి 4 టన్నుల పశువుల ఎరువు + 100 కిలోల సింగిల్ సూపర్ ఫాస్ఫేట్ + 25 కిలోల పొటాష్ + 10 కిలోల యూరియా.\n• ఊడలు దిగే దశలో (40-45 రోజులకు): ఎకరానికి 200 కిలోల జిప్సం వేసి మట్టి ఎగదోయండి.\n• ఆకులు పసుపుబారితే అన్నభేది 5 గ్రా/లీ + నిమ్మ ఉప్పు 1 గ్రా/లీ పిచికారీ చేయండి.",
                "hi": "• बुवाई के समय: 4 टन गोबर खाद + 100 किग्रा सिंगल सुपर फॉस्फेट + 25 किग्रा पोटाश डालें।\n• पेगिंग अवस्था (40-45 दिन पर): 200 किग्रा जिप्सम प्रति एकड़ पौधों की जड़ों के पास डालकर मिट्टी चढ़ाएं।\n• पीलापन आने पर फेरस सल्फेट 5 ग्राम + साइट्रिक एसिड 1 ग्राम प्रति लीटर छिड़कें।"
            },
            "precautions": {
                "en": "Do not disturb soil after peg penetration. Adequate moisture during pegging and pod filling is critical for calcium absorption.",
                "te": "ఊడలు నేలలోకి దిగిన తర్వాత అంతరకృషి చేయవద్దు. జిప్సం వేసినప్పుడు నేలలో తేమ ఉండాలి.",
                "hi": "सूंइयां मिट्टी में घुसने के बाद निराई-गुड़ाई न करें। जिप्सम डालते समय नमी का होना जरूरी है।"
            },
            "source": "ICAR-DGR Junagadh & ANGRAU Groundnut Production Guide"
        },

        "symptoms": {
            "blight_spots": {
                "title": {"en": "Tikka Leaf Spot (Cercospora)", "te": "టిక్కా ఆకుమచ్చ తెగులు", "hi": "टिक्का पत्ती धब्बा रोग"},
                "happening": {
                    "en": "Fungal pathogen causes circular reddish-brown to dark spots with prominent yellow halos, causing premature leaf shedding.",
                    "te": "ఆకులపై గుండ్రటి ఎరుపు-గోధుమ రంగు మచ్చలు పసుపు వలయంతో ఏర్పడి ఆకులు రాలిపోతాయి.",
                    "hi": "पत्तियों पर गोल गहरे भूरे धब्बे पीले छल्ले के साथ बनते हैं और पत्तियां गिरने लगती हैं।"
                },
                "check": {
                    "en": "Inspect leaves for dark circular spots with bright yellow halos.",
                    "te": "ఆకులపై పసుపు వలయంతో కూడిన నల్లటి మచ్చలను చూడండి.",
                    "hi": "पत्तियों पर पीले छल्ले वाले काले-भूरे धब्बे जांचें।"
                },
                "actions": {
                    "en": "• Spray Mancozeb 75% WP @ 2.5 g/L or Carbendazim + Mancozeb @ 2 g/L.\n• Apply gypsum @ 200 kg/acre at 40–45 days after sowing during earthing-up for pod development.",
                    "te": "• నివారణకు మ్యాంకోజెబ్ 2.5 గ్రా/లీ లేదా కార్బెండజిమ్ + మ్యాంకోజెబ్ 2 గ్రా/లీ పిచికారీ చేయండి.\n• విత్తిన 40–45 రోజులకు ఎకరానికి 200 కిలోల జిప్సం వేయండి.",
                    "hi": "• रोकथाम हेतु मैंकोजेब 2.5 ग्राम/लीटर का छिड़काव करें।\n• बुवाई के 40-45 दिन बाद 200 किग्रा/एकड़ जिप्सम डालें।"
                },
                "precautions": {
                    "en": "Do not skip gypsum at pegging stage, as calcium is directly absorbed by developing pods.",
                    "te": "ఊడలు దిగే దశలో జిప్సం వేయడం మర్చిపోవద్దు, ఇది కాయ గట్టిపడటానికి ఎంతో ముఖ్యం.",
                    "hi": "सुइयां बनते समय जिप्सम जरूर डालें, इससे दानों का भराव अच्छा होता है।"
                },
                "source": "ICAR-DGR (Directorate of Groundnut Research) Advisory"
            }
        }
    },

    "Wheat": {
        "name": {"en": "Wheat", "te": "గోధుమలు", "hi": "गेहूं"},
        "suitable_seasons": {"en": "Rabi (November sowing)", "te": "రబీ (నవంబర్)", "hi": "रबी (नवंबर बुवाई)"},
        "suitable_soils": {"en": "Well-drained fertile clay loam or loam soils (pH 6.5–7.5)", "te": "సారవంతమైన గరప లేదా నల్ల నేలలు", "hi": "अच्छी जल निकासी वाली उपजाऊ दोमट मिट्टी"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Wheat", "te": "గోధుమ సమగ్ర ఎరువుల యాజమాన్యం", "hi": "गेहूं के लिए संतुलित उर्वरक प्रबंधन"},
            "happening": {
                "en": "Wheat requires balanced NPK (120:60:40 kg/ha). Adequate basal phosphorus promotes crown root establishment, while split nitrogen boosts tillering.",
                "te": "గోధుమలో వేరు వ్యవస్థ పటిష్టంగా ఉండటానికి, ఎక్కువ పిలకలు మరియు గింజ బరువు పెరగడానికి సమతుల్య ఎరువులు అవసరం.",
                "hi": "गेहूं में कल्ले फूटने और दाना मोटा होने के लिए समय पर संतुलित एनपीके (120:60:40) खाद देना अनिवार्य है।"
            },
            "check": {
                "en": "Inspect Crown Root Initiation (CRI at 21 DAS) and Tillering/Jointing stages (40-45 DAS).",
                "te": "మొదటి తడి ఇచ్చే సమయం (21 రోజులు) మరియు పిలక దశను గమనించండి.",
                "hi": "ताज जड़ (CRI) अवस्था (20-25 दिन) और कल्ले फूटने की अवस्था जांचें।"
            },
            "actions": {
                "en": "• Basal (at sowing): DAP @ 50 kg/acre + MOP @ 20 kg/acre + Urea @ 15 kg/acre.\n• 1st Irrigation (CRI stage, 21 DAS): Top dress Urea @ 30 kg/acre with moisture.\n• 2nd Irrigation (Jointing, 40-45 DAS): Top dress Urea @ 25 kg/acre.\n• Booting stage: Spray 0:52:34 @ 5 g/L to protect against terminal heat.",
                "te": "• విత్తే సమయంలో: ఎకరానికి 50 కిలోల డీఏపీ + 20 కిలోల పొటాష్ + 15 కిలోల యూరియా.\n• మొదటి తడి వద్ద (21 రోజులు): ఎకరానికి 30 కిలోల యూరియా వేయండి.\n• రెండో తడి వద్ద (40-45 రోజులు): ఎకరానికి 25 కిలోల యూరియా వేయండి.\n• ఈనె దశలో 0:52:34 ఎరువు 5 గ్రా/లీ పిచికారీ చేయండి.",
                "hi": "• बुवाई के समय: 50 किग्रा डीएपी + 20 किग्रा पोटाश + 15 किग्रा यूरिया प्रति एकड़ दें।\n• पहली सिंचाई पर (CRI अवस्था, 21 दिन): 30 किग्रा यूरिया प्रति एकड़ दें।\n• दूसरी सिंचाई पर (40-45 दिन): 25 किग्रा यूरिया दें।\n• बालियां निकलते समय 0:52:34 (5 ग्राम/लीटर) का छिड़काव करें।"
            },
            "precautions": {
                "en": "Never delay the first irrigation and top-dressing beyond 25 days as Crown Root Initiation directly determines final grain yield.",
                "te": "మొదటి తడి మరియు యూరియా వేయడం 25 రోజులు దాటకుండా చూసుకోండి.",
                "hi": "पहली सिंचाई और यूरिया देने में 21-25 दिन से अधिक की देरी न करें।"
            },
            "source": "ICAR-IIWBR Karnal Wheat Production Technology"
        },

        "symptoms": {
            "blight_spots": {
                "title": {"en": "Yellow Rust & Brown Rust", "te": "కుంకుమ తెగులు (పసుపు రంగు రస్ట్)", "hi": "पीला रतुआ एवं भूरा रतुआ रोग"},
                "happening": {
                    "en": "Fungal spores form linear yellow or orange-brown powdery stripes on leaves, wiping off as dust on fingers.",
                    "te": "ఆకులపై పసుపు లేదా నారింజ రంగు పొడి లాంటి చారలు ఏర్పడతాయి. వేలితో తాకితే పసుపు రంగు అంటుకుంటుంది.",
                    "hi": "पत्तियों पर पीली या भूरी धारियों में पाउडर जैसी फफूंद बनती है जो हाथ लगाने पर उंगलियों पर चिपक जाती है।"
                },
                "check": {
                    "en": "Rub affected leaf between fingers; if yellow powder rubs off, it is yellow rust.",
                    "te": "ఆకును వేలితో రుద్ది చూడండి, పసుపు పొడి అంటుకుంటే అది కుంకుమ తెగులే.",
                    "hi": "पत्ती को छूकर देखें, यदि पीला पाउडर हाथ पर लगे तो यह पीला रतुआ है।"
                },
                "actions": {
                    "en": "• Spray Propiconazole 25% EC @ 1 ml/L or Tebuconazole 25.9% EC @ 1 ml/L upon first detection.",
                    "te": "• నివారణకు ప్రొపికొనజోల్ 25% EC 1 మి.లీ/లీటరు నీటికి కలిపి పిచికారీ చేయండి.",
                    "hi": "• रोकथाम हेतु प्रोपिकोनाजोल 25% EC (1 मिली/लीटर पानी) का तुरंत छिड़काव करें।"
                },
                "precautions": {
                    "en": "Act promptly upon initial localized foci ('yellow patches') to prevent whole-field spread.",
                    "te": "పొలంలో ఎక్కడైనా చిన్న పసుపు మచ్చ కనిపించిన వెంటనే పిచికారీ చేయండి.",
                    "hi": "शुरुआती पैच दिखते ही छिड़काव करें ताकि पूरे खेत में न फैले।"
                },
                "source": "ICAR-IIWBR (Indian Institute of Wheat and Barley Research) Protocol"
            }
        }
    },

    "Gram": {
        "name": {"en": "Gram / Pulses", "te": "శనగలు / పప్పుధాన్యాలు", "hi": "चना / दालें"},
        "suitable_seasons": {"en": "Rabi (October–November sowing)", "te": "రబీ (అక్టోబర్–నవంబర్)", "hi": "रबी (अक्टूबर-नवंबर)"},
        "suitable_soils": {"en": "Well-drained deep black or alluvial loams (pH 6.5–8.0)", "te": "తేమను నిలిపే లోతైన నల్లరేగడి నేలలు", "hi": "गहरी काली या दोमट मिट्टी जिसमें जलभराव न हो"},
        "fertilizer_guide": {
            "title": {"en": "Nutrient & Fertilizer Schedule for Bengal Gram (Chana)", "te": "శనగ సమగ్ర ఎరువుల యాజమాన్యం", "hi": "चना (बंगाल ग्राम) के लिए संतुलित उर्वरक प्रबंधन"},
            "happening": {
                "en": "Bengal Gram fixes its own nitrogen through Rhizobium root nodules. It requires starter nitrogen and basal phosphorus plus sulphur for maximum pod setting.",
                "te": "శనగ పంట వేరుబుడిపెల ద్వారా గాలిలోని నత్రజనిని గ్రహిస్తుంది. పూత, కాయ బాగా రావడానికి ప్రారంభ నత్రజని మరియు భాస్వరం, గంధకం ముఖ్యం.",
                "hi": "चना दलहनी फसल होने के कारण स्वयं नाइट्रोजन बनाती है। इसमें शुरुआती नाइट्रोजन, फॉस्फोरस और गंधक (सल्फर) की मुख्य जरूरत होती है।"
            },
            "check": {
                "en": "Check root nodulation at 25-30 DAS. Inspect for flower initiation at 45 DAS.",
                "te": "25-30 రోజుల వద్ద వేర్లపై బుడిపెలను, 45 రోజుల వద్ద పూత దశను గమనించండి.",
                "hi": "25-30 दिन पर जड़ों में गुलाबी ग्रंथियां और 45 दिन पर फूल आने की अवस्था जांचें।"
            },
            "actions": {
                "en": "• Basal (at sowing): DAP @ 40 kg/acre + 10 kg Sulphur (or SSP @ 100 kg/acre + Urea @ 10 kg/acre).\n• Seed treatment with Rhizobium + PSB @ 250 g per 10 kg seed.\n• Flower initiation (45 DAS): Foliar spray of 2% DAP or 19:19:19 @ 4-5 g/L to boost flowering and reduce flower drop.\n• Pod development: Spray 0:52:34 @ 5 g/L.",
                "te": "• విత్తే సమయంలో: ఎకరానికి 40 కిలోల డీఏపీ + 10 కిలోల సల్ఫర్.\n• విత్తనాలకు రైజోబియం మరియు పి.ఎస్.బి కల్చర్ పట్టించి విత్తండి.\n• పూత దశలో: 2% డీఏపీ ద్రావణం లేదా 19:19:19 ఎరువు 5 గ్రా/లీ పిచికారీ చేయండి.\n• కాయ దశలో 0:52:34 ఎరువు 5 గ్రా/లీ పిచికారీ చేయండి.",
                "hi": "• बुवाई पर: 40 किग्रा डीएपी + 10 किग्रा सल्फर प्रति एकड़ डालें।\n• राइजोबियम एवं पीएसबी कल्चर से बीजोपचार अवश्य करें।\n• फूल आते समय: 2% डीएपी घोल या 19:19:19 (5 ग्राम/लीटर) का छिड़काव करें।\n• फली बनते समय 0:52:34 (5 ग्राम/लीटर) का छिड़काव करें।"
            },
            "precautions": {
                "en": "Avoid heavy application of urea/nitrogen as excessive nitrogen causes luxurious vegetative growth at the expense of flowering.",
                "te": "యూరియా ఎక్కువ వేయవద్దు, దీనివల్ల పైరు ఏపుగా పెరిగి పూత తగ్గిపోతుంది.",
                "hi": "अधिक यूरिया न दें, इससे वानस्पतिक बढ़वार अधिक होती है और फूल कम आते हैं।"
            },
            "source": "ICAR-IIPR Kanpur Pulses Production Technology"
        },

        "symptoms": {
            "borer": {
                "title": {"en": "Gram Pod Borer (Helicoverpa armigera)", "te": "శనగ కాయతొలుచు పురుగు", "hi": "चने की फली छेदक इल्ली"},
                "happening": {
                    "en": "Greenish larvae feed on young foliage and bore circular holes into developing pods, eating the green seeds.",
                    "te": "ఆకుపచ్చ పురుగులు లేత ఆకులను తింటూ, కాయలకు రంధ్రాలు చేసి లోపలి గింజలను తింటాయి.",
                    "hi": "हरी इल्लियां पत्तियों को खाती हैं और फलियों में गोल छेद करके अंदर के दानों को चट कर जाती हैं।"
                },
                "check": {
                    "en": "Shake plants over a white sheet; count dislodged caterpillars. If >= 1 larva per meter row, threshold is crossed.",
                    "te": "మొక్కలను కదిపి చూడండి. మీటరు వరుసలో 1 పురుగు కనిపించినా నివారణ చర్యలు చేపట్టాలి.",
                    "hi": "प्रति मीटर कतार में 1 या अधिक इल्ली दिखने पर तुरंत नियंत्रण करें।"
                },
                "actions": {
                    "en": "• Install 5 pheromone traps per acre.\n• Erect 15 bird perches per acre for natural predation.\n• Spray Neem oil @ 2 ml/L or Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Emamectin Benzoate 5% SG @ 0.4 g/L.",
                    "te": "• ఎకరానికి 5 లింగాకర్షక బుట్టలు, 15 పక్షి స్థావరాలు ఏర్పాటు చేయండి.\n• నివారణకు వేపనూనె 2 మి.లీ/లీ లేదా ఇమామెక్టిన్ బెంజోయేట్ 0.4 గ్రా/లీ పిచికారీ చేయండి.",
                    "hi": "• प्रति एकड़ 5 फेरोमोन ट्रैप और 15 टी-आकार की पक्षी खूंटियां लगाएं।\n• रोकथाम के लिए नीम तेल 2 मिली/लीटर या इमामेक्टिन बेंजोएट 0.4 ग्राम/लीटर का छिड़काव करें।"
                },
                "precautions": {
                    "en": "Spray in late afternoon when larvae are actively feeding.",
                    "te": "సాయంత్రం వేళల్లో పిచికారీ చేయడం వలన మంచి ఫలితం ఉంటుంది.",
                    "hi": "शाम के समय छिड़काव करें जब इल्लियां अधिक सक्रिय होती हैं।"
                },
                "source": "ICAR-IIPR (Indian Institute of Pulses Research) Protocol"
            }
        }
    }
}


# ------------------------------------------------------------------------------
# Symptom & Intent Detection Functions
# ------------------------------------------------------------------------------

def detect_agri_intent_and_symptoms(query: str) -> Dict[str, Any]:
    """Analyzes a natural language question to extract crop, symptom type, and ambiguity."""
    q = query.lower()

    # Symptom tags
    is_yellowing = any(k in q for k in ["yellow", "yellowing", "పసుపు", "पीली", "पीला", "chlorosis"])
    is_lower_yellow = is_yellowing and any(k in q for k in ["bottom", "lower", "old", "older", "కింది", "పాత", "नीचे", "पुरानी"])
    is_upper_yellow = is_yellowing and any(k in q for k in ["top", "upper", "young", "new", "లేత", "పై", "ऊपर", "नई"])

    is_leaf_curl = any(k in q for k in ["curl", "curling", "ముడత", "ముడుచుకు", "మరోడ్", "मुड़", "thrip", "thrips", "mite", "mites", "whitefly", "తామర", "నల్లి", "తెల్లదోమ", "सफेद मक्खी"])
    is_borer = any(k in q for k in ["borer", "caterpillar", "worm", "larva", "కాయతొలుచు", "తొలుచు", "పురుగు", "ఇల్లి", "छेड़क", "छेदक", "इल्ली", "सुंडी", "सेना"])
    is_blight = any(k in q for k in ["blight", "spot", "spots", "leaf spot", "anthracnose", "dieback", "మచ్చ", "మచ్చలు", "తెగులు", "మాడ", "धब्बा", "धब्बे", "झुलसा", "डाइबैक"])
    is_wilt = any(k in q for k in ["wilt", "wilting", "rot", "root rot", "ఎండిపో", "కుళ్లు", "మురిగి", "उकठा", "सड़न", "मुरझा"])
    is_fertilizer = any(k in q for k in ["fertilizer", "nutrient", "npk", "urea", "dap", "potash", "boron", "zinc", "ఎరువు", "పోషక", "యూరియా", "ఖరీదు", "खाद", "उर्वरक", "यूरिया"])
    is_irrigation = any(k in q for k in ["water", "watering", "irrigation", "నీరు", "తడులు", "సిసాయి", "सिंचाई", "पानी"])
    is_crop_planning = any(k in q for k in [
        "which crop", "what crop", "crop to grow", "suggest crop", "crop recommendation",
        "best crop", "what should i grow", "crops to grow", "what to sow", "sowing",
        "ఏ పంట వేయాలి", "ఏ పంట సాగు", "పంట ఎంపిక", "कौन सी फसल", "फसल लगाएं", "फसल बोएं", "फसल चयन"
    ])

    return {
        "is_yellowing": is_yellowing,
        "is_lower_yellow": is_lower_yellow,
        "is_upper_yellow": is_upper_yellow,
        "is_leaf_curl": is_leaf_curl,
        "is_borer": is_borer,
        "is_blight": is_blight,
        "is_wilt": is_wilt,
        "is_fertilizer": is_fertilizer,
        "is_irrigation": is_irrigation,
        "is_crop_planning": is_crop_planning
    }


def is_ambiguous_symptom_query(query: str, crop: Optional[str] = None) -> Tuple[bool, str]:
    """
    Determines if user query is vague and needs clarification:
    - Asks 'Why are leaves turning yellow?' without indicating upper or lower leaves.
    - Asks 'Which crop should I grow?' without season, soil, or location.
    - Asks general pest query without symptoms or crop.
    """
    q_norm = query.lower()
    intent = detect_agri_intent_and_symptoms(q_norm)

    # 1. Crop Planning Ambiguity
    if intent["is_crop_planning"]:
        has_season = any(s in q_norm for s in ["kharif", "rabi", "summer", "monsoon", "winter", "ఖరీఫ్", "రబీ", "వేసవి", "खरीफ", "रबी", "जायद"])
        has_soil = any(s in q_norm for s in ["black", "red", "sandy", "clay", "loam", "నల్లరేగడి", "ఎర్ర", "ఇసుక", "काली", "लाल", "दोमट"])
        if not (has_season and has_soil):
            return True, "crop_planning"

    # 2. General Leaf Yellowing Ambiguity (did not specify upper vs lower)
    if intent["is_yellowing"] and not (intent["is_lower_yellow"] or intent["is_upper_yellow"] or intent["is_leaf_curl"] or intent["is_blight"]):
        return True, "yellowing_general"

    # 3. Missing crop on generic pest inquiry
    if not crop and any(w in q_norm for w in ["pest", "disease", "medicine", "spray", "పురుగు", "మందు", "తెగులు", "कीट", "दवा", "रोग"]):
        return True, "missing_crop"

    return False, "none"


def get_clarification_response(crop: Optional[str], ambiguity_type: str, lang: str) -> Dict[str, Any]:
    """Generates polite, task-specific follow-up questions to gather essential diagnostic details."""
    c_name = crop or "crop"

    if ambiguity_type == "yellowing_general":
        if lang == "te":
            reply = f"మీ {c_name if crop else 'పంట'}లో సరైన కారణాన్ని నిర్ధారించడానికి, దయచేసి ఈ వివరాలు గమనించండి:\n\n1. **కింది ముదిరిన ఆకులు** పసుపుబారుతున్నాయా (సాధారణంగా నత్రజని లోపం లేదా నీరు నిలవడం)?\n2. లేదా **పై లేత ఆకులు** పసుపు రంగులోకి మారుతున్నాయా (జింక్, ఐరన్ లేదా వైరస్ లక్షణాలు)?\n3. ఆకులపై మచ్చలు, ఆకుముడత లేదా పురుగులు ఏమైనా గమనించారా?"
            spoken = "పంటలో కింది ఆకులు పసుపుబారుతున్నాయా లేక పై లేత ఆకులా తెలపండి."
        elif lang == "hi":
            reply = f"आपकी {c_name if crop else 'फसल'} में सही कारण जानने के लिए, कृपया बताएं:\n\n1. क्या **नीचे के पुराने पत्ते** पीले हो रहे हैं (नाइट्रोजन की कमी या जलभराव)?\n2. या **ऊपर के नए पत्ते** पीले पड़ रहे हैं (जिंक, आयरन की कमी या लीफ कर्ल)?\n3. क्या पत्तों पर कोई धब्बे, पत्ती मरोड़ या कीड़े दिखाई दे रहे हैं?"
            spoken = "कृपया बताएं कि नीचे के पुराने पत्ते पीले हो रहे हैं या ऊपर के नए पत्ते।"
        else:
            reply = f"To provide an accurate diagnosis for your {c_name if crop else 'crop'}, could you check a few quick details?\n\n1. Are the **bottom/older leaves** turning yellow (often nitrogen deficiency or waterlogging)?\n2. Or are the **top/younger leaves** turning yellow (typically iron, zinc, or viral curl)?\n3. Are there any visible spots, leaf curling, or insects on the undersides?"
            spoken = f"For your {c_name}, are the bottom older leaves turning yellow or the top young leaves?"

        return {
            "reply": reply,
            "spoken_text": spoken,
            "tool_used": "clarification",
            "detected_language": lang,
            "suggested_actions": ["🍃 Bottom leaves yellow", "🌱 Top young leaves yellow", "🦟 Leaf curl & insects"]
        }

    if ambiguity_type == "crop_planning":
        if lang == "te":
            reply = "మీ ప్రాంతానికి సరైన లాభదాయక పంటను సూచించడానికి, దయచేసి తెలపండి:\n\n1. మీరు ఏ **సీజన్** కోసం ఆలోచిస్తున్నారు (ఖరీఫ్ / రబీ / వేసవి)?\n2. మీ పొలం **నేల రకం** ఏది (నల్లరేగడి, ఎర్ర నేలలు, ఇసుక నేలలు)?\n3. **నీటి వసతి** (బోరు/కాల్వ) ఉందా లేక వర్షాధారమా?"
            spoken = "మీరు ఏ సీజన్ మరియు నేల రకానికి పంట సూచన కోరుకుంటున్నారో తెలపండి."
        elif lang == "hi":
            reply = "आपके खेत के लिए सही फसल की सलाह देने हेतु, कृपया बताएं:\n\n1. आप किस **मौसम** के लिए योजना बना रहे हैं (खरीफ / रबी / जायद)?\n2. आपके खेत की **मिट्टी का प्रकार** क्या है (काली, लाल, दोमट या बलुई)?\n3. क्या आपके पास **सिंचाई की सुविधा** उपलब्ध है?"
            spoken = "कृपया योजना का मौसम और मिट्टी का प्रकार बताएं।"
        else:
            reply = "To recommend the best suited crop for your land, please share:\n\n1. Which **season** are you planning for (Kharif / Rabi / Summer)?\n2. What is your **soil type** (Black cotton, red loamy, sandy, or alluvial)?\n3. Do you have **assured irrigation** (borewell/canal) or is it rainfed?"
            spoken = "Please let me know your planned season, soil type, and irrigation availability."

        return {
            "reply": reply,
            "spoken_text": spoken,
            "tool_used": "clarification",
            "detected_language": lang,
            "suggested_actions": ["🌧️ Kharif Black Soil", "❄️ Rabi Loamy Soil", "☀️ Summer Irrigated"]
        }

    # Missing crop
    if lang == "te":
        reply = "మీరు ఏ పంట గురించి అడుగుతున్నారు? (ఉదా: మిర్చి, టమోటా, పత్తి, వరి, ఉల్లిపాయ). పంట పేరు చెబితే సరైన సస్యరక్షణ సూచన ఇవ్వగలను."
        spoken = "మీరు ఏ పంట గురించి అడుగుతున్నారో తెలిపితే సరైన సస్యరక్షణ సూచన ఇవ్వగలను."
    elif lang == "hi":
        reply = "आप किस फसल के बारे में पूछ रहे हैं? (जैसे: मिर्च, टमाटर, कपास, धान, प्याज)। कृपया फसल का नाम बताएं ताकि सही परामर्श मिल सके।"
        spoken = "कृपया फसल का नाम बताएं ताकि सही परामर्श मिल सके।"
    else:
        reply = "Which crop are you asking about? (e.g., Chilli, Tomato, Cotton, Paddy, Onion). Please specify your crop so I can provide the right crop protection advisory."
        spoken = "Which crop are you asking about?"

    return {
        "reply": reply,
        "spoken_text": spoken,
        "tool_used": "clarification",
        "detected_language": lang,
        "suggested_actions": ["🌶️ Chilli Protection", "🍅 Tomato Protection", "☁️ Cotton Protection", "🌾 Paddy Protection"]
    }


def get_structured_agri_advisory(crop: str, query: str, lang: str, profile: Any = None) -> Dict[str, Any]:
    """
    Renders grounded agricultural advice in the official 5-part extension structure:
    1. What may be happening
    2. What you can check in the field
    3. What you can do next
    4. Important precautions
    5. Source
    """
    c_key = crop.capitalize() if crop else "Chilli"
    crop_info = AGRI_KNOWLEDGE_BASE.get(c_key, AGRI_KNOWLEDGE_BASE.get("Chilli"))

    crop_display = crop_info["name"].get(lang, crop_info["name"]["en"])
    intent = detect_agri_intent_and_symptoms(query)
    symptoms = crop_info.get("symptoms", {})

    # Select best matching problem profile
    chosen = None
    if intent["is_leaf_curl"] and "leaf_curl" in symptoms:
        chosen = symptoms["leaf_curl"]
    elif intent["is_upper_yellow"] and "yellowing_upper" in symptoms:
        chosen = symptoms["yellowing_upper"]
    elif intent["is_lower_yellow"] and "yellowing_lower" in symptoms:
        chosen = symptoms["yellowing_lower"]
    elif intent["is_borer"] and "borer" in symptoms:
        chosen = symptoms["borer"]
    elif intent["is_blight"] and "blight_spots" in symptoms:
        chosen = symptoms["blight_spots"]
    elif intent["is_fertilizer"] and "fertilizer_guide" in crop_info:
        chosen = crop_info["fertilizer_guide"]
    elif intent["is_irrigation"] and "irrigation_guide" in crop_info:
        chosen = crop_info["irrigation_guide"]
    else:
        # Default to leaf curl or first available symptom
        chosen = symptoms.get("leaf_curl") or symptoms.get("yellowing_lower") or list(symptoms.values())[0]

    title = chosen["title"].get(lang, chosen["title"]["en"])
    happening = chosen["happening"].get(lang, chosen["happening"]["en"])
    check = chosen["check"].get(lang, chosen["check"]["en"])
    actions = chosen["actions"].get(lang, chosen["actions"]["en"])
    precautions = chosen["precautions"].get(lang, chosen["precautions"]["en"])
    source = chosen.get("source", "ICAR / State Agricultural University Extension Guidelines")

    # Build 5-part response
    if lang == "te":
        reply = f"""### 🛡️ **{crop_display}** పంట సంరక్షణ & సస్యరక్షణ మార్గదర్శి: {title}

1. **ఏమి జరుగుతుండవచ్చు:**
   {happening}

2. **పొలంలో మీరు ఏమి గమనించాలి:**
   {check}

3. **నివారణ చర్యలు / మీరు చేయవలసిన పనులు:**
{actions}

4. **ముఖ్యమైన జాగ్రత్తలు:**
   • {precautions}
   • రసాయన మందుల వాడకానికి ముందు లేబుల్ సూచనలను గమనించండి. తీవ్ర ఉధృతి ఉంటే స్థానిక వ్యవసాయ అధికారి (AO) లేదా కృషి విజ్ఞాన కేంద్రం (KVK) శాస్త్రవేత్తను సంప్రదించండి.

5. **ఆధారం / వనరు:**
   *{source}*"""
        if "ఆకుముడత" in title or "leaf_curl" in str(chosen):
            spoken = f"{crop_display} పంటలో ఆకుముడత నివారణకు లేత ఆకుల అడుగున తామర పురుగులను గమనించి లీటరు నీటికి 2 మి.లీ వేపనూనె లేదా సిఫార్సు చేసిన మందు పిచికారీ చేయండి."
        else:
            spoken = f"{crop_display} పంట సంరక్షణ కొరకు సమగ్ర సస్యరక్షణ చర్యలు మరియు లేబుల్ సూచనలు పాటించండి."

    elif lang == "hi":
        reply = f"""### 🛡️ **{crop_display}** फसल प्रबंधन एवं सुरक्षा परामर्श: {title}

1. **क्या समस्या हो सकती है:**
   {happening}

2. **खेत में क्या जांचें:**
   {check}

3. **रोकथाम एवं उपचार / क्या उपाय करें:**
{actions}

4. **महत्वपूर्ण सावधानियां:**
   • {precautions}
   • कीटनाशक के लेबल पर लिखे निर्देशों का पालन करें। गंभीर प्रकोप होने पर स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि अधिकारी से संपर्क करें।

5. **स्रोत:**
   *{source}*"""
        if "पत्ती मरोड़" in title or "leaf_curl" in str(chosen):
            spoken = f"{crop_display} में पत्ती मरोड़ की रोकथाम हेतु पत्तियों की निचली सतह पर थ्रिप्स की जांच करें और 2 मिली नीम तेल प्रति लीटर पानी में मिलाकर छिड़काव करें।"
        else:
            spoken = f"{crop_display} की सुरक्षा हेतु एकीकृत कीट प्रबंधन एवं उत्पाद लेबल के निर्देशों का पालन करें।"

    else:
        reply = f"""### 🛡️ Plant Protection Guide for **{crop_display}**: {title}

1. **What may be happening:**
   {happening}

2. **What you can check in the field:**
   {check}

3. **What you can do next (Recommended Management):**
{actions}

4. **Important precautions:**
   • {precautions}
   • Always adhere strictly to the CIBRC product label. When infestation is severe, consult your local Krishi Vigyan Kendra (KVK) or Agricultural Officer before spraying chemicals.

5. **Source:**
   *{source}*"""
        if "leaf_curl" in str(chosen) or "Leaf Curl" in title:
            spoken = f"For leaf curl in {crop_display}, inspect lower leaf surfaces for thrips and apply Neem oil at 2 ml per liter or approved foliar spray."
        else:
            spoken = f"For {crop_display} protection, follow integrated pest management practices and approved label precautions."

    return {
        "reply": reply,
        "spoken_text": spoken,
        "tool_used": "crop_doctor",
        "context_applied": {"crop": crop, "crop_display": crop_display, "condition": title},
        "suggested_actions": ["📸 Check Crop Photo", "🌿 Bio-control Methods", "🌦️ Check Spray Weather"]
    }


def get_crop_planning_recommendation(query: str, lang: str) -> Dict[str, Any]:
    """
    Provides grounded crop planning & suitability advice based on season and soil type.
    """
    q_norm = query.lower()
    is_rabi = any(w in q_norm for w in ["rabi", "winter", "రబీ", "శీతాకాలం", "रबी", "सर्दियों"])
    is_summer = any(w in q_norm for w in ["summer", "zaid", "వేసవి", "जायद", "గ్రీష్మ"])
    is_red = any(w in q_norm for w in ["red", "loam", "loamy", "sand", "ఎర్ర", "ఇసుక", "తేలికపాటి", "लाल", "दोमट", "बलुई"])

    if is_rabi:
        season_title = {"en": "Rabi Season (Winter)", "te": "రబీ సీజన్ (శీతాకాలం)", "hi": "रबी मौसम (सर्दियां)"}[lang] if lang in ["te", "hi"] else "Rabi Season (Winter)"
        crops_rec = {
            "en": "• **Bengal Gram (Chana / శనగ):** Ideal for deep black & loamy soils with residual moisture.\n• **Wheat (గేहूं / గోధుమ):** Suitable for well-drained fertile soils with 4–5 timely irrigations.\n• **Maize (మొక్కజొన్న):** High-yielding hybrid varieties perform exceptionally well in Rabi with assured water.\n• **Vegetables (Tomato / Onion):** High market returns when transplanted in October–November.",
            "te": "• **శనగలు (Bengal Gram):** నల్లరేగడి నేలల్లో మిగిలిన తేమతో తక్కువ పెట్టుబడితో ఎక్కువ దిగుబడి.\n• **గోధుమ (Wheat):** నీటి వసతి ఉన్న సారవంతమైన నేలల్లో 4–5 తడులతో మంచి దిగుబడి.\n• **మొక్కజొన్న (Maize):** రబీలో సూర్యరశ్మి ఎక్కువగా ఉండటం వల్ల ఖరీఫ్ కంటే ఎక్కువ దిగుబడి వస్తుంది.\n• **టమోటా & ఉల్లిపాయ:** అక్టోబర్-నవంబర్‌లో నాట్లు వేస్తే శీతాకాలంలో మంచి దిగుబడి మరియు గిట్టుబాటు ధర.",
            "hi": "• **चना (Bengal Gram):** काली व दोमट मिट्टी में कम पानी में उत्तम पैदावार।\n• **गेहूं (Wheat):** उपजाऊ भूमि में 4-5 समय पर सिंचाई के साथ उत्कृष्ट विकल्प।\n• **मक्का (Maize):** रबी में अधिक धूप के कारण खरीफ की तुलना में बेहतर उत्पादन।\n• **टमाटर व प्याज:** अक्टूबर-नवंबर में रोपाई करने पर अच्छे बाजार भाव और पैदावार।"
        }[lang] if lang in ["te", "hi"] else "• **Bengal Gram (Chana):** High yields in residual moisture.\n• **Wheat:** Optimal with 4–5 timely irrigations.\n• **Rabi Maize:** Exceptional yields under assured water.\n• **Tomato & Onion:** High commercial returns."
    elif is_summer:
        season_title = {"en": "Summer Season (Zaid)", "te": "వేసవి సీజన్ (జాయద్)", "hi": "जायद / ग्रीष्मकालीन मौसम"}[lang] if lang in ["te", "hi"] else "Summer Season (Zaid)"
        crops_rec = {
            "en": "• **Groundnut (Summer):** High pod yield and oil content with assured drip/sprinkler irrigation.\n• **Green Gram / Black Gram (Pulses):** Short-duration (65–70 days) pulse crops improving soil nitrogen.\n• **Sesame (తిలాలు):** Highly heat tolerant with low water requirement.",
            "te": "• **వేసవి వేరుశనగ:** స్ప్రింక్లర్ లేదా బిందు సేద్యంతో అధిక కాయల నాణ్యత మరియు దిగుబడి.\n• **మినుము / పెసర:** 65-70 రోజుల స్వల్పకాలిక పంటలు, భూమి సారవంతం అవుతుంది.\n• **నువ్వులు (Sesame):** తక్కువ నీటితో ఎండ వేడిని తట్టుకునే లాభదాయక పంట.",
            "hi": "• **ग्रीष्मकालीन मूंगफली:** ड्रिप या फव्वारा सिंचाई से बेहतरीन पैदावार।\n• **मूंग एवं उड़द:** 65-70 दिनों की अल्पकालिक दलहनी फसलें, जो भूमि की उर्वरा शक्ति बढ़ाती हैं।\n• **तिल:** कम पानी और अधिक तापमान सहन करने वाली लाभकारी फसल।"
        }[lang] if lang in ["te", "hi"] else "• **Groundnut:** High yields under sprinkler/drip.\n• **Green Gram / Black Gram:** Short duration (65–70 days).\n• **Sesame:** Drought and heat tolerant."
    else:
        # Kharif default
        season_title = {"en": "Kharif Season (Monsoon)", "te": "ఖరీఫ్ సీజన్ (వర్షాకాలం)", "hi": "खरीफ मौसम (मानसून)"}[lang] if lang in ["te", "hi"] else "Kharif Season (Monsoon)"
        if is_red:
            crops_rec = {
                "en": "• **Groundnut (వేరుశనగ):** Best suited for well-drained red sandy loams. Avoid waterlogged fields.\n• **Maize (మొక్కజొన్న):** Tolerates moderate drought, responsive to fertilizers in red soils.\n• **Red Gram / Tur (కంది):** Deep-rooted drought-hardy pulse, ideal for intercropping with Groundnut or Cotton.\n• **Chilli (మిర్చి):** Good drainage in red loamy soils prevents wilt and root diseases.",
                "te": "• **వేరుశనగ (Groundnut):** తేలికపాటి ఎర్ర నేలలకు అత్యుత్తమ పంట. నీరు నిలవకుండా చూసుకోవాలి.\n• **మొక్కజొన్న (Maize):** ఎర్ర నేలల్లో సమతుల్య ఎరువులతో అధిక దిగుబడి ఇస్తుంది.\n• **కంది (Red Gram):** లోతైన వేరు వ్యవస్థతో బెట్టను తట్టుకునే పప్పుధాన్యపు పంట.\n• **మిర్చి (Chilli):** మురుగునీటి వసతి ఉన్న ఎర్ర నేలల్లో వేరుకుళ్ళు రాకుండా ఏపుగా పెరుగుతుంది.",
                "hi": "• **मूंगफली:** लाल दोमट मिट्टी के लिए सबसे उपयुक्त। जलभराव से बचाएं।\n• **मक्का:** लाल मिट्टी में संतुलित खाद के साथ अच्छी पैदावार।\n• **अरहर (तुअर):** सूखे को सहन करने वाली दलहनी फसल, मूंगफली के साथ अंतर्वर्ती खेती के लिए उपयुक्त।\n• **मिर्च:** जल निकासी वाली लाल मिट्टी में जड़ गलन की समस्या कम होती है।"
            }[lang] if lang in ["te", "hi"] else "• **Groundnut:** Best for red sandy loams.\n• **Maize:** High response in red soils.\n• **Red Gram (Tur):** Deep rooted and drought hardy.\n• **Chilli:** Well drained soils prevent root rot."
        else:
            crops_rec = {
                "en": "• **Cotton (పత్తి / कपास):** Thrives in deep black cotton soils (regur) with high water retention.\n• **Chilli (మిర్చి / मिर्च):** High commercial value; requires ridge planting in black soils to avoid root rot.\n• **Soybean (సోయాబీన్):** Excellent pulse-oilseed crop for black soils with good monsoon drainage.\n• **Paddy (వరి / धान):** Ideal for clayey black soils with abundant water availability.",
                "te": "• **పత్తి (Cotton):** అధిక తేమ నిలుపుకునే నల్లరేగడి నేలలకు సహజంగా అనుకూలమైన పంట.\n• **మిర్చి (Chilli):** బోదెలు మరియు సాళ్ళ పద్ధతిలో సాగు చేస్తే నల్లరేగడిలో అత్యధిక లాభాలు.\n• **సోయాబీన్ (Soybean):** వర్షాకాలపు నల్లరేగడి నేలల్లో తక్కువ ఖర్చుతో స్థిరమైన దిగుబడి.\n• **వరి (Paddy):** పుష్కలంగా నీటి వసతి ఉన్న బరువైన నల్లరేగడి నేలల్లో ప్రధాన ఆహార పంట.",
                "hi": "• **कपास (Cotton):** नमी सोखने वाली गहरी काली मिट्टी के लिए सर्वोत्तम नकदी फसल।\n• **मिर्च (Chilli):** मेड़ बनाकर बुवाई करने पर काली मिट्टी में भारी मुनाफा।\n• **सोयाबीन (Soybean):** खरीफ की काली मिट्टी में कम लागत और स्थिर पैदावार।\n• **धान (Paddy):** पर्याप्त पानी वाले चिकनी काली मिट्टी के खेतों में मुख्य फसल।"
            }[lang] if lang in ["te", "hi"] else "• **Cotton:** Highly suited to deep black soils.\n• **Chilli:** High commercial value on raised ridges.\n• **Soybean:** Dependable pulse-oilseed crop.\n• **Paddy:** Ideal for heavy clayey soils with water."

    if lang == "te":
        reply = f"""### 🌾 **{season_title}** పంట ప్రణాళిక & అనుకూల పంటల సిఫార్సు

1. **నేల మరియు వాతావరణ విశ్లేషణ:**
   మీరు ఎంచుకున్న సీజన్ మరియు నేల రకానికి సరైన పంటను ఎంపిక చేసుకోవడం ద్వారా గరిష్ట దిగుబడి మరియు స్థిరమైన ఆదాయం పొందవచ్చు.

2. **సిఫార్సు చేయబడిన అనుకూల పంటలు:**
{crops_rec}

3. **సాగులో ముఖ్యమైన పద్ధతులు:**
   • విత్తన శుద్ధి తప్పనిసరిగా చేయండి (రక్షక శిలీంధ్రనాశిని లేదా ట్రైకోడెర్మా విరిడేతో).
   • మురుగునీరు నిలవకుండా పొలంలో ప్రతి 10–12 మీటర్లకు ఒక డ్రైనేజీ కాలువ తీయండి.
   • నేల పరీక్ష ఆధారంగా సమతుల్య ఎరువులను సమకూర్చండి.

4. **ముఖ్యమైన జాగ్రత్తలు:**
   • నకిలీ విత్తనాల బారిన పడకుండా అధీకృత డీలర్ల వద్ద రసీదుతో మాత్రమే విత్తనాలు కొనండి.
   • విత్తే సమయం దాటిపోకుండా చూసుకోండి.

5. **ఆధారం / వనరు:**
   *ICAR-CRIDA & ANGRAU Crop Suitability & Agro-climatic Guidelines*"""
        spoken = f"{season_title} కోసం సిఫార్సు చేసిన అనుకూల పంటలు మరియు సాగు సూచనలను సిద్ధం చేసాను."
    elif lang == "hi":
        reply = f"""### 🌾 **{season_title}** फसल नियोजन एवं उपयुक्त फसलों की सिफारिश

1. **मिट्टी और मौसम का आंकलन:**
   सही मौसम और मिट्टी के अनुसार फसल का चयन करने से लागत कम होती है और अधिकतम उत्पादन प्राप्त होता है।

2. **अनुशंसित उपयुक्त फसलें:**
{crops_rec}

3. **खेत की तैयारी एवं मुख्य कार्य:**
   • बीजोपचार अवश्य करें (फफूंदनाशी अथवा ट्राइकोडर्मा विरिडी से)।
   • भारी वर्षा में जलभराव रोकने हेतु खेत में जल निकासी की नालियां बनाएं।
   • मिट्टी जांच के आधार पर ही संतुलित एनपीके और गोबर की सड़ी खाद का उपयोग करें।

4. **महत्वपूर्ण सावधानियां:**
   • अधिकृत विक्रेता से पक्के बिल के साथ ही प्रमाणित बीज खरीदें।
   • बुवाई का उचित समय न चूकें।

5. **स्रोत:**
   *ICAR-CRIDA एवं भारतीय कृषि अनुसंधान संस्थान (IARI) फसल संस्तुति दिशा-निर्देश*"""
        spoken = f"{season_title} के लिए उपयुक्त फसलों और बुवाई की सिफारिशें तैयार हैं।"
    else:
        reply = f"""### 🌾 Crop Planning & Advisory for **{season_title}**

1. **What may be happening / Agro-climatic Assessment:**
   Matching the right crop to your soil drainage and seasonal rainfall ensures optimal return on investment and reduces disease pressure.

2. **Recommended Suitable Crops:**
{crops_rec}

3. **What you can do next (Field Preparation & Best Practices):**
   • Always perform seed treatment with approved bio-agent (Trichoderma viride @ 5-10 g/kg) or fungicide.
   • Prepare drainage channels every 10–12 meters to prevent standing water during torrential showers.
   • Apply well-decomposed Farm Yard Manure (FYM) as basal organic matter.

4. **Important precautions:**
   • Procure certified hybrid seeds exclusively from authorized dealers with a valid GST invoice.
   • Adhere strictly to the recommended sowing window to minimize pest-vector infestation.

5. **Source:**
   *ICAR-CRIDA (Central Research Institute for Dryland Agriculture) & State Agri University Packages*"""
        spoken = f"Here are the recommended crops and sowing practices for {season_title} based on ICAR guidelines."

    return {
        "reply": reply,
        "spoken_text": spoken,
        "tool_used": "crop_planning",
        "detected_language": lang,
        "suggested_actions": ["🌧️ Kharif Black Soil", "❄️ Rabi Season Crops", "💧 Drip Irrigation Tips"]
    }
