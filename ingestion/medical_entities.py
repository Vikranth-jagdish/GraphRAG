"""
Medical entity definitions and extraction utilities for healthcare documents.
"""

from typing import Set, Dict, List
import re

# Medical Conditions and Diseases
MEDICAL_CONDITIONS = {
    # Diabetes-related
    "Type 1 diabetes", "Type 2 diabetes", "T1DM", "T2DM", "diabetes mellitus",
    "gestational diabetes", "GDM", "prediabetes", "hyperglycemia", "hypoglycemia",
    "diabetic ketoacidosis", "DKA", "diabetic coma",

    # Diabetes complications
    "diabetic retinopathy", "diabetic nephropathy", "diabetic neuropathy",
    "diabetic foot", "diabetic ulcer", "diabetic cardiomyopathy",

    # Cardiovascular conditions
    "hypertension", "high blood pressure", "primary hypertension", "secondary hypertension",
    "coronary artery disease", "CAD", "myocardial infarction", "MI", "heart attack",
    "congestive heart failure", "CHF", "heart failure", "arrhythmia",
    "ischemic heart disease", "IHD", "angina", "stroke", "cerebrovascular accident", "CVA",
    "deep vein thrombosis",

    # Kidney conditions
    "chronic kidney disease", "CKD", "acute kidney injury", "AKI", "nephropathy",
    "end stage renal disease", "ESRD", "renal failure", "kidney failure",

    # Metabolic conditions
    "obesity", "overweight", "metabolic syndrome", "dyslipidemia", "hyperlipidemia",
    "hypercholesterolemia", "hypertriglyceridemia", "atherosclerosis",

    # Cancer types
    "cancer", "breast cancer", "prostate cancer", "colorectal cancer", "CRC", "mCRC",
    "nasopharyngeal cancer", "lung cancer", "ovarian cancer", "cervical cancer",
    "uterine cancer", "endometrial cancer", "gastric cancer", "stomach cancer",
    "liver cancer", "gallbladder cancer", "thyroid cancer", "pancreatic cancer",
    "oral cancer", "mouth cancer", "esophageal cancer", "oesophageal cancer",
    "laryngeal cancer", "pharyngeal cancer", "hypopharyngeal cancer",
    "biliary tract cancer", "brain cancer", "skin cancer",

    # Cancer stages and types
    "operable breast cancer", "OBC", "large operable breast cancer", "LOBC",
    "locally advanced breast cancer", "LABC", "metastatic breast cancer", "MBC",
    "ductal carcinoma in situ", "DCIS", "invasive breast cancer",
    "triple negative breast cancer", "HER2 positive breast cancer", "ER positive breast cancer",
    "inflammatory breast cancer", "basal type breast cancer",
    "castration resistant prostate cancer", "hormone sensitive prostate cancer",
    "metastatic castration-sensitive prostate cancer", "mCSPC",
    "metastatic castration-resistant prostate cancer", "mCRPC",

    # Cancer metastasis
    "bone metastasis", "bone metastases", "brain metastasis", "liver metastasis",
    "lung metastasis", "lymph node metastasis", "distant metastasis",
    "metastatic disease", "locally advanced disease", "colorectal liver metastasis", "CLM",

    # Hereditary cancer syndromes
    "hereditary breast cancer", "hereditary ovarian cancer syndrome", "HBOC",
    "BRCA1 mutation", "BRCA2 mutation", "Lynch syndrome", "HNPCC",
    "familial adenomatous polyposis", "FAP", "Turcot syndrome",
    "Gardner syndrome", "attenuated FAP", "MyH-associated polyposis",
    "Li-Fraumeni syndrome",

    # Pregnancy-related conditions
    "polyhydramnios", "pre-eclampsia", "shoulder dystocia", "uterine atony",
    "postpartum hemorrhage", "neonatal hypoglycemia", "infant respiratory distress syndrome",
    "intra-uterine death", "stillbirth", "congenital malformation", "birth injuries",
    "spontaneous abortion", "prolonged labor", "obstructed labor",

    # Cancer complications
    "multifocal disease", "multicentric disease", "Paget's disease", "micro-invasion",
    "extracapsular extension", "seminal vesicle invasion", "perineural invasion",
    "lymphovascular invasion", "vascular invasion", "angiolymphatic invasion",
    "bowel perforation", "bowel obstruction", "anastomotic leak",
    "bladder neck contracture", "urinary incontinence", "erectile dysfunction",
    "lymphocele", "spinal cord compression", "visceral crisis", "tumor flare",

    # Cancer progression
    "biochemical relapse", "biochemical recurrence", "local recurrence",
    "loco-regional recurrence", "disease progression", "treatment failure",

    # Other conditions
    "tuberculosis", "TB", "pneumonia", "sepsis", "infection", "UTI",
    "polycystic ovary syndrome", "PCOS", "thyroid disorder", "hypothyroidism",
    "hyperthyroidism", "acromegaly"
}

