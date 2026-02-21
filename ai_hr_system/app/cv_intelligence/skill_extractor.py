import spacy
import re
from typing import List, Set, Dict

class SkillExtractor:
    def __init__(self, model: str = "en_core_web_sm"):
        # Auto-download model if missing
        if not spacy.util.is_package(model):
            print(f"Downloading Spacy model '{model}'...")
            spacy.cli.download(model)
        
        print(f"Loading Spacy model '{model}'...")
        self.nlp = spacy.load(model)

        # Extended explicit skills list (Common Tech Stack) - Multilingual
        self.common_skills = {
            # Languages
            "python", "пайтон", "питон", "piton", "payton",
            "javascript", "джаваскрипт", "js", "typescript", "тайпскрипт", "ts",
            "java", "джава", "c++", "c#", "go", "golang", "rust", "раст", "php", "ruby", "swift", "kotlin",
            # Frontend
            "react", "реактор", "реакт", "vue", "angular", "ангуляр", "svelte", "next.js", "nuxt.js", "html", "css", "sass", "less", "tailwind",
            # Backend
            "node.js", "express", "nest.js", "django", "джанго", "flask", "фласк", "fastapi", "фастапи", "spring boot", "laravel", "rails", ".net",
            # Data / AI
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
            "machine learning", "ml", "deep learning", "dl", "nlp", "computer vision", "tensorflow", "pytorch",
            "scikit-learn", "pandas", "numpy", "opencv", "llm", "transformers", "hugging face",
            # DevOps / Cloud
            "docker", "докер", "kubernetes", "k8s", "aws", "azure", "gcp", "terraform", "ansible", "jenkins", "gitlab ci", "circleci",
            "git", "linux", "bash", "powershell",
            # Architecture / Concepts
            "rest api", "graphql", "grpc", "microservices", "event-driven architecture", "tdd", "bdd",
            "agile", "scrum", "kanban", "jira", "confluence"
        }

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts explicit skills and candidate noun chunks for semantic analysis.
        """
        if not text:
            return {"explicit": [], "candidates": []}

        # Normalize text for better extraction
        text_clean = text.lower()
        doc = self.nlp(text_clean)
        
        explicit_skills = self._find_explicit_skills(text_clean)
        
        candidates = []
        for chunk in doc.noun_chunks:
            clean_chunk = chunk.text.strip()
            word_count = len(clean_chunk.split())
            
            if 1 <= word_count <= 5 and clean_chunk not in explicit_skills:
                candidates.append(clean_chunk)

        # Return skills, ensuring they are always in their canonical form
        return {
            "explicit": sorted(list(explicit_skills)),
            "candidates": list(set(candidates))
        }

    def _find_explicit_skills(self, text: str) -> Set[str]:
        found = set()
        text_lower = text.lower()
        
        # Mapping for normalization - Standard Tech Names (Canonical English)
        # Using explicit strings to avoid any encoding mixup
        normalization_map = {
            "пайтон": "python", "питон": "python", "piton": "python", "payton": "python",
            "джаваскрипт": "javascript", "js": "javascript",
            "тайпскрипт": "typescript", "ts": "typescript",
            "джава": "java", "ячми": "java", # accidental RU layout for 'java'
            "раст": "rust",
            "реактор": "react", "реакт": "react",
            "ангуляр": "angular",
            "джанго": "django", "джанго": "django",
            "фласк": "flask",
            "фастапи": "fastapi",
            "докер": "docker", "контейнеризация": "docker",
            "k8s": "kubernetes", "кубернетес": "kubernetes",
            "ml": "machine learning", "дл": "deep learning", "dl": "deep learning",
            "с++": "c++", "с#": "c#", # Cyrillic 'c'
            "гит": "git", "гитхаб": "git"
        }
        
        for skill in self.common_skills:
            pattern = None
            if any(c in skill for c in "+#."):
                pattern = re.escape(skill)
            else:
                pattern = r'\b' + re.escape(skill) + r'\b'
            
            if re.search(pattern, text_lower):
                # Standardize to canonical name if it exists in map, else use skill itself
                # CRITICAL: We look up the 'skill' as defined in self.common_skills
                canonical = normalization_map.get(skill.lower(), skill)
                found.add(canonical)
                
        return found
