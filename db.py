import sqlite3
from typing import Optional
from pathlib import Path
import json

def init_db(conn):
    # Connect to SQLite (or create db file)
    cursor = conn.cursor()

    # Create tables with corrected SQLite syntax
    cursor.executescript(
    """
    DROP TABLE IF EXISTS lexical_entries;
    DROP TABLE IF EXISTS semantic_categories;
    DROP TABLE IF EXISTS word_forms;
    DROP TABLE IF EXISTS form_representations;
    DROP TABLE IF EXISTS senses;
    DROP TABLE IF EXISTS sense_examples;
    DROP TABLE IF EXISTS sense_relations;
    DROP TABLE IF EXISTS syntactic_patterns;
    DROP TABLE IF EXISTS equivalents;
    DROP TABLE IF EXISTS phrase_proverbs;
    DROP TABLE IF EXISTS multimedia;
    drop table if exists variants;
    drop table if exists subject_categories;
                         
    CREATE TABLE IF NOT EXISTS lexical_entries (
        id INTEGER PRIMARY KEY NOT NULL,
        part_of_speech TEXT NOT NULL,
        written_form TEXT NOT NULL,
        homonym_number INTEGER NOT NULL,
        lexical_unit TEXT NOT NULL,
        vocabulary_level TEXT
    );

    create table if not exists subject_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        lexical_entry_id INTEGER NOT NULL
    );

    create table if not exists phrase_proverbs (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER,
        written_form TEXT NOT NULL,
        lexical_unit TEXT NOT NULL
    );
                         
    create table if not exists equivalents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lexical_entry_id INTEGER NOT NULL,
        sense_id INTEGER NOT NULL,
        language TEXT NOT NULL,
        lemma TEXT NOT NULL,
        definition TEXT NOT NULL
    );
                         
    create table if not exists semantic_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lexical_entry_id INTEGER NOT NULL,
        base TEXT NOT NULL,
        detail TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS word_forms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lexical_entry_id INTEGER NOT NULL,
        pronunciation TEXT,
        sound TEXT,
        type_of_form TEXT NOT NULL,
        written_form TEXT
    );

    CREATE TABLE IF NOT EXISTS form_representations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_form_id INTEGER NOT NULL,
        pronunciation TEXT,
        sound TEXT,
        type_of_form TEXT NOT NULL,
        written_form TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS senses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lexical_entry_id INTEGER NOT NULL,
        definition TEXT NOT NULL,
        annotation TEXT,
        syntactic_annotation TEXT
    );

    CREATE TABLE IF NOT EXISTS sense_examples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sense_id INTEGER NOT NULL REFERENCES senses(id) ON DELETE CASCADE,
        example TEXT NOT NULL,
        type_of_example TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sense_relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sense_id INTEGER NOT NULL REFERENCES senses(id) ON DELETE CASCADE,
        lexical_entry_id INTEGER NOT NULL ,
        type_of_relation TEXT NOT NULL,
        lemma TEXT NOT NULL,
        homonym_number INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS syntactic_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sense_id INTEGER NOT NULL REFERENCES senses(id) ON DELETE CASCADE,
        pattern TEXT NOT NULL
    );

    create table if not exists multimedia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sense_id INTEGER NOT NULL REFERENCES senses(id) ON DELETE CASCADE,
        type_of_media TEXT NOT NULL,
        label TEXT NOT NULL,
        url TEXT NOT NULL
    );

    create table if not exists variants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lexical_entry_id INTEGER NOT NULL,
        variant TEXT NOT NULL
    );
    """)

    conn.commit()

language_map = {
    "인도네시아어": "Indonesian",
    "중국어": "Chinese",
    "베트남어": "Vietnamese",
    "아랍어": "Arabic",
    "일본어": "Japanese",
    "몽골어": "Mongolian",
    "러시아어": "Russian",
    "스페인어": "Spanish",
    "kor": "Korean",
    "타이어": "Thai",
    "영어": "English",
    "프랑스어": "French"
}

lexical_unit_map = {
    "문법‧표현": "Grammar and Expression",
    "단어": "Word",
    "속담": "Proverb",
    "관용구": "Idiom",
    "구": "Phrase"
}

vocab_level_map = {
    "초급": "Beginner",
    "중급": "Intermediate",
    "고급": "Advanced",
    "없음": "None"
}