# Medications and Treatments
MEDICATIONS = {
    # Diabetes medications
    "metformin", "insulin", "glipizide", "gliclazide", "glibenclamide",
    "pioglitazone", "rosiglitazone", "sitagliptin", "vildagliptin", "saxagliptin",
    "canagliflozin", "dapagliflozin", "empagliflozin", "liraglutide", "exenatide",
    "dulaglutide", "semaglutide", "acarbose", "voglibose",
    "insulin glargine", "insulin detemir", "NPH insulin", "regular insulin",
    "rapid acting insulin", "basal insulin", "bolus insulin", "glucagon",

    # Hypertension medications
    "lisinopril", "enalapril", "ramipril", "losartan", "valsartan", "telmisartan",
    "amlodipine", "nifedipine", "diltiazem", "verapamil", "atenolol", "metoprolol",
    "propranolol", "hydrochlorothiazide", "HCTZ", "furosemide", "spironolactone",

    # Lipid medications
    "atorvastatin", "simvastatin", "rosuvastatin", "pravastatin", "lovastatin",
    "fenofibrate", "gemfibrozil", "ezetimibe",

    # Cancer hormone therapy
    "tamoxifen", "letrozole", "anastrozole", "exemestane", "fulvestrant",
    "bicalutamide", "enzalutamide", "abiraterone",
    "goserelin", "leuprolide", "triptorelin", "degarelix", "relugolix",

    # Cancer targeted therapy
    "trastuzumab", "lapatinib", "pertuzumab", "bevacizumab",
    "cetuximab", "panitumumab", "aflibercept", "regorafenib",

    # Chemotherapy agents
    "irinotecan", "oxaliplatin", "capecitabine", "5-fluorouracil", "5-FU",
    "leucovorin", "folinic acid", "docetaxel", "paclitaxel",
    "carboplatin", "cisplatin", "cyclophosphamide", "epirubicin",
    "doxorubicin", "vinorelbine", "gemcitabine", "mitomycin", "ixabepilone",

    # Chemotherapy regimens
    "FOLFOX", "FOLFIRI", "CAPEOX", "CAPIRI", "FEC", "FAC", "CMF", "TAC", "AC", "EC",

    # Cancer supportive medications
    "prednisolone", "prednisone", "dexamethasone",
    "zoledronic acid", "denosumab", "morphine", "venlafaxine",
    "medroxyprogesterone acetate", "G-CSF", "granulocyte colony-stimulating factor",

    # Supplements
    "calcium supplementation", "vitamin D supplementation",

    # Antibiotics
    "fluoroquinolone", "antibiotic prophylaxis",

    # Drug classes
    "ACE inhibitor", "ACEI", "ARB", "beta blocker", "calcium channel blocker", "CCB",
    "diuretic", "thiazide", "sulfonylurea", "SU", "thiazolidinedione", "TZD",
    "DPP4 inhibitor", "DPP4i", "SGLT2 inhibitor", "SGLT2i", "GLP-1 agonist", "GLP-1RA",
    "alpha glucosidase inhibitor", "AGI", "statin", "fibrate",
    "anthracycline", "taxane", "fluoropyrimidine", "platinum agent",
    "PARP inhibitor", "aromatase inhibitor", "AI",
    "SERM", "selective estrogen receptor modulator", "anti-androgen",
    "GnRH agonist", "GnRH antagonist", "LHRH agonist", "LHRH antagonist",
    "bisphosphonate", "checkpoint inhibitor"
}

