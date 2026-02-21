from app.cv_intelligence.cv_analyzer import CVAnalyzer

def test_diagnostics():
    analyzer = CVAnalyzer()
    
    scenarios = {
        "Minimal Real CV": "John Doe. Email: doe@test.com. Experience: python dev.",
        "Short CV with Phone": "Jane Doe. +998901112233. Skills: Java, SQL.",
        "Only Markers": "Experience Skills Education CV Resume",
        "Fairy Tale (Long)": "Once upon a time in a kingdom far away... " * 100,
        "Actual Fairy Tale with one CV term": ("Once upon a time in a career... " * 100) + " Education",
        "Minimal ordinary CV (RU)": "Иван Иванов. Почта: ivan@mail.ru. Работа в банке."
    }

    for name, text in scenarios.items():
        print(f"\n>>> TESTING SCENARIO: {name}")
        result = analyzer._validate_resume(text)
        print(f"RESULT: {'PASS' if result else 'FAIL'}")

if __name__ == "__main__":
    test_diagnostics()