pos_map = {
    "관형사": "Determiner",
    "품사 없음": "None",
    "부사": "Adverb",
    "수사": "Numeral",
    "감탄사": "Interjection",
    "보조 동사": "Auxiliary Verb",
    "대명사": "Pronoun",
    "어미": "Ending",
    "접사": "Affix",
    "의존 명사": "Bound Noun",
    "보조 형용사": "Auxiliary Adjective",
    "형용사": "Adjective",
    "명사": "Noun",
    "조사": "Particle",
    "동사": "Verb"
}

type_map = {
    "파생어": "Derived Word",
    "사진": "Photo",
    "센말": "Fortis Form",
    "☞(가 보라)": "See also (가)",
    "동영상": "Video",
    "활용": "Conjugation",
    "준말": "Abbreviation",
    "본말": "Full Form",
    "반대말": "Antonym",
    "작은말": "Diminutive Form",
    "참고어": "Reference Word",
    "발음": "Pronunciation",
    "큰말": "Augmentative Form",
    "문장": "Sentence",
    "유의어": "Synonym",
    "낮춤말": "Humble Speech",
    "대화": "Dialogue",
    "여린말": "Lenis Form",
    "1": "1",
    "구": "Phrase",
    "높임말": "Honorific Speech"
}

semantic_category_map = {
    "가사 행위": "Household Activities",
    "가족 행사": "Family Events",
    "감각": "Sensation",
    "감정": "Emotion",
    "개념": "Concept",
    "건물 종류": "Types of Buildings",
    "경제 산물": "Economic Goods",
    "경제 상태": "Economic Conditions",
    "경제 생활": "Economic Life",
    "경제 수단": "Economic Means",
    "경제 행위": "Economic Actions",
    "경제 행위 장소": "Economic Activity Locations",
    "경제 행위 주체": "Economic Actors",
    "곡류": "Grains",
    "곤충류": "Insects",
    "공공 기관": "Public Institutions",
    "과일": "Fruits",
    "교수 학습 주체": "Teaching/Learning Agents",
    "교수 학습 행위": "Teaching/Learning Actions",
    "교육": "Education",
    "교육 기관": "Educational Institutions",
    "교통 수단": "Transportation Means",
    "교통 이용 장소": "Transportation Locations",
    "교통 이용 행위": "Transportation Use",
    "기상 및 기후": "Weather and Climate",
    "능력": "Ability",
    "대중 문화": "Popular Culture",
    "동물 소리": "Animal Sounds",
    "동물류": "Animals",
    "동물의 부분": "Animal Body Parts",
    "동식물": "Flora and Fauna",
    "동식물 행위": "Animal/Plant Actions",
    "말": "Speech",
    "맛": "Taste",
    "매체": "Media",
    "모양": "Shape",
    "모자, 신발, 장신구": "Hats, Shoes, Accessories",
    "무기": "Weapons",
    "문학": "Literature",
    "문화": "Culture",
    "문화 생활 장소": "Cultural Venues",
    "문화 활동": "Cultural Activities",
    "문화 활동 주체": "Cultural Participants",
    "미술": "Fine Arts",
    "미용 행위": "Beauty Care Actions",
    "밝기": "Brightness",
    "병과 증상": "Diseases and Symptoms",
    "빈도": "Frequency",
    "사람의 종류": "Types of People",
    "사법 및 치안 주체": "Judicial/Public Safety Agents",
    "사법 및 치안 행위": "Judicial/Public Safety Actions",
    "사회 생활": "Social Life",
    "사회 생활 상태": "Social Conditions",
    "사회 행사": "Social Events",
    "사회 활동": "Social Activities",
    "삶": "Life",
    "삶의 상태": "Life Conditions",
    "삶의 행위": "Life Actions",
    "색깔": "Color",
    "생리 현상": "Physiological Phenomena",
    "생활 용품": "Everyday Items",
    "성격": "Personality",
    "성질": "Properties",
    "세는 말": "Counting Words",
    "소리": "Sound",
    "소통 수단": "Means of Communication",
    "속도": "Speed",
    "수": "Number",
    "순서": "Order",
    "시간": "Time",
    "식물류": "Plants",
    "식물의 부분": "Parts of a Plant",
    "식사 및 조리 행위": "Eating and Cooking Actions",
    "식생활": "Eating Habits",
    "식생활 관련 장소": "Food-related Places",
    "식재료": "Ingredients",
    "신앙 대상": "Objects of Worship",
    "신체 내부 구성": "Internal Body Structure",
    "신체 변화": "Bodily Changes",
    "신체 부위": "Body Parts",
    "신체 행위": "Physical Actions",
    "신체에 가하는 행위": "Actions Affecting the Body",
    "약품류": "Medicines",
    "양": "Quantity",
    "언어 행위": "Linguistic Actions",
    "여가 도구": "Leisure Tools",
    "여가 시설": "Leisure Facilities",
    "여가 활동": "Leisure Activities",
    "예술": "Art",
    "온도": "Temperature",
    "옷 종류": "Clothing Types",
    "옷감": "Fabrics",
    "옷의 부분": "Parts of Clothing",
    "용모": "Appearance",
    "위치 및 방향": "Location and Direction",
    "음료": "Drinks",
    "음식": "Food",
    "음악": "Music",
    "의문": "Interrogatives",
    "의복 착용 상태": "Clothing States",
    "의복 착용 행위": "Clothing Actions",
    "의생활": "Clothing Life",
    "의생활 관련 장소": "Clothing-related Places",
    "인간": "Human",
    "인간관계": "Human Relationships",
    "인지 행위": "Cognitive Actions",
    "인칭": "Person (1st/2nd/3rd)",
    "일상 행위": "Daily Activities",
    "자연": "Nature",
    "자원": "Resources",
    "재해": "Disasters",
    "전공과 교과목": "Majors and Subjects",
    "전통 문화": "Traditional Culture",
    "접속": "Conjunctions",
    "정도": "Degree / Intensity",
    "정치 및 치안 상태": "Political/Security Conditions",
    "정치 및 행정 주체": "Political/Administrative Agents",
    "정치 및 행정 행위": "Political/Administrative Actions",
    "정치와 행정": "Politics and Administration",
    "조리 도구": "Cooking Tools",
    "종교": "Religion",
    "종교 유형": "Types of Religion",
    "종교 행위": "Religious Actions",
    "종교 활동 도구": "Religious Tools",
    "종교 활동 장소": "Religious Places",
    "종교어": "Religious Terms",
    "종교인": "Religious People",
    "주거 상태": "Housing Conditions",
    "주거 지역": "Residential Areas",
    "주거 행위": "Housing Actions",
    "주거 형태": "Housing Types",
    "주생활": "Residential Life",
    "주택 구성": "Housing Components",
    "지시": "Demonstratives",
    "지역": "Regions",
    "지표면 사물": "Surface Features",
    "지형": "Terrain",
    "직업": "Occupation",
    "직위": "Job Title",
    "직장": "Workplace",
    "직장 생활": "Work Life",
    "채소": "Vegetables",
    "천체": "Celestial Bodies",
    "체력 상태": "Physical Condition",
    "치료 시설": "Medical Facilities",
    "치료 행위": "Medical Actions",
    "친족 관계": "Kinship",
    "태도": "Attitude",
    "통신 행위": "Communication Actions",
    "학교 시설": "School Facilities",
    "학문 용어": "Academic Terms",
    "학문 행위": "Academic Actions",
    "학습 관련 사물": "Learning Objects"
}