# Medical Tests and Procedures
MEDICAL_TESTS = {
    # Blood tests
    "HbA1c", "hemoglobin A1c", "fasting blood glucose", "FBG", "FPG", "fasting plasma glucose",
    "postprandial glucose", "PPG", "2 hour post-prandial glucose", "2hr PPPG",
    "random blood glucose", "RBG", "oral glucose tolerance test", "OGTT", "75g OGTT", "100g OGTT",
    "C-peptide", "insulin level", "microalbumin", "creatinine", "BUN", "blood urea nitrogen",
    "lipid profile", "total cholesterol", "LDL", "HDL", "triglycerides", "TG",
    "liver function test", "LFT", "ALT", "AST", "bilirubin",
    "glucometer", "plasma calibrated glucometer",

    # Physical measurements
    "blood pressure", "BP", "systolic", "diastolic", "body mass index", "BMI",
    "waist circumference", "height", "weight", "pulse", "heart rate",
    "performance status", "ECOG performance status", "Karnofsky performance status",
    "comorbidity index",

    # Specialized cardiac tests
    "electrocardiogram", "ECG", "EKG", "echocardiogram", "echo",

    # Imaging tests - General
    "chest X-ray", "CXR", "skeletal survey", "DEXA scan", "dual-energy x-ray absorptiometry",

    # Imaging tests - CT
    "CT scan", "computed tomography", "CECT", "contrast enhanced CT", "triple phase CT",
    "CT thorax", "CT abdomen", "CT pelvis", "CT TAP", "CT colography",

    # Imaging tests - MRI
    "MRI", "magnetic resonance imaging", "breast MRI", "rectal MRI", "pelvic MRI",
    "multi-parametric MRI", "mpMRI", "whole body MRI", "WB-MRI",
    "diffusion weighted MRI", "DW-MRI", "endorectal coil", "phased-array coil",

    # Imaging tests - Nuclear medicine
    "PET-CT", "PET-MRI", "FDG PET/CT", "choline PET/CT", "PSMA PET/CT",
    "Ga-68 PSMA", "F-18 PSMA", "F-18 NaF PET",
    "bone scan", "bone scintigraphy",

    # Imaging tests - Ultrasound
    "ultrasound", "USG abdomen", "ultrasound abdomen", "breast ultrasound",
    "trans-rectal ultrasound", "TRUS", "endoscopic ultrasound", "EUS",
    "transvaginal ultrasound",

    # Breast cancer tests
    "mammography", "breast imaging", "clinical breast examination", "CBE",
    "breast self-examination", "BSE", "triple test",

    # Biopsy procedures
    "biopsy", "core biopsy", "fine needle aspiration", "FNAC", "FNA",
    "excision biopsy", "incision biopsy", "frozen section", "frozen section analysis",
    "sentinel node biopsy", "SNB", "axillary sampling",
    "trans-perineal biopsy", "trans-rectal biopsy", "systematic biopsy",
    "targeted biopsy", "MRI fusion biopsy", "cognitive fusion biopsy",
    "in-bore biopsy", "12 core biopsy",
    "image-guided biopsy", "ultrasound-guided biopsy", "CT-guided biopsy",
    "MRI-guided biopsy", "stereotactic biopsy", "vacuum-assisted biopsy",

    # Gastrointestinal tests
    "colonoscopy", "sigmoidoscopy", "rigid sigmoidoscopy", "flexible sigmoidoscopy",
    "endoscopic mucosal resection", "EMR", "polypectomy", "colonoscopic polypectomy",
    "digital rectal examination", "DRE",

    # Tumor markers
    "tumor markers", "PSA", "prostate specific antigen", "serum PSA", "total PSA",
    "free PSA", "PSA density", "PSA velocity", "PSA doubling time",
    "carcinoembryonic antigen", "CEA", "CA19.9", "CA-15.3",

    # Pathology tests
    "estrogen receptor", "ER", "progesterone receptor", "PR",
    "HER2", "HER2 IHC", "HER2 FISH", "IHC", "FISH",
    "immunohistochemistry", "fluorescence in situ hybridization",
    "Ki-67", "MIB1", "IHC4 test",
    "Gleason score", "ISUP grade", "International Society of Urologic Pathology grade",
    "histological grade", "tumor grade", "Richardson Bloom score",
    "Nottingham grade", "modified Bloom-Richardson",

    # Molecular tests
    "Oncotype DX", "Mammaprint", "Coloprint", "gene expression profiling",
    "multi-gene signature", "RAS mutation", "KRAS mutation", "BRAF mutation",
    "NRAS mutation", "MMR testing", "mismatch repair", "microsatellite instability",
    "MSI", "MSI-H", "dMMR", "deficient MMR",
    "BRCA testing", "germline mutation testing", "somatic mutation testing",
    "tumor molecular profiling",

    # Staging and assessment
    "TNM staging", "AJCC staging", "UICC staging", "Dukes classification",
    "T stage", "N stage", "M stage", "pathological stage", "clinical stage",
    "PIRADS", "PI-RADS score", "risk stratification",

    # Pathology assessment
    "circumferential resection margin", "CRM", "resection margin", "surgical margin",
    "positive margin", "negative margin", "R0 resection", "R1 resection",
    "lymph node yield", "lymph node count", "lymph node dissection",
    "extended lymph node dissection", "eLND", "pelvic lymph node dissection", "PLND",
    "tumor regression grade", "TRG score", "pathological complete response", "pCR",
    "downstaging", "tumor shrinkage",

    # Risk assessment tools
    "Briganti nomogram", "Roach formula", "Partin nomogram", "MSKCC nomogram",

    # Other specialized tests
    "fundoscopy", "ophthalmoscopy", "retinal examination", "dilated fundus examination",
    "foot examination", "monofilament test", "vibration perception test",
    "ankle brachial index", "ABI", "Doppler study",
    "tissue transglutaminase antibody", "tTG antibody",
    "gestational diabetes screening", "cyst aspiration",

    # Urine tests
    "urine routine", "urine microscopy", "proteinuria", "albumin creatinine ratio", "ACR",
    "microalbuminuria", "spot urine", "24-hour urine"
}

