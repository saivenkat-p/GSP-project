from typing import List, Dict, Any, Optional, Tuple
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Semantic Intent Exemplars for Vector-Space Classification
INTENT_EXEMPLAR_DATA = {
    "GREETING": [
        "hi", "hello", "hey", "hello andi", "hi andi", "say hi to me", "say hello", "say hi", "good morning",
        "good afternoon", "good evening", "greetings", "namaste", "namaskaram", "vanakkam", "pranam",
        "hi bot", "hello assistant", "heya", "hi there", "greet me", "hello there"
    ],
    "HOW_ARE_YOU": [
        "how are you", "how are you doing", "how r u", "how is it going", "ela unnaru", "ela unnav",
        "how are things", "are you doing well", "how do you do"
    ],
    "CONVERSATIONAL_READY": [
        "sir naaku oka doubt undi", "oka doubt undi", "i have a doubt", "can you help me", "help me please",
        "help kavali", "naaku help kavali", "i need some help", "tell me what you can do", "i want to ask something",
        "anna help me", "doubt sir", "doubt anna", "can i ask a question", "help me", "can you help", "i need assistance"
    ],
    "COURTESY": [
        "thanks", "thank you", "thank you so much", "dhanyavadalu", "chala thanks", "okay", "ok",
        "got it", "sure", "bye", "goodbye", "see you", "perfect thanks", "great thanks", "thank u"
    ],
    "GEN_AI_EXPLANATION": [
        "what is ai", "what is artificial intelligence", "explain ai", "about ai", "what is machine learning",
        "what is ml", "how does ai work", "explain artificial intelligence simply", "what are neural networks"
    ],
    "GEN_INFLATION_EXPLANATION": [
        "what is inflation", "explain inflation", "inflation simply", "why prices rise in economy", "what causes inflation"
    ],
    "GEN_BFS_DFS_EXPLANATION": [
        "what is bfs and dfs", "difference between bfs and dfs", "bfs vs dfs", "explain graph traversal algorithms"
    ],
    "GEN_RESUME_GUIDANCE": [
        "how to write a resume", "resume tips", "resume format", "how do i write a resume", "cv format", "best resume structure"
    ],
    "CAREER_GOVT_JOBS": [
        "degree ayyaka govt jobs em vastai", "govt jobs after graduation", "jobs for degree holders", "government jobs after degree",
        "what govt jobs after degree", "govt exams after btech", "appsc upsc bank jobs after degree", "jobs after degree"
    ],
    "LATEST_UPDATE": [
        "what are new updates", "what are new scheme updates", "new updates", "latest updates", "recent government schemes",
        "new government schemes", "what are new schemes", "schemes recently launched", "recent updates", "latest citizen notices",
        "rule changes", "recent welfare updates", "tell me new updates", "show new updates", "updates today", "what is new in government"
    ],
    "BROAD_GOVT_HELP": [
        "naaku govt nundi emaina help undha", "any help from government", "govt help kavali", "government help kavali",
        "i need government help", "help from government", "what benefits can i get from government", "welfare programs for citizens",
        "financial help from govt", "i want government help"
    ],
    "BROAD_SCHOLARSHIP_DISCOVERY": [
        "all scholarships", "scholarship list", "scholership kavali", "scholarship kavali", "what scholarships are available",
        "student scholarships in ap", "scholarship details", "scholarships for students"
    ],
    "BROAD_SCHEME_DISCOVERY": [
        "all schemes", "welfare schemes", "government schemes list", "show all government schemes", "what schemes are available",
        "government schemes in andhra pradesh"
    ],
    "SERVICE_COUNT": [
        "how many services you have", "how many services", "total services", "count of services", "how many categories"
    ],
    "SCHEME_COUNT": [
        "how many schemes you have", "how many schemes", "total schemes", "count of welfare schemes", "number of schemes"
    ],
    "SERVICE_LIST": [
        "what services do you provide", "list services", "available services", "show services", "what services you have",
        "list of all services"
    ]
}

class SemanticEngine:
    def __init__(self):
        self.intent_labels: List[str] = []
        self.intent_corpus: List[str] = []
        for label, phrases in INTENT_EXEMPLAR_DATA.items():
            for p in phrases:
                self.intent_labels.append(label)
                self.intent_corpus.append(p.lower().strip())
        
        self.intent_vectorizer = TfidfVectorizer(ngram_range=(1, 3), analyzer="char_wb", sublinear_tf=True)
        self.intent_matrix = self.intent_vectorizer.fit_transform(self.intent_corpus)

    def classify_intent_semantic(self, query: str) -> Tuple[str, float]:
        """
        Computes cosine similarity between input query and all intent exemplars in vector space.
        Returns top matched intent label and similarity confidence.
        """
        q_clean = query.lower().strip()
        q_vec = self.intent_vectorizer.transform([q_clean])
        similarities = cosine_similarity(q_vec, self.intent_matrix)[0]
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])
        return self.intent_labels[best_idx], best_score

    def build_service_search_index(self, records: List[Any], sub_services: List[Any]):
        """
        Builds a semantic vector search index over all InformationRecords and SubServices.
        """
        self.doc_types: List[str] = []
        self.doc_objects: List[Any] = []
        self.doc_corpus: List[str] = []

        for rec in records:
            aliases_str = " ".join(rec.aliases or [])
            kw_str = " ".join(rec.keywords or [])
            hist_str = " ".join(rec.historical_names or [])
            text = f"{rec.title} {rec.previous_title or ''} {hist_str} {aliases_str} {kw_str} {rec.department} {rec.organization} {rec.description}".lower()
            self.doc_types.append("INFO_RECORD")
            self.doc_objects.append(rec)
            self.doc_corpus.append(text)

        for sub in sub_services:
            aliases_str = " ".join(sub.aliases or [])
            kw_str = " ".join(sub.keywords or [])
            text = f"{sub.sub_service_name} {sub.action_type} {aliases_str} {kw_str} {sub.description}".lower()
            self.doc_types.append("SUB_SERVICE")
            self.doc_objects.append(sub)
            self.doc_corpus.append(text)

        if self.doc_corpus:
            self.search_vectorizer = TfidfVectorizer(ngram_range=(1, 3), analyzer="char_wb", sublinear_tf=True)
            self.search_matrix = self.search_vectorizer.fit_transform(self.doc_corpus)
        else:
            self.search_vectorizer = None
            self.search_matrix = None

    def search_semantic(self, query: str, top_k: int = 3) -> List[Tuple[float, str, Any]]:
        """
        Searches government documents semantically via vector cosine similarity.
        """
        if not hasattr(self, 'search_matrix') or self.search_matrix is None:
            return []

        q_clean = query.lower().strip()
        q_vec = self.search_vectorizer.transform([q_clean])
        similarities = cosine_similarity(q_vec, self.search_matrix)[0]

        ranked_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            if score > 0.15:  # Semantic similarity threshold
                results.append((score, self.doc_types[idx], self.doc_objects[idx]))
        return results

# Global Singleton
SEMANTIC_ENGINE = SemanticEngine()