subject_category_map = {
    "기분 표현하기": "Expressing Moods",
    "사고": "Accidents",
    "재해 기술하기": "Describing Disasters",
    "가족 행사": "Family Events",
    "가족 행사-명절": "Family Events – Holidays",
    "감사하기": "Expressing Gratitude",
    "감정": "Emotions",
    "개인 정보 교환하기": "Exchanging Personal Information",
    "건강": "Health",
    "건축": "Architecture",
    "경제·경영": "Economy and Business",
    "공공 기관 이용하기(도서관)": "Using Public Institutions (Library)",
    "공공 기관 이용하기(우체국)": "Using Public Institutions (Post Office)",
    "공공 기관 이용하기(출입국 관리 사무소)": "Using Public Institutions (Immigration Office)",
    "공공기관 이용하기": "Using Public Institutions",
    "공연과 감상": "Performances and Appreciation",
    "과학과 기술": "Science and Technology",
    "교육": "Education",
    "교통 이용하기": "Using Transportation",
    "기후": "Climate",
    "길찾기": "Finding Directions",
    "날씨와 계절": "Weather and Seasons",
    "날짜 표현하기": "Expressing Dates",
    "대중 매체": "Mass Media",
    "대중 문화": "Popular Culture",
    "문제 해결하기(분실 및 고장)": "Problem Solving (Loss and Breakdowns)",
    "문화 비교하기": "Comparing Cultures",
    "문화 차이": "Cultural Differences",
    "물건 사기": "Shopping for Goods",
    "법": "Law",
    "병원 이용하기": "Using a Hospital",
    "보건과 의료": "Health and Medical Care",
    "복장 표현하기": "Describing Clothing",
    "사건": "Incidents",
    "사과하기": "Apologizing",
    "사회 문제": "Social Issues",
    "사회 제도": "Social Systems",
    "성격 표현하기": "Describing Personality",
    "소개하기(가족 소개)": "Introducing Family",
    "소개하기(자기소개)": "Self-Introduction",
    "스포츠": "Sports",
    "시간 표현하기": "Expressing Time",
    "식문화": "Food Culture",
    "실수담 말하기": "Talking About Mistakes",
    "심리": "Psychology",
    "약국 이용하기": "Using a Pharmacy",
    "약속하기": "Making Appointments",
    "언론": "News Media",
    "언어": "Language",
    "여가 생활": "Leisure Life",
    "여행": "Travel",
    "역사": "History",
    "연애와 결혼": "Dating and Marriage",
    "영화 보기": "Watching Movies",
    "예술": "Art",
    "외모 표현하기": "Describing Appearance",
    "외양": "Outward Appearance",
    "요리 설명하기": "Describing Cooking",
    "요일 표현하기": "Expressing Days of the Week",
    "위치 표현하기": "Expressing Location",
    "음식 설명하기": "Describing Food",
    "음식 주문하기": "Ordering Food",
    "인간관계": "Human Relationships",
    "인사하기": "Greeting",
    "전화하기": "Making a Phone Call",
    "정치": "Politics",
    "종교": "Religion",
    "주거 생활": "Residential Life",
    "주말 및 휴가": "Weekend and Vacation",
    "지리 정보": "Geographic Information",
    "직업과 진로": "Occupations and Career Paths",
    "직장 생활": "Work Life",
    "집 구하기": "Finding Housing",
    "집안일": "Housework",
    "철학·윤리": "Philosophy and Ethics",
    "초대와 방문": "Inviting and Visiting",
    "취미": "Hobbies",
    "컴퓨터와 인터넷": "Computers and the Internet",
    "하루 생활": "Daily Life",
    "학교생활": "School Life",
    "한국 생활": "Life in Korea",
    "한국의 문학": "Korean Literature",
    "환경 문제": "Environmental Issues"
}


