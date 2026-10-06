"""
db.py — Database layer for Madras Foodies Consultancy
------------------------------------------------------
Primary   : MongoDB Atlas (madras_foodies)
Fallback  : SQLite (data/madras_foodies.db)

Collections : clients | restaurants | contacts | reviews | projects
"""

import os
import json
import sqlite3
from datetime import datetime, timezone

import certifi
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# ---------------------------------------------------------------------------
# Default project seed data
# ---------------------------------------------------------------------------

DEFAULT_PROJECTS = [
    {"order": 1, "name": "Noodle House",            "location": "Mayajaal Cinemas, ECR, Uthandi", "category": "India",         "description": "Hospitality concept and kitchen setup for a high-footfall cinema dining outlet.", "image": "images/projects/noodle_house.jpg"},
    {"order": 2, "name": "The Padington Club",       "location": "Nandanam",                        "category": "India",         "description": "Comprehensive hospitality planning, beverage setup, and operational guidance.", "image": "images/projects/padington_club.jpg"},
    {"order": 3, "name": "Episode 23 Bistro",        "location": "Anna Nagar",                      "category": "India",         "description": "Complete bistro concept design, menu engineering, and pre-opening advisory.", "image": "images/projects/episode_23_bistro.jpg"},
    {"order": 4, "name": "Fika Café",                "location": "Adyar (Pre-Opening)",             "category": "India",         "description": "Pre-opening café planning, interior guidance, and staff training.", "image": "images/projects/fika_cafe.jpg"},
    {"order": 5, "name": "Sola Resto Bar",           "location": "Pondicherry",                     "category": "India",         "description": "Restaurant and bar layout, menu development, and operational consulting.", "image": "images/projects/sola_resto_bar.jpg"},
    {"order": 6, "name": "Mantra Restaurant",        "location": "Kuala Lumpur, Malaysia",          "category": "International", "description": "International hospitality project covering kitchen workflow and recipe standardization.", "image": "images/projects/mantra_restaurant.jpg"},
    {"order": 7, "name": "Sam's Kitchen Catering",   "location": "Ipoh, Malaysia",                  "category": "International", "description": "High-volume catering setup, food logistics, and standard operating procedures.", "image": "images/projects/sams_kitchen.jpg"},
    {"order": 8, "name": "Radha's Restaurant",       "location": "Kuala Lumpur, Malaysia",          "category": "International", "description": "Multi-cuisine dining establishment setup and staff operational reviews.", "image": "images/projects/radhas_restaurant.jpg"},
]


# ---------------------------------------------------------------------------
# SQLite fallback — mirrors PyMongo's collection interface
# ---------------------------------------------------------------------------