# Medical Values and Targets
MEDICAL_VALUES = {
    # Diabetes targets
    "HbA1c <7%", "HbA1c <=7%", "fasting glucose 80-130", "postprandial <180",
    "blood glucose target", "glycemic control", "euglycemia",
    "2hr glucose ≥140 mg/dL", "fasting glucose ≥126 mg/dL",
    "blood glucose >250 mg/dL", "blood glucose <70 mg/dL",

    # Blood pressure targets
    "BP <140/90", "BP <=140/90", "BP <130/80", "normotension", "optimal BP",

    # Lipid targets
    "LDL <100", "LDL <70", "HDL >40", "HDL >50", "triglycerides <150",

    # BMI categories
    "BMI <18.5", "underweight", "BMI 18.5-22.9", "normal weight",
    "BMI 23-27.5", "overweight", "BMI >27.5", "obese",

    # PSA values
    "PSA <4 ng/mL", "PSA 4-10 ng/mL", "PSA >10 ng/mL",
    "PSA >20 ng/mL", "PSA >50 ng/mL", "PSA nadir", "PSA progression",

    # Gleason and ISUP grades
    "Gleason 6", "Gleason 7", "Gleason 8-10", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3",
    "ISUP grade 1", "ISUP grade 2", "ISUP grade 3", "ISUP grade 4", "ISUP grade 5",

    # Tumor grades
    "Grade I", "Grade II", "Grade III", "low grade", "intermediate grade", "high grade",
    "well differentiated", "moderately differentiated", "poorly differentiated", "undifferentiated",

    # TNM staging values
    "T1 tumor", "T2 tumor", "T3 tumor", "T4 tumor",
    "N0", "N1", "N2", "N3", "M0", "M1", "M1a", "M1b",

    # Cancer stages
    "Stage I", "Stage II", "Stage III", "Stage IV",
    "Stage IIA", "Stage IIB", "Stage IIC",
    "Stage IIIA", "Stage IIIB", "Stage IIIC",
    "Stage IVA", "Stage IVB",
    "Dukes A", "Dukes B", "Dukes C",

    # Risk categories
    "low risk", "intermediate risk", "favorable intermediate risk",
    "unfavorable intermediate risk", "high risk", "very high risk",

    # Disease extent
    "organ confined", "locally advanced", "metastatic",
    "resectable", "unresectable", "borderline resectable", "oligometastatic",

    # Node status
    "node negative", "node positive", "1-3 positive nodes", ">3 positive nodes",
    "4-9 positive nodes", "≥10 positive nodes",

    # Margin status
    "margin positive", "margin negative", "close margin",

    # Receptor status
    "ER positive", "ER negative", "PR positive", "PR negative",
    "HER2 positive", "HER2 negative", "triple negative",
    "hormone receptor positive",

    # Prostate cancer specific
    "castrate level testosterone", "testosterone <50 ng/mL",
    "biochemical failure", "clinical progression",

    # Survival outcomes
    "5-year survival", "10-year survival", "overall survival",
    "disease-free survival", "progression-free survival",
    "recurrence-free survival", "event-free survival",
    "cancer-specific survival", "metastasis-free survival"
}

# Medical Organizations and Guidelines
MEDICAL_ORGANIZATIONS = {
    # Indian organizations
    "ICMR", "Indian Council of Medical Research", "AIIMS", "All India Institute of Medical Sciences",
    "Ministry of Health and Family Welfare", "National Health Mission", "NHM",
    "Diabetes Foundation India", "Indian Medical Association", "IMA",
    "Tata Memorial Hospital", "TMH", "ACTREC",
    "Diabetes in Pregnancy Study Group",

    # International organizations
    "WHO", "World Health Organization", "ADA", "American Diabetes Association",
    "ESC", "European Society of Cardiology", "AHA", "American Heart Association",
    "KDIGO", "Kidney Disease Improving Global Outcomes",
    "National Comprehensive Cancer Network", "NCCN",
    "St.Gallen International Expert Consensus",
    "European Society of Medical Oncology", "ESMO",
    "National Institute for Health and Care Excellence", "NICE",
    "European Organisation for Research and Treatment of Cancer", "EORTC",
    "National Cancer Institute", "NCI",
    "American Society of Clinical Oncology", "ASCO",
    "Union for International Cancer Control", "UICC",
    "American Joint Committee on Cancer", "AJCC",

    # Clinical teams
    "multidisciplinary team", "MDT", "tumor board",

    # Guidelines and criteria
    "clinical practice guidelines", "treatment guidelines", "standard treatment guidelines", "STG",
    "evidence-based guidelines", "consensus statement", "position statement",
    "NCCN guidelines", "ESMO guidelines", "NICE guidelines", "WHO guidelines", "ICMR guidelines",
    "Bethesda guidelines", "Amsterdam criteria"
}

# Anatomical Terms and Systems
ANATOMICAL_TERMS = {
    # Endocrine and metabolic
    "pancreas", "beta cells", "insulin resistance", "insulin secretion",
    "liver", "liver segment", "future liver remnant", "FLR", "portal vein", "hepatic vein",

    # Renal
    "kidney", "nephron", "glomerulus",

    # Eyes
    "retina", "macula", "optic nerve",

    # Nervous system
    "peripheral nerves", "autonomic nervous system",

    # Cardiovascular
    "cardiovascular system", "coronary arteries", "carotid arteries", "peripheral arteries",

    # Extremities
    "foot", "toes", "lower extremity", "upper extremity",

    # Breast anatomy
    "breast", "mammary gland", "nipple", "areola",
    "axilla", "axillary lymph nodes", "supraclavicular lymph nodes",
    "infraclavicular lymph nodes", "internal mammary nodes", "IMN",
    "sentinel lymph node", "chest wall", "pectoralis muscle", "tumor bed",
    "breast quadrant", "upper outer quadrant", "lower outer quadrant",
    "upper inner quadrant", "lower inner quadrant",

    # Gastrointestinal anatomy
    "colon", "rectum", "sigmoid colon", "descending colon", "transverse colon",
    "ascending colon", "cecum", "caecum", "hepatic flexure", "splenic flexure",
    "anal canal", "anal verge", "mesorectum", "mesorectal fascia",
    "pelvic floor", "levator ani", "puborectalis", "sphincter",
    "internal sphincter", "external sphincter",

    # Prostate and male genitourinary
    "prostate", "prostate gland", "prostatic capsule", "seminal vesicles",
    "vas deferens", "ejaculatory duct", "urethra", "membranous urethra",
    "prostatic urethra", "bladder neck", "neurovascular bundle",

    # Pelvic anatomy
    "pelvic lymph nodes", "obturator nodes", "internal iliac nodes",
    "external iliac nodes", "common iliac nodes", "pelvic plexus",
    "dorsal venous complex", "endopelvic fascia", "Denonvilliers fascia",
    "pelvic side wall", "bony pelvis", "sacrum", "coccyx",

    # Female reproductive anatomy
    "uterus", "ovary", "fallopian tube", "cervix", "vagina",
    "placenta", "fetus", "umbilical cord"
}