# Insertion functions (with optional ID specification)
def insert_subject_category(
        cursor, name: str, lexical_entry_id: int):
    cursor.execute("""
        INSERT INTO subject_categories (name, lexical_entry_id)
        VALUES (?, ?)
    """, (subject_category_map[name.strip()], lexical_entry_id))

def insert_equivalent(
        cursor, language, lemma, definition, lexical_id: int = None,
        sense_id: Optional[int] = None, id: Optional[int] = None):
    #print(f"Inserting equivalent: {(id, sense_id, language, lemma, definition)=}")
    cursor.execute("""
        INSERT INTO equivalents (id, lexical_entry_id, sense_id, language, lemma, definition)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id, lexical_id, sense_id, language_map[language], lemma, definition))

def insert_lexical_entry(
        cursor,
    part_of_speech: str, written_form: str, homonym_number: int,
    lexical_unit: str,
    vocabulary_level: Optional[str] = None, 
    id: Optional[int] = None
):
    #print(f"Inserting {(id, part_of_speech, written_form, homonym_number, lexical_unit, vocabulary_level)=}")
    if part_of_speech == "":
        cursor.execute("""
                       insert into phrase_proverbs (id, written_form, lexical_unit)
                       values (?, ?, ?)
                       """, (id, written_form, lexical_unit_map[lexical_unit]))
    else:
        cursor.execute("""
            INSERT INTO lexical_entries (id, part_of_speech, written_form,
                                        homonym_number, lexical_unit, vocabulary_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, pos_map[part_of_speech], written_form, homonym_number, lexical_unit_map[lexical_unit], vocab_level_map[vocabulary_level]))

def insert_word_form(
        cursor,
    lexical_entry_id: int, type_of_form: str, written_form: Optional[str] = None,
    pronunciation: Optional[str] = None, sound: Optional[str] = None,
    id: Optional[int] = None
):
    #print(f"Inserting {(id, lexical_entry_id, pronunciation, sound, type_of_form, written_form)=}")
    if isinstance(pronunciation, list):
        for i, pron in enumerate(pronunciation):
            if sound is not None:
                pron_sound = sound[i] if isinstance(sound, list) else sound
            else:
                pron_sound = None
            cursor.execute("""
                INSERT INTO word_forms (id, lexical_entry_id, pronunciation, sound, type_of_form, written_form)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id + i if id else None, lexical_entry_id, pron, pron_sound, type_map[type_of_form], written_form))
    else:
        cursor.execute("""
            INSERT INTO word_forms (id, lexical_entry_id, pronunciation, sound, type_of_form, written_form)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, lexical_entry_id, pronunciation, sound, type_map[type_of_form], written_form))

