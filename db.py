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
                         
    CREATE TABLE IF NOT EXISTS lexical_entries (
        id INTEGER PRIMARY KEY NOT NULL,
        part_of_speech TEXT NOT NULL,
        written_form TEXT NOT NULL,
        homonym_number INTEGER NOT NULL,
        lexical_unit TEXT NOT NULL,
        vocabulary_level TEXT
    );

    create table if not exists phrase_proverbs (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER,
        written_form TEXT NOT NULL,
        lexical_unit TEXT NOT NULL
    );
                         
    create table if not exists equivalents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        type TEXT NOT NULL,
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

# Insertion functions (with optional ID specification)
def insert_equivalent(
        cursor, language, lemma, definition,
        sense_id: Optional[int] = None, id: Optional[int] = None):
    #print(f"Inserting equivalent: {(id, sense_id, language, lemma, definition)=}")
    cursor.execute("""
        INSERT INTO equivalents (id, sense_id, language, lemma, definition)
        VALUES (?, ?, ?, ?, ?)
    """, (id, sense_id, language, lemma, definition))

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
                       """, (id, written_form, lexical_unit))
    else:
        cursor.execute("""
            INSERT INTO lexical_entries (id, part_of_speech, written_form,
                                        homonym_number, lexical_unit, vocabulary_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, part_of_speech, written_form, homonym_number, lexical_unit, vocabulary_level))

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
            """, (id + i if id else None, lexical_entry_id, pron, pron_sound, type_of_form, written_form))
    else:
        cursor.execute("""
            INSERT INTO word_forms (id, lexical_entry_id, pronunciation, sound, type_of_form, written_form)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, lexical_entry_id, pronunciation, sound, type_of_form, written_form))

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
            """, (id + i if id else None, word_form_id, pron, pron_sound, type_of_form, written_form))
    else:
        cursor.execute("""
            INSERT INTO form_representations (id, word_form_id, pronunciation, sound, type_of_form, written_form)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, word_form_id, pronunciation, sound, type_of_form, written_form))

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
    """, (id, sense_id, example, type_of_example))

def insert_sense_relation(
        cursor,
    sense_id: int, lexical_entry_id: int, type_of_relation: str,
    lemma: str, homonym_number: int, id: Optional[int] = None
):
    cursor.execute("""
        INSERT INTO sense_relations (id, sense_id, lexical_entry_id, type_of_relation, lemma, homonym_number)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id, sense_id, lexical_entry_id, type_of_relation, lemma, homonym_number))

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
    """, (id, lexical_entry_id, base, detail))

def insert_multimedia(cursor, sense_id: int, type: str, label: str, url: str, id: Optional[int] = None):
    cursor.execute("""
        INSERT INTO multimedia (id, sense_id, type, label, url)
        VALUES (?, ?, ?, ?, ?)
    """, (id, sense_id, type, label, url))

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
                    definition=equivalent.get("definition", "")
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