# Symptoms and Signs
SYMPTOMS_SIGNS = {
    # Diabetes symptoms
    "polyuria", "polydipsia", "polyphagia", "weight loss", "fatigue", "weakness",
    "blurred vision", "frequent urination", "excessive thirst", "increased hunger",
    "non-healing wounds", "slow healing", "recurrent infections",
    "tingling", "numbness", "paresthesia", "burning sensation", "nocturia",

    # Cardiovascular symptoms
    "chest pain", "shortness of breath", "dyspnea", "palpitations",
    "dizziness", "syncope", "edema", "leg swelling",

    # Breast symptoms
    "breast lump", "nipple discharge", "nipple retraction", "skin dimpling",
    "peau d'orange", "breast pain", "mastalgia", "axillary lump", "galactorrhea",

    # Gastrointestinal symptoms
    "bleeding per rectum", "rectal bleeding", "change in bowel habit",
    "constipation", "diarrhea", "mucus in stool", "blood in stool",
    "melena", "tenesmus",

    # Urinary symptoms
    "difficulty urinating", "urinary hesitancy", "weak urinary stream",
    "urinary retention", "hematuria", "incontinence",
    "stress incontinence", "urge incontinence", "fecal incontinence",

    # Cancer-related symptoms
    "bone pain", "pathological fracture", "back pain", "radicular pain", "sciatica",

    # Endocrine symptoms
    "hot flushes", "vasomotor symptoms", "night sweats",
    "gynecomastia", "loss of libido", "sexual dysfunction",

    # Lymphatic symptoms
    "lymphedema", "arm swelling",

    # Advanced cancer symptoms
    "ascites", "jaundice", "fungating wound", "ulceration", "skin infiltration",
    "seizures", "altered consciousness", "confusion",
    "paraparesis", "paraplegia", "cord compression symptoms",

    # General symptoms
    "headache", "nausea", "vomiting", "abdominal pain", "fever"
}

