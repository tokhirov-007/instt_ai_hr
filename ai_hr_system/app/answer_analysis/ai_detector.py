import re
from typing import List
from app.answer_analysis.schemas import AnalysisResult, AnalysisType

class AIDetector:
    """
    Heuristic-based detector of AI-generated content patterns (V2).
    Analyzes style, structure, markers, and entropy simulation.
    """
    
    # 1. Expanded AI Markers (The "Fingerprints")
    AI_MARKERS = [
        # EN
        r"it's important to note", r"in terms of", r"from a technical perspective", r"to summarize",
        r"furthermore", r"moreover", r"additionally", r"typically", r"in many cases",
        r"key features include", r"one should consider", r"it is worth mentioning", r"best practices suggest",
        r"as an ai language model", r"i cannot provides", r"delves into", r"comprehensive overview",
        r"complex landscape", r"tapestry of", r"rich history", r"not only ... but also",
        
        # RU
        r"важно отметить", r"с технической точки зрения", r"подводя итог", r"кроме того",
        r"более того", r"дополнительно", r"как привило", r"в большинстве случаев",
        r"стоит упомянуть", r"лучшие практики", r"как языковая модель", r"не могу предоставить",
        r"в заключение", r"следует учитывать", r"является важным аспектом", r"играет ключевую роль",
        r"не только ..., но и", r"рассмотрим подробнее", r"резюмируя вышесказанное",
        
        # UZ
        r"shuni ta'kidlash kerakki", r"texnik nuqtai nazardan", r"xulosa qilib aytganda",
        r"bundan tashqari", r"qo'shimcha ravishda", r"odatda", r"ko'p hollarda",
        r"sun'iy intellekt sifatida", r"tavsiya etiladi", r"eng yaxshi amaliyotlar",
        r"e'tiborga loyiq", r"hisobga olish kerak", r"muhim ahamiyatga ega", r"asosiy omillardan biri",
        r"quyidagilarni o'z ichiga oladi", r"tahlil qilish kerak", r"misol sifatida",
        r"umumlashtirganda", r"ahamiyatli jihati shundaki"
    ]

    def analyze(self, text: str, time_spent: int = 0) -> AnalysisResult:
        """
        Analyze text for AI indicators, unnatural typing speed, and entropy.
        """
        if not text:
            return AnalysisResult(type=AnalysisType.AI_DETECTION, score=0.0, flags=["empty_text"])

        flags = []
        
        # 0. SPEED TRAP: Check for superhuman typing speed
        # Average typing speed is 40 WPM. Fast is 80-100. Impossible is >150.
        word_count = len(text.split())
        wpm = 0
        if time_spent > 0:
            wpm = (word_count / time_spent) * 60
            
        if wpm > 150 and word_count > 10: 
            flags.append("superhuman_typing_speed")
        elif wpm > 100 and word_count > 10:
            flags.append("fast_typing_suspicion")

        # 1. Check for specific AI markers (linguistic patterns)
        marker_count = 0
        found_markers = []
        text_lower = text.lower()
        for marker in self.AI_MARKERS:
            if marker in text_lower:
                marker_count += 1
                found_markers.append(marker)
        
        # 2. Analyze structure (AI often uses perfect bullet points or "Star Lists")
        structure_score = 0.0
        
        # Check for list patterns
        lines = text.split('\n')
        star_bullets = len([l for l in lines if l.strip().startswith('* ')])
        dash_bullets = len([l for l in lines if l.strip().startswith('- ')])
        numbered_lists = len(re.findall(r"^\d+\.\s", text, re.MULTILINE))
        
        if star_bullets > 2: # AI loves using * for bullets
            flags.append("ai_star_formatting")
            structure_score += 0.25
        elif dash_bullets > 2:
            flags.append("perfect_bullet_points")
            structure_score += 0.15
        elif numbered_lists > 2:
            flags.append("perfect_numbered_list")
            structure_score += 0.15
            
        # Check for "Term: Definition" pattern (common in AI explanations)
        colon_definitions = len(re.findall(r"^\**[\w\s]+:\**\s", text, re.MULTILINE))
        if colon_definitions > 1:
            flags.append("colon_definitions_pattern")
            structure_score += 0.2

        # 3. Entropy / Perplexity Simulation
        # AI text often has a "flat" vocabulary distribution. Humans are more chaotic.
        words = re.findall(r'\w+', text_lower)
        if len(words) > 20:
            unique_words = len(set(words))
            ratio = unique_words / len(words)
            
            # Very low ratio = repetitive (dumb bot or copy-paste spam)
            # Very high ratio (near 1.0) for long text = suspicious unique word usage (thesaurus stuffing or AI)
            # AI tends to be in a "sweet spot" of 0.5-0.7 for technical text.
            # But let's verify REPETITION specifically.
            if ratio < 0.4:
                flags.append("high_repetition_rate")
                structure_score += 0.2
            
            # Clause coupling check: "However, ...", "Therefore, ..."
            transitions = ["however", "therefore", "thus", "consequently", "moreover", "lekin", "shuning uchun"]
            trans_count = sum(1 for t in transitions if t in text_lower)
            if trans_count > 2 and len(words) < 50: # Too many transitions for short text
                flags.append("robot_transitions")
                structure_score += 0.2

        # 4. Perfect grammar indicator
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if len(sentences) > 0:
            # Check capitalization of first letter of sentences
            perfect_caps = sum(1 for s in sentences if s[0].isupper())
            if perfect_caps == len(sentences) and len(sentences) > 2:
                # Humans usually miss one or two in chat
                structure_score += 0.1

        # Calculate final probability
        # Base from markers
        marker_score = min(0.6, marker_count * 0.15) 
        
        # Combine
        ai_probability = min(0.98, marker_score + structure_score)
        
        # Boost probability if speed trap triggered
        if "superhuman_typing_speed" in flags:
            ai_probability = max(ai_probability, 0.99)
        elif "fast_typing_suspicion" in flags:
            ai_probability = max(ai_probability, 0.75)
        
        if marker_count >= 3:
            flags.append("high_marker_density")
            ai_probability = max(ai_probability, 0.85)
            
        return AnalysisResult(
            type=AnalysisType.AI_DETECTION,
            score=round(ai_probability, 2),
            probability=ai_probability,
            flags=list(set(flags)), # Remove duplicates
            details={
                "marker_count": marker_count,
                "found_markers": found_markers[:3],
                "wpm": round(wpm, 1),
                "structure_score": round(structure_score, 2)
            }
        )