class _SQLiteCursor:
    """Minimal cursor returned by SQLite collection queries."""

    def __init__(self, items):
        self._items = list(items)

    def sort(self, key, direction=1):
        reverse = direction == -1
        self._items.sort(
            key=lambda x: (x.get(key) is None, x.get(key)), reverse=reverse
        )
        return self

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class _SQLiteCollection:
    """PyMongo-compatible collection backed by an SQLite JSON table."""

    def __init__(self, db_path: str, table: str):
        self._db_path = db_path
        self._table = table

    # -- internal helpers --------------------------------------------------

    def _conn(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    # -- public API (matches PyMongo) --------------------------------------

    def insert_one(self, doc: dict):
        doc = dict(doc)
        now = self._now()
        doc.setdefault("created_at", now)
        doc.setdefault("updated_at", now)
        conn = self._conn()
        try:
            with conn:
                conn.execute(
                    f"INSERT INTO {self._table} (data, created_at, updated_at) VALUES (?, ?, ?)",
                    (json.dumps(doc), doc["created_at"], doc["updated_at"]),
                )
        finally:
            conn.close()

    def insert_many(self, docs):
        for doc in docs:
            self.insert_one(doc)

    def find(self, query=None, projection=None):
        conn = self._conn()
        try:
            rows = conn.execute(f"SELECT data FROM {self._table}").fetchall()
        finally:
            conn.close()
        results = [json.loads(r["data"]) for r in rows]
        if query:
            results = [d for d in results if all(d.get(k) == v for k, v in query.items())]
        if projection:
            exclude = {k for k, v in projection.items() if not v}
            results = [{k: v for k, v in d.items() if k not in exclude} for d in results]
        return _SQLiteCursor(results)

    def find_one(self, query=None):
        items = list(self.find(query))
        return items[0] if items else None

    def count_documents(self, query=None):
        return len(list(self.find(query or {})))

    def delete_many(self, query):
        if not query:
            conn = self._conn()
            try:
                with conn:
                    conn.execute(f"DELETE FROM {self._table}")
            finally:
                conn.close()


class _SQLiteProjectsCollection:
    """Dedicated SQLite collection for the projects table (structured columns)."""

    def __init__(self, db_path: str):
        self._db_path = db_path

    def _conn(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def insert_one(self, doc: dict):
        conn = self._conn()
        try:
            with conn:
                conn.execute(
                    'INSERT INTO projects ("order", name, location, category, description, image) VALUES (?,?,?,?,?,?)',
                    (doc.get("order"), doc["name"], doc.get("location", ""), doc.get("category", ""), doc.get("description", ""), doc.get("image", "")),
                )
        finally:
            conn.close()

    def insert_many(self, docs):
        for doc in docs:
            self.insert_one(doc)

    def find(self, query=None, projection=None):
        conn = self._conn()
        try:
            rows = conn.execute('SELECT id, "order", name, location, category, description, image FROM projects').fetchall()
        finally:
            conn.close()
        results = []
        for r in rows:
            d = dict(r)
            d["_id"] = str(d["id"])
            results.append(d)
        if query:
            results = [d for d in results if all(str(d.get(k)) == str(v) or d.get(k) == v for k, v in query.items())]
        if projection:
            exclude = {k for k, v in projection.items() if not v}
            results = [{k: v for k, v in d.items() if k not in exclude} for d in results]
        return _SQLiteCursor(results)

    def find_one(self, query=None):
        items = list(self.find(query))
        return items[0] if items else None

    def update_one(self, query: dict, update: dict):
        set_data = update.get("$set", update)
        conn = self._conn()
        try:
            with conn:
                target_id = query.get("_id") or query.get("id") or query.get("order")
                if "_id" in query or "id" in query:
                    val = int(query.get("_id") or query.get("id"))
                    clause = "id = ?"
                elif "order" in query:
                    val = int(query["order"])
                    clause = '"order" = ?'
                else:
                    return
                fields = []
                values = []
                for k, v in set_data.items():
                    if k not in ("_id", "id"):
                        col_name = f'"{k}"' if k == "order" else k
                        fields.append(f"{col_name} = ?")
                        values.append(v)
                values.append(val)
                if fields:
                    conn.execute(f"UPDATE projects SET {', '.join(fields)} WHERE {clause}", values)
        finally:
            conn.close()

    def delete_one(self, query: dict):
        conn = self._conn()
        try:
            with conn:
                if "_id" in query or "id" in query:
                    val = int(query.get("_id") or query.get("id"))
                    conn.execute("DELETE FROM projects WHERE id = ?", (val,))
                elif "order" in query:
                    val = int(query["order"])
                    conn.execute('DELETE FROM projects WHERE "order" = ?', (val,))
        finally:
            conn.close()

    def count_documents(self, query=None):
        return len(list(self.find(query or {})))

    def delete_many(self, query):
        if not query:
            conn = self._conn()
            try:
                with conn:
                    conn.execute("DELETE FROM projects")
            finally:
                conn.close()


class _LocalSQLiteDatabase:
    """Top-level database object wrapping all SQLite collections."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_schema()
        self._seed_projects()

        self.clients     = _SQLiteCollection(db_path, "clients")
        self.restaurants = _SQLiteCollection(db_path, "restaurants")
        self.contacts    = _SQLiteCollection(db_path, "contacts")
        self.reviews     = _SQLiteCollection(db_path, "reviews")
        self.projects    = _SQLiteProjectsCollection(db_path)

    def _init_schema(self):
        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id          INTEGER PRIMARY KEY AUTOINCREMENT,
                        "order"     INTEGER,
                        name        TEXT NOT NULL,
                        location    TEXT,
                        category    TEXT,
                        description TEXT,
                        image       TEXT
                    )
                """)
                # Ensure image column exists if table pre-existed
                cols = [c[1] for c in conn.execute("PRAGMA table_info(projects)").fetchall()]
                if "image" not in cols:
                    conn.execute("ALTER TABLE projects ADD COLUMN image TEXT")

                for table in ("clients", "restaurants", "contacts", "reviews"):
                    conn.execute(f"""
                        CREATE TABLE IF NOT EXISTS {table} (
                            id         INTEGER PRIMARY KEY AUTOINCREMENT,
                            data       TEXT NOT NULL,
                            created_at TEXT,
                            updated_at TEXT
                        )
                    """)
        finally:
            conn.close()

    def _seed_projects(self):
        conn = sqlite3.connect(self._db_path)
        try:
            count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
            if count == 0:
                for p in DEFAULT_PROJECTS:
                    conn.execute(
                        'INSERT INTO projects ("order", name, location, category, description, image) VALUES (?,?,?,?,?,?)',
                        (p["order"], p["name"], p["location"], p["category"], p["description"], p.get("image", "")),
                    )
                conn.commit()
            else:
                # Update images for existing seeds if missing
                for p in DEFAULT_PROJECTS:
                    conn.execute(
                        'UPDATE projects SET image = ? WHERE "order" = ? AND (image IS NULL OR image = "")',
                        (p.get("image", ""), p["order"]),
                    )
                conn.commit()
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# Public factory — returns (db, engine_name)
# ---------------------------------------------------------------------------

def get_database(mongo_uri: str = None, db_name: str = None, fallback_dir: str = None):
    """
    Returns a (db, engine) tuple.

    Tries MongoDB Atlas first.  On any connection or auth failure, silently
    falls back to a local SQLite database so the app never goes offline.

    Returns:
        db      — PyMongo Database object OR _LocalSQLiteDatabase instance
        engine  — "mongodb" | "sqlite"
    """
    mongo_uri   = mongo_uri   or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name     = db_name     or os.getenv("MONGO_DB",  "madras_foodies")
    if not fallback_dir:
        if os.getenv("VERCEL"):
            fallback_dir = os.path.join("/tmp", "data")
        else:
            fallback_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
            )

    # -- Attempt MongoDB Atlas connection --
    try:
        kwargs = {
            "serverSelectionTimeoutMS": 8000,
            "connectTimeoutMS":         8000,
            "socketTimeoutMS":          10000,
            "maxPoolSize":              50,
            "minPoolSize":              5,
        }
        if "mongodb+srv://" in mongo_uri or "ssl=true" in mongo_uri.lower():
            kwargs["tlsCAFile"] = certifi.where()

        client = MongoClient(mongo_uri, **kwargs)
        client.admin.command("ping")          # raises if unreachable / wrong creds
        db = client[db_name]

        # Seed projects if the collection is empty
        if db.projects.count_documents({}) == 0:
            db.projects.insert_many(DEFAULT_PROJECTS)
        else:
            for p in DEFAULT_PROJECTS:
                db.projects.update_one(
                    {"order": p["order"], "$or": [{"image": {"$exists": False}}, {"image": None}, {"image": ""}]},
                    {"$set": {"image": p.get("image", "")}}
                )

        return db, "mongodb"

    except (PyMongoError, Exception):
        # -- Fall back to SQLite --
        sqlite_file = os.path.join(fallback_dir, f"{db_name}.db")
        return _LocalSQLiteDatabase(sqlite_file), "sqlite"