# Medical Procedures and Interventions
PROCEDURES = {
    # Lifestyle and conservative management
    "lifestyle modification", "dietary counseling", "exercise prescription",
    "patient education", "self-monitoring", "SMBG", "self-monitoring blood glucose",
    "continuous glucose monitoring", "CGM",
    "medical nutrition therapy", "MNT", "diet therapy", "nutrition counseling",
    "active surveillance", "AS", "watchful waiting", "observation", "expectant management",

    # General diabetes procedures
    "insulin injection", "insulin injection technique", "insulin titration",
    "subcutaneous injection", "oral medication", "dose escalation", "dose reduction",

    # Bariatric procedures
    "bariatric surgery", "gastric bypass", "sleeve gastrectomy",

    # Cardiac procedures
    "coronary angioplasty", "PCI", "CABG", "coronary artery bypass",

    # Renal procedures
    "hemodialysis", "peritoneal dialysis", "kidney transplant",

    # Ophthalmic procedures
    "laser photocoagulation", "vitrectomy", "cataract surgery",

    # Breast surgery
    "mastectomy", "simple mastectomy", "modified radical mastectomy", "radical mastectomy",
    "breast conserving surgery", "BCT", "lumpectomy", "wide local excision", "quadrantectomy",
    "oncoplastic surgery", "partial breast reconstruction", "whole breast reconstruction",
    "breast reconstruction", "immediate reconstruction", "delayed reconstruction",
    "latissimus dorsi flap", "TRAM flap", "DIEP flap",
    "tissue expander", "implant reconstruction", "nipple reconstruction",
    "axillary clearance", "axillary dissection",
    "level I dissection", "level II dissection", "level III dissection",
    "Hadfield surgery", "microdochectomy", "duct excision",

    # Colorectal surgery
    "right hemicolectomy", "left hemicolectomy",
    "extended right hemicolectomy", "extended left hemicolectomy",
    "transverse colectomy", "sigmoid colectomy",
    "anterior resection", "low anterior resection", "LAR",
    "ultra-low anterior resection", "abdominoperineal excision", "APR",
    "abdominoperineal resection", "Hartmann procedure",
    "colostomy", "ileostomy", "stoma formation", "stoma reversal",
    "temporary stoma", "permanent stoma",
    "total mesorectal excision", "TME",
    "transanal excision", "local excision",
    "transanal endoscopic microsurgery", "TEMS",
    "intersphincteric dissection",

    # Liver surgery
    "liver resection", "hepatectomy", "metastasectomy", "liver metastasectomy",
    "segmentectomy", "lobectomy", "extended hepatectomy", "two-stage hepatectomy",

    # Liver interventions
    "portal vein embolization", "PVE",
    "radiofrequency ablation", "RFA", "microwave ablation", "cryoablation",
    "selective internal radiation therapy", "SIRT",
    "yttrium-90 microspheres", "Y-90 radioembolization",
    "transarterial chemoembolization", "TACE",

    # Prostate surgery
    "radical prostatectomy", "RP", "RRP", "radical retropubic prostatectomy",
    "robot-assisted prostatectomy", "RALP", "RARP",
    "laparoscopic prostatectomy", "LRP", "open prostatectomy",
    "retro-pubic approach", "trans-perineal approach",
    "nerve-sparing surgery", "bilateral nerve-sparing", "unilateral nerve-sparing",
    "retzius-sparing", "salvage prostatectomy", "salvage surgery",
    "pelvic exenteration",

    # Endocrine surgery
    "orchiectomy", "bilateral orchiectomy", "surgical castration", "medical castration",

    # Minimally invasive surgery
    "laparoscopic surgery", "laparoscopy-assisted surgery", "robotic surgery",
    "minimally invasive surgery", "open surgery",
    "hand-assisted laparoscopy", "single-port laparoscopy",

    # Anastomosis techniques
    "stapled anastomosis", "hand-sewn anastomosis",
    "end-to-end anastomosis", "coloanal anastomosis",
    "ileoanal anastomosis", "primary anastomosis", "delayed anastomosis",

    # Biopsy and mapping procedures
    "sentinel node mapping", "lymphatic mapping",
    "blue dye injection", "radioisotope injection", "technetium injection",
    "patent blue dye", "methylene blue",

    # Cancer therapy - Systemic
    "androgen deprivation therapy", "ADT", "hormone therapy", "endocrine therapy",
    "neoadjuvant therapy", "NACT", "neoadjuvant chemotherapy",
    "neoadjuvant chemoradiotherapy", "NACTRT",
    "adjuvant therapy", "adjuvant chemotherapy", "adjuvant radiotherapy",
    "adjuvant hormone therapy", "perioperative chemotherapy",
    "palliative chemotherapy", "first-line chemotherapy",
    "second-line chemotherapy", "third-line chemotherapy", "salvage chemotherapy",
    "combination chemotherapy", "single-agent chemotherapy",
    "sequential chemotherapy", "dose-dense chemotherapy",
    "immunotherapy", "checkpoint inhibitor therapy",
    "targeted therapy", "molecular targeted therapy",
    "anti-EGFR therapy", "anti-VEGF therapy", "anti-HER2 therapy",

    # Radiotherapy - External beam
    "external beam radiotherapy", "EBRT",
    "intensity modulated radiotherapy", "IMRT",
    "3D conformal radiotherapy", "3DCRT",
    "image guided radiotherapy", "IGRT",
    "volumetric modulated arc therapy", "VMAT",
    "stereotactic ablative radiotherapy", "SABR",
    "stereotactic body radiotherapy", "SBRT",
    "stereotactic radiosurgery", "SRS",
    "whole brain radiotherapy", "WBRT",

    # Radiotherapy - Breast specific
    "partial breast irradiation", "APBI",
    "accelerated partial breast irradiation",
    "whole breast irradiation", "post-mastectomy radiotherapy", "PMRT",
    "chest wall irradiation",

    # Radiotherapy - Pelvic
    "pelvic radiotherapy", "pelvic nodal irradiation",

    # Radiotherapy - Techniques
    "brachytherapy", "low dose rate brachytherapy", "LDR brachytherapy",
    "high dose rate brachytherapy", "HDR brachytherapy",
    "interstitial brachytherapy", "intracavitary brachytherapy",
    "boost radiotherapy", "tumor bed boost", "lymph node boost",

    # Radiotherapy - Timing
    "adjuvant radiotherapy", "salvage radiotherapy", "palliative radiotherapy",
    "short course radiotherapy", "SCPRT", "long course radiotherapy",

    # Radiotherapy - Fractionation
    "hypofractionated radiotherapy", "moderate hypofractionation",
    "ultra-hypofractionation", "conventional fractionation",

    # Chemoradiotherapy
    "chemoradiotherapy", "CTRT", "concurrent chemoradiotherapy",

    # Supportive and palliative care
    "supportive care", "best supportive care", "BSC",
    "palliative care", "hospice care", "symptom control",
    "pain management", "pain control", "morphine therapy", "opioid therapy",
    "bisphosphonate therapy", "bone-directed therapy",
    "skeletal-related event prevention",

    # Genetic services
    "genetic counseling", "genetic testing",

    # Risk-reducing procedures
    "risk-reducing surgery", "prophylactic surgery",
    "risk-reducing mastectomy", "bilateral prophylactic mastectomy", "BPM",
    "risk-reducing salpingo-oophorectomy", "RRSO",

    # Screening
    "ovarian cancer screening", "CA-125 testing",

    # Follow-up and monitoring
    "follow-up", "surveillance", "disease monitoring",
    "response assessment", "restaging",

    # Clinical research
    "clinical trial", "randomized controlled trial", "RCT",
    "phase I trial", "phase II trial", "phase III trial"
}

# Comprehensive medical entity dictionary
MEDICAL_ENTITIES = {
    "conditions": MEDICAL_CONDITIONS,
    "medications": MEDICATIONS,
    "tests": MEDICAL_TESTS,
    "values": MEDICAL_VALUES,
    "organizations": MEDICAL_ORGANIZATIONS,
    "anatomy": ANATOMICAL_TERMS,
    "symptoms": SYMPTOMS_SIGNS,
    "procedures": PROCEDURES
}

