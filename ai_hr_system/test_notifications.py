import asyncio
import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

from app.notifications.dispatcher import NotificationDispatcher

async def test_notification_languages():
    print("Testing Notification Dispatcher Language Selection...")
    dispatcher = NotificationDispatcher()
    
    test_cases = [
        {"status": "INVITED", "lang": "ru", "expected_start": "Поздравляем!"},
        {"status": "INVITED", "lang": "en", "expected_start": "Congratulations!"},
        {"status": "INVITED", "lang": "uz", "expected_start": "Tabriklaymiz!"},
        {"status": "REJECTED", "lang": "ru", "expected_start": "Спасибо за участие"},
        {"status": "REJECTED", "lang": "en", "expected_start": "Thank you for your interest"},
        {"status": "REJECTED", "lang": "uz", "expected_start": "Qiziqishingiz uchun rahmat"},
    ]
    
    for case in test_cases:
        print(f"\nTesting: {case['status']} in {case['lang']}...")
        content = dispatcher._get_template_content(f"{case['status'].lower()}.txt", case['lang'], "Test Candidate")
        
        if content:
            print(f"Content: {content[:50]}...")
            if content.startswith(case['expected_start']):
                print(f"[SUCCESS] Language {case['lang']} correctly selected.")
            else:
                print(f"[FAILURE] Content does not match expected start. Got: {content[:30]}")
        else:
            print(f"[FAILURE] Content not found for {case['status']} in {case['lang']}")

if __name__ == "__main__":
    asyncio.run(test_notification_languages())
