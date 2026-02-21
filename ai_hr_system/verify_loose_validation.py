from app.cv_intelligence.cv_analyzer import CVAnalyzer

def test_validation():
    analyzer = CVAnalyzer()
    
    # 1. Very simple/ordinary CV
    simple_cv = """
    Ivan Ivanov
    Email: ivan@example.com
    Experience: 2 years in Python development.
    Skills: Python, Django, SQL.
    """
    
    # 2. Short CV with minimal markers
    short_cv = "John Doe. Phone: +998901234567. I am a developer. CV 2023."
    
    # 3. Non-CV junk
    junk = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

    print(f"Simple CV valid? {analyzer._validate_resume(simple_cv)}") # Expect True
    print(f"Short CV valid? {analyzer._validate_resume(short_cv)}")   # Expect True
    print(f"Junk valid? {analyzer._validate_resume(junk)}")           # Expect False

if __name__ == "__main__":
    test_validation()