def insert_form_representation(
        cursor,
    word_form_id: int, type_of_form: str, written_form: str,
    pronunciation: Optional[str] = None, sound: Optional[str] = None,
    id: Optional[int] = None
):
    #print(f"Inserting {(id, word_form_id, pronunciation, sound, type_of_form, written_form)=}")
    if isinstance(pronunciation, list):
        for i, pron in enumerate(pronunciation):
            if sound is not None:
                pron_sound = sound[i] if isinstance(sound, list) else sound
            else:
                pron_sound = None
            cursor.execute("""
                INSERT INTO form_representations (id, word_form_id, pronunciation, sound, type_of_form, written_form)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id + i if id else None, word_form_id, pron, pron_sound, type_map[type_of_form], written_form))
    else:
        cursor.execute("""
            INSERT INTO form_representations (id, word_form_id, pronunciation, sound, type_of_form, written_form)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, word_form_id, pronunciation, sound, type_map[type_of_form], written_form))

def insert_sense(
        cursor,
    lexical_entry_id: int, definition: str,
    annotation: Optional[str] = None,
    syntactic_annotation: Optional[str] = None, id: Optional[int] = None
):
    cursor.execute("""
        INSERT INTO senses (id, lexical_entry_id, definition, annotation, syntactic_annotation)
        VALUES (?, ?, ?, ?, ?)
    """, (id, lexical_entry_id, definition, annotation, syntactic_annotation))

def insert_sense_example(
        cursor,
    sense_id: int, example: str, type_of_example: str, id: Optional[int] = None
):
    if isinstance(example, list):
        # lists seem to be dialogues
        example = "\n".join([f'"{_}"' for _ in example])
    # For consistency
    if type_of_example == "대화" and not example.startswith('"'):
        example = f'"{example}"'
    cursor.execute("""
        INSERT INTO sense_examples (id, sense_id, example, type_of_example)
        VALUES (?, ?, ?, ?)
    """, (id, sense_id, example, type_map[type_of_example]))