# Medical abbreviations mapping
MEDICAL_ABBREVIATIONS = {
    # Diabetes
    "T1DM": "Type 1 diabetes mellitus",
    "T2DM": "Type 2 diabetes mellitus",
    "GDM": "Gestational diabetes mellitus",
    "DKA": "Diabetic ketoacidosis",
    "HbA1c": "Hemoglobin A1c",
    "FPG": "Fasting plasma glucose",
    "PPG": "Postprandial glucose",
    "PPPG": "Post-prandial plasma glucose",
    "OGTT": "Oral glucose tolerance test",
    "SMBG": "Self-monitoring blood glucose",
    "CGM": "Continuous glucose monitoring",
    "MNT": "Medical nutrition therapy",

    # Cardiovascular
    "CAD": "Coronary artery disease",
    "MI": "Myocardial infarction",
    "CHF": "Congestive heart failure",
    "BP": "Blood pressure",

    # Renal
    "CKD": "Chronic kidney disease",
    "AKI": "Acute kidney injury",
    "ESRD": "End stage renal disease",

    # General conditions
    "PCOS": "Polycystic ovary syndrome",
    "UTI": "Urinary tract infection",

    # Cancer types and stages
    "OBC": "Operable breast cancer",
    "LOBC": "Large operable breast cancer",
    "LABC": "Locally advanced breast cancer",
    "MBC": "Metastatic breast cancer",
    "DCIS": "Ductal carcinoma in situ",
    "HBOC": "Hereditary breast ovarian cancer syndrome",
    "CRC": "Colorectal cancer",
    "mCRC": "Metastatic colorectal cancer",
    "CLM": "Colorectal liver metastasis",
    "FAP": "Familial adenomatous polyposis",
    "HNPCC": "Hereditary non-polyposis colorectal cancer",
    "mCSPC": "Metastatic castration-sensitive prostate cancer",
    "mCRPC": "Metastatic castration-resistant prostate cancer",

    # Cancer surgery
    "TME": "Total mesorectal excision",
    "LAR": "Low anterior resection",
    "APR": "Abdominoperineal resection",
    "TEMS": "Transanal endoscopic microsurgery",
    "EMR": "Endoscopic mucosal resection",
    "BCT": "Breast conserving surgery",
    "SNB": "Sentinel node biopsy",
    "RP": "Radical prostatectomy",
    "RRP": "Radical retropubic prostatectomy",
    "RALP": "Robot-assisted laparoscopic prostatectomy",
    "RARP": "Robot-assisted radical prostatectomy",
    "LRP": "Laparoscopic radical prostatectomy",
    "PLND": "Pelvic lymph node dissection",
    "eLND": "Extended lymph node dissection",
    "BPM": "Bilateral prophylactic mastectomy",
    "RRSO": "Risk-reducing salpingo-oophorectomy",

    # Liver procedures
    "PVE": "Portal vein embolization",
    "FLR": "Future liver remnant",
    "RFA": "Radiofrequency ablation",
    "SIRT": "Selective internal radiation therapy",
    "TACE": "Transarterial chemoembolization",

    # Tumor markers and tests
    "PSA": "Prostate specific antigen",
    "CEA": "Carcinoembryonic antigen",
    "DRE": "Digital rectal examination",
    "CBE": "Clinical breast examination",
    "BSE": "Breast self-examination",
    "FNA": "Fine needle aspiration",
    "FNAC": "Fine needle aspiration cytology",

    # Pathology
    "ER": "Estrogen receptor",
    "PR": "Progesterone receptor",
    "HER2": "Human epidermal growth factor receptor 2",
    "IHC": "Immunohistochemistry",
    "FISH": "Fluorescence in situ hybridization",
    "MMR": "Mismatch repair",
    "MSI": "Microsatellite instability",
    "MSI-H": "Microsatellite instability high",
    "dMMR": "Deficient mismatch repair",
    "ISUP": "International Society of Urologic Pathology",
    "CRM": "Circumferential resection margin",
    "TRG": "Tumor regression grade",
    "pCR": "Pathological complete response",

    # Imaging
    "CT": "Computed tomography",
    "CECT": "Contrast enhanced CT",
    "MRI": "Magnetic resonance imaging",
    "mpMRI": "Multi-parametric MRI",
    "WB-MRI": "Whole body MRI",
    "DW-MRI": "Diffusion weighted MRI",
    "PET": "Positron emission tomography",
    "USG": "Ultrasonography",
    "TRUS": "Trans-rectal ultrasound",
    "EUS": "Endoscopic ultrasound",
    "PIRADS": "Prostate Imaging-Reporting and Data System",
    "CXR": "Chest X-ray",
    "DEXA": "Dual-energy x-ray absorptiometry",

    # Staging
    "TNM": "Tumor Node Metastasis",
    "UICC": "Union for International Cancer Control",
    "AJCC": "American Joint Committee on Cancer",

    # Cancer therapy
    "ADT": "Androgen deprivation therapy",
    "GnRH": "Gonadotropin-releasing hormone",
    "LHRH": "Luteinizing hormone-releasing hormone",
    "CAB": "Combined androgen blockade",
    "NACT": "Neoadjuvant chemotherapy",
    "NACTRT": "Neoadjuvant chemoradiotherapy",
    "CTRT": "Chemoradiotherapy",

    # Chemotherapy
    "5-FU": "5-fluorouracil",
    "LV": "Leucovorin",
    "FA": "Folinic acid",
    "FOLFOX": "Folinic acid, fluorouracil, oxaliplatin",
    "FOLFIRI": "Folinic acid, fluorouracil, irinotecan",
    "CAPEOX": "Capecitabine, oxaliplatin",
    "CAPIRI": "Capecitabine, irinotecan",
    "FEC": "Fluorouracil, epirubicin, cyclophosphamide",
    "FAC": "Fluorouracil, doxorubicin, cyclophosphamide",
    "CMF": "Cyclophosphamide, methotrexate, fluorouracil",
    "TAC": "Docetaxel, doxorubicin, cyclophosphamide",
    "AC": "Doxorubicin, cyclophosphamide",
    "EC": "Epirubicin, cyclophosphamide",
    "G-CSF": "Granulocyte colony-stimulating factor",

    # Drug classes
    "ACEI": "ACE inhibitor",
    "ARB": "Angiotensin receptor blocker",
    "CCB": "Calcium channel blocker",
    "SU": "Sulfonylurea",
    "TZD": "Thiazolidinedione",
    "DPP4i": "DPP4 inhibitor",
    "SGLT2i": "SGLT2 inhibitor",
    "GLP-1RA": "GLP-1 receptor agonist",
    "AGI": "Alpha glucosidase inhibitor",
    "AI": "Aromatase inhibitor",
    "SERM": "Selective estrogen receptor modulator",

    # Radiotherapy
    "EBRT": "External beam radiotherapy",
    "IMRT": "Intensity modulated radiotherapy",
    "3DCRT": "3D conformal radiotherapy",
    "IGRT": "Image guided radiotherapy",
    "VMAT": "Volumetric modulated arc therapy",
    "SABR": "Stereotactic ablative radiotherapy",
    "SBRT": "Stereotactic body radiotherapy",
    "SRS": "Stereotactic radiosurgery",
    "WBRT": "Whole brain radiotherapy",
    "LDR": "Low dose rate",
    "HDR": "High dose rate",
    "APBI": "Accelerated partial breast irradiation",
    "PMRT": "Post-mastectomy radiotherapy",
    "SCPRT": "Short course preoperative radiotherapy",
    "IMN": "Internal mammary nodes",
    "SCF": "Supraclavicular fossa",

    # Breast reconstruction
    "TRAM": "Transverse rectus abdominis myocutaneous",
    "DIEP": "Deep inferior epigastric perforator",

    # Organizations
    "ICMR": "Indian Council of Medical Research",
    "WHO": "World Health Organization",
    "ADA": "American Diabetes Association",
    "TMH": "Tata Memorial Hospital",
    "NCCN": "National Comprehensive Cancer Network",
    "ESMO": "European Society of Medical Oncology",
    "NICE": "National Institute for Health and Care Excellence",
    "EORTC": "European Organisation for Research and Treatment of Cancer",
    "NCI": "National Cancer Institute",
    "ASCO": "American Society of Clinical Oncology",
    "MDT": "Multidisciplinary team",

    # Other
    "BMI": "Body mass index",
    "ECG": "Electrocardiogram",
    "LFT": "Liver function test",
    "ACR": "Albumin creatinine ratio",
    "BSC": "Best supportive care",
    "RCT": "Randomized controlled trial",
    "AS": "Active surveillance",
    "NPH": "Neutral protamine Hagedorn",
    "TSH": "Thyroid stimulating hormone",
    "tTG": "Tissue transglutaminase",
    "ANC": "Antenatal care",
    "ANM": "Auxiliary nurse midwife",
    "PHC": "Primary health centre",
    "CHC": "Community health centre",
    "DH": "District hospital",
    "MC": "Medical college"
}