def insert_sense_relation(
        cursor,
    sense_id: int, lexical_entry_id: int, type_of_relation: str,
    lemma: str, homonym_number: int, id: Optional[int] = None
):
    cursor.execute("""
        INSERT INTO sense_relations (id, sense_id, lexical_entry_id, type_of_relation, lemma, homonym_number)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id, sense_id, lexical_entry_id, type_map[type_of_relation], lemma, homonym_number))

def insert_syntactic_pattern(
        cursor,
    sense_id: int, pattern: str, id: Optional[int] = None
):
    cursor.execute("""
        INSERT INTO syntactic_patterns (id, sense_id, pattern)
        VALUES (?, ?, ?)
    """, (id, sense_id, pattern))

def insert_semantic_category(cursor, lexical_entry_id: int, semantic_category: str, id: Optional[int] = None):
    if ">" not in semantic_category:
        raise ValueError(f"Invalid semantic category format: {semantic_category}")
    base, detail = [_.strip() for _ in semantic_category.split(">", 1)]
    cursor.execute("""
        INSERT INTO semantic_categories (id, lexical_entry_id, base, detail)
        VALUES (?, ?, ?, ?)
    """, (id, lexical_entry_id, semantic_category_map[base], semantic_category_map[detail]))

def insert_multimedia(cursor, sense_id: int, type: str, label: str, url: str, id: Optional[int] = None):
    cursor.execute("""
        INSERT INTO multimedia (id, sense_id, type_of_media, label, url)
        VALUES (?, ?, ?, ?, ?)
    """, (id, sense_id, type_map[type], label, url))

def insert_variant(cursor, lexical_entry_id: int, variant: str):
    cursor.execute("""
        INSERT INTO variants (lexical_entry_id, variant)
        VALUES (?, ?)
    """, (lexical_entry_id, variant))

conn = sqlite3.connect("lexicon.db")
init_db(conn)


def add_semantic_categories(cursor, semantic_categories, id):
    if isinstance(semantic_categories, str):
        semantic_categories = [semantic_categories]
    for category in semantic_categories:
        insert_semantic_category(cursor, id, category)


def add_word_forms(cursor, word_forms, id):
    if isinstance(word_forms, dict):
        word_forms = [word_forms]
    for form in word_forms:
        insert_word_form(
            cursor,
            lexical_entry_id=id,
            type_of_form=form.get("type", ""),
            written_form=form.get("writtenForm", None),
            pronunciation=form.get("pronunciation", None),
            sound=form.get("sound", None)
        )
        if "FormRepresentation" in form:
            representation = form["FormRepresentation"]
            insert_form_representation(
                cursor,
                word_form_id=id,
                type_of_form=representation.get("type", ""),
                written_form=representation.get("writtenForm", ""),
                pronunciation=representation.get("pronunciation", None),
                sound=representation.get("sound", None)
            )

def add_senses(cursor, senses, lexical_entry_id):
    if isinstance(senses, dict):
        senses = [senses]
    for sense in senses:
        insert_sense(
            cursor,
            lexical_entry_id=lexical_entry_id,
            definition=sense.get("definition", ""),
            annotation=sense.get("annotation", None),
            syntactic_annotation=sense.get("syntacticAnnotation", None)
        )
        sense_id = cursor.lastrowid
        if "SenseExample" in sense:
            examples = sense["SenseExample"]
            if isinstance(examples, dict):
                examples = [examples]
            for example in examples:
                text = example.get("example", "")
                # for some reason there are some example dialogues that are just "."
                if text == '.':
                    continue
                insert_sense_example(
                    cursor,
                    sense_id=sense_id,
                    example=text,
                    type_of_example=example.get("type", "")
                )
        if "SenseRelation" in sense:
            relations = sense["SenseRelation"]
            if isinstance(relations, dict):
                relations = [relations]
            for relation in relations:
                insert_sense_relation(
                    cursor,
                    sense_id=sense_id,
                    lexical_entry_id=relation.get("id", 0),
                    type_of_relation=relation.get("type", ""),
                    lemma=relation.get("lemma", ""),
                    homonym_number=relation.get("homonymNumber", 0)
                )
        if "syntacticPattern" in sense:
            patterns = sense["syntacticPattern"]
            if isinstance(patterns, str):
                patterns = [patterns]
            for pattern in patterns:
                insert_syntactic_pattern(
                    cursor,
                    sense_id=sense_id,
                    pattern=pattern
                )
        if "Equivalent" in sense:
            equivalents = sense["Equivalent"]
            if isinstance(equivalents, dict):
                equivalents = [equivalents]
            for equivalent in equivalents:
                insert_equivalent(
                    cursor,
                    sense_id=sense_id,
                    language=equivalent.get("language", ""),
                    lemma=equivalent.get("lemma", ""),
                    definition=equivalent.get("definition", ""),
                    lexical_id=lexical_entry_id
                )
        
        if "Multimedia" in sense:
            multimedia = sense["Multimedia"]
            if isinstance(multimedia, dict):
                multimedia = [multimedia]
            for item in multimedia:
                insert_multimedia(
                    cursor,
                    sense_id=sense_id,
                    type=item.get("type"),
                    label=item.get("label"),
                    url=item.get("url")
                )


def add_to_db(data):
    entries = data.get("LexicalResource", {}).get("Lexicon", {}).get("LexicalEntry", [])
    for entry in entries:
        cursor = conn.cursor()
        id = entry.get("id")
        lemma = entry["Lemma"]
        written_form=lemma.get("writtenForm", "")
        insert_lexical_entry(
            cursor,
            part_of_speech=entry.get("partOfSpeech", ""),
            written_form=written_form,
            homonym_number=entry.get("homonym_number", 0),
            lexical_unit=entry.get("lexicalUnit", ""),
            vocabulary_level=entry.get("vocabularyLevel", ""),
            id=id
        )
        
        subject_category=entry.get("subjectCategiory")
        if subject_category:
            if isinstance(subject_category, str):
                categories = subject_category.split(",")
                for category in categories:
                    insert_subject_category(cursor, category, id)

        variants = [written_form] + [_ for _ in lemma.get("variant", "").split(",") if _ != '']
        for variant in variants:
            insert_variant(cursor, id, variant)

        if "semanticCategory" in entry:
            add_semantic_categories(cursor, entry.get("semanticCategory"), id)
        add_word_forms(cursor, entry.get("WordForm", []), id)
        add_senses(cursor, entry.get("Sense", []), id)

    conn.commit()


for json_file in Path('simplified').glob("*.json"):
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)
    print(f"Processing {json_file.name}...")
    add_to_db(data)