def get_all_medical_terms() -> Set[str]:
    """Get all medical terms from all categories."""
    all_terms = set()
    for category_terms in MEDICAL_ENTITIES.values():
        all_terms.update(category_terms)
    return all_terms

def get_medical_terms_by_category(category: str) -> Set[str]:
    """Get medical terms for a specific category."""
    return MEDICAL_ENTITIES.get(category, set())

def expand_abbreviations(text: str) -> str:
    """Expand medical abbreviations in text."""
    expanded_text = text
    for abbrev, full_form in MEDICAL_ABBREVIATIONS.items():
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(abbrev) + r'\b'
        expanded_text = re.sub(pattern, f"{abbrev} ({full_form})", expanded_text)
    return expanded_text

def extract_medical_values(text: str) -> List[str]:
    """Extract medical values and ranges from text."""
    value_patterns = [
        r'HbA1c\s*[<>=]+\s*\d+\.?\d*%?',
        r'BP\s*[<>=]+\s*\d+/\d+',
        r'BMI\s*[<>=]+\s*\d+\.?\d*',
        r'LDL\s*[<>=]+\s*\d+',
        r'HDL\s*[<>=]+\s*\d+',
        r'\d+\s*mg/dl',
        r'\d+\s*mmHg',
        r'\d+\.?\d*%'
    ]

    values = []
    for pattern in value_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        values.extend(matches)

    return values