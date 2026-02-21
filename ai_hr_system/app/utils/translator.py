from typing import Dict, List, Optional

class Translator:
    """
    Simplified dictionary-based translator for interview questions and templates.
    Supports ru, en, uz.
    """
    
    DICTIONARY = {
        # Templates
        "Что такое {skill} и для чего он используется?": {
            "en": "What is {skill} and what is it used for?",
            "uz": "{skill} nima va u nima uchun ishlatiladi?"
        },
        "Объясните основные концепции {skill}.": {
            "en": "Explain the core concepts of {skill}.",
            "uz": "{skill} ning asosiy tushunchalarini tushuntiring."
        },
        "Какие преимущества даёт использование {skill}?": {
            "en": "What are the advantages of using {skill}?",
            "uz": "{skill} dan foydalanishning qanday afzalliklari bor?"
        },
        "Напишите простой пример использования {skill}.": {
            "en": "Write a simple example of using {skill}.",
            "uz": "{skill} dan foydalanishga oddiy misol yozing."
        },
        "Как бы вы решили базовую задачу с помощью {skill}?": {
            "en": "How would you solve a basic task using {skill}?",
            "uz": "{skill} yordamida asosiy vazifani qanday hal qilgan bo'lardingiz?"
        },
        "Создайте простое приложение используя {skill}.": {
            "en": "Create a simple application using {skill}.",
            "uz": "{skill} yordamida oddiy ilova yarating."
        },
        "Объясните продвинутые возможности {skill}.": {
            "en": "Explain the advanced features of {skill}.",
            "uz": "{skill} ning ilg'or imkoniyatlarini tushuntiring."
        },
        "Какие best practices существуют для {skill}?": {
            "en": "What are the best practices for {skill}?",
            "uz": "{skill} uchun qanday eng yaxshi amaliyotlar (best practices) mavjud?"
        },
        "Сравните {skill} с альтернативными решениями.": {
            "en": "Compare {skill} with alternative solutions.",
            "uz": "{skill} ni muqobil yechimlar bilan solishtiring."
        },
        "Как бы вы оптимизировали производительность в {skill}?": {
            "en": "How would you optimize performance in {skill}?",
            "uz": "{skill} da unumdorlikni qanday optimallashtirgan bo'lardingiz?"
        },
        "Спроектируйте решение для типичной задачи с {skill}.": {
            "en": "Design a solution for a typical task with {skill}.",
            "uz": "{skill} bilan odatiy vazifa uchun yechim loyihalang."
        },
        "Как обработать ошибки при работе с {skill}?": {
            "en": "How to handle errors when working with {skill}?",
            "uz": "{skill} bilan ishlashda xatolarni qanday qayta ishlash kerak?"
        },
        "Объясните внутреннее устройство {skill}.": {
            "en": "Explain the internal workings of {skill}.",
            "uz": "{skill} ning ichki tuzilishini tushuntiring."
        },
        "Какие архитектурные паттерны применимы для {skill}?": {
            "en": "What architectural patterns are applicable for {skill}?",
            "uz": "{skill} uchun qaysi arxitektura namunalari qo'llaniladi?"
        },
        "Как {skill} работает под капотом?": {
            "en": "How does {skill} work under the hood?",
            "uz": "{skill} ichki qismida qanday ishlaydi?"
        },
        "Спроектируйте масштабируемую систему используя {skill}.": {
            "en": "Design a scalable system using {skill}.",
            "uz": "{skill} yordamida kengaytiriladigan tizim loyihalang."
        },
        "Как бы вы решили сложную архитектурную задачу с {skill}?": {
            "en": "How would you solve a complex architectural task with {skill}?",
            "uz": "{skill} bilan murakkab arxitektura vazifasini qanday hal qilgan bo'lardingiz?"
        },
        "Оптимизируйте высоконагруженное приложение на {skill}.": {
            "en": "Optimize a high-load application on {skill}.",
            "uz": "{skill} dagi yuqori yuklamali ilovani optimallashtiring."
        },
        
        # Specific Question Bank Questions
        "Что такое list comprehension в Python и когда его использовать?": {
            "en": "What is list comprehension in Python and when to use it?",
            "uz": "Python-da list comprehension nima va uni qachon ishlatish kerak?"
        },
        "Напишите функцию, которая находит все уникальные элементы в списке.": {
            "en": "Write a function that finds all unique elements in a list.",
            "uz": "Ro'yxatdagi barcha noyob elementlarni topadigan funktsiya yozing."
        },
        "Объясните разницу между @staticmethod и @classmethod.": {
            "en": "Explain the difference between @staticmethod and @classmethod.",
            "uz": "@staticmethod va @classmethod o'rtasidagi farqni tushuntiring."
        },
        "Как бы вы оптимизировали код, который обрабатывает большой CSV файл?": {
            "en": "How would you optimize code that processes a large CSV file?",
            "uz": "Katta CSV faylini qayta ishlaydigan kodni qanday optimallashtirgan bo'lardingiz?"
        },
        "Объясните работу GIL (Global Interpreter Lock) и его влияние на многопоточность.": {
            "en": "Explain GIL (Global Interpreter Lock) and its impact on multithreading.",
            "uz": "GIL (Global Interpreter Lock) va uning ko'p oqimlilikka (multithreading) ta'sirini tushuntiring."
        },
        "Спроектируйте систему кэширования с TTL для API запросов.": {
            "en": "Design a caching system with TTL for API requests.",
            "uz": "API so'rovlari uchun TTL bo'lgan kesh tizimini loyihalang."
        },
        "Что такое замыкание (closure) в JavaScript?": {
            "en": "What is a closure in JavaScript?",
            "uz": "JavaScript-da closure (yopiqlik) nima?"
        },
        "Напишите функцию debounce для оптимизации поиска.": {
            "en": "Write a debounce function to optimize search.",
            "uz": "Qidiruvni optimallashtirish uchun debounce funktsiyasini yozing."
        },
        "Объясните разницу между Promise и async/await.": {
            "en": "Explain the difference between Promise and async/await.",
            "uz": "Promise va async/await o'rtasidagi farqni tushuntiring."
        },
        "Как бы вы оптимизировали работу асинхронных запросов в SPA?": {
            "en": "How would you optimize asynchronous requests in an SPA?",
            "uz": "SPA-da asinxron so'rovlarni qanday optimallashtirgan bo'lardingiz?"
        },
        "Объясните Event Loop и как работает очередь микрозадач.": {
            "en": "Explain the Event Loop and how the microtask queue works.",
            "uz": "Event Loop va microtask navbati qanday ishlashini tushuntiring."
        },
        "Спроектируйте систему управления состоянием для большого приложения.": {
            "en": "Design a state management system for a large application.",
            "uz": "Katta ilova uchun holatni boshqarish (state management) tizimini loyihalang."
        },
        "Что такое Virtual DOM и зачем он нужен?": {
            "en": "What is Virtual DOM and why is it needed?",
            "uz": "Virtual DOM nima va u nima uchun kerak?"
        },
        "Создайте простой компонент счётчика с useState.": {
            "en": "Create a simple counter component with useState.",
            "uz": "useState yordamida oddiy hisoblagich (counter) komponentini yarating."
        },
        "Объясните useEffect и его зависимости.": {
            "en": "Explain useEffect and its dependencies.",
            "uz": "useEffect va uning bog'liqliklarini (dependencies) tushuntiring."
        },
        "Как избежать лишних ререндеров в React?": {
            "en": "How to avoid unnecessary re-renders in React?",
            "uz": "React-da keraksiz qayta yuklanishlarni (re-renders) qanday oldini olish mumkin?"
        },
        "Объясните работу React Fiber и приоритизацию рендеринга.": {
            "en": "Explain React Fiber and rendering prioritization.",
            "uz": "React Fiber va renderlash ustuvorligini tushuntiring."
        },
        "Спроектируйте архитектуру для микрофронтенд приложения на React.": {
            "en": "Design an architecture for a micro-frontend application on React.",
            "uz": "React-da mikro-frontend ilovasi uchun arxitektura loyihalang."
        },
        "Что такое middleware в Express.js?": {
            "en": "What is middleware in Express.js?",
            "uz": "Express.js-da middleware nima?"
        },
        "Как организовать обработку ошибок в Express приложении?": {
            "en": "How to organize error handling in an Express application?",
            "uz": "Express ilovasida xatolarni qayta ishlashni qanday tashkil qilish kerak?"
        },
        "Спроектируйте систему обработки очередей с использованием Node.js.": {
            "en": "Design a queue processing system using Node.js.",
            "uz": "Node.js yordamida navbatlarni qayta ishlash tizimini loyihalang."
        },
        "Что такое ORM в Django и как он работает?": {
            "en": "What is ORM in Django and how does it work?",
            "uz": "Django-da ORM nima va u qanday ishlaydi?"
        },
        "Как оптимизировать запросы к базе данных в Django?": {
            "en": "How to optimize database queries in Django?",
            "uz": "Django-da ma'lumotlar bazasi so'rovlarini qanday optimallashtirish mumkin?"
        },
        "Спроектируйте систему прав доступа для многопользовательского приложения.": {
            "en": "Design a permissions system for a multi-user application.",
            "uz": "Ko'p foydalanuvchili ilova uchun ruxsatnomalar tizimini loyihalang."
        },
        "Что такое индексы и зачем они нужны?": {
            "en": "What are indexes and why are they needed?",
            "uz": "Indekslar nima va nima uchun ular kerak?"
        },
        "Как бы вы оптимизировали медленный SQL запрос?": {
            "en": "How would you optimize a slow SQL query?",
            "uz": "Sekin SQL so'rovini qanday optimallashtirgan bo'lardingiz?"
        },
        "Объясните разницу между INNER JOIN и LEFT JOIN.": {
            "en": "Explain the difference between INNER JOIN and LEFT JOIN.",
            "uz": "INNER JOIN va LEFT JOIN o'rtasidagi farqni tushuntiring."
        },
        "Что такое Docker контейнер и чем он отличается от виртуальной машины?": {
            "en": "What is a Docker container and how does it differ from a virtual machine?",
            "uz": "Docker konteyneri nima va u virtual mashinadan nimasi bilan farq qiladi?"
        },
        "Как организовать multi-stage build для оптимизации Docker образа?": {
            "en": "How to organize multi-stage build to optimize a Docker image?",
            "uz": "Docker tasvirini optimallashtirish uchun multi-stage build-ni qanday tashkil qilish kerak?"
        },
        "Спроектируйте Docker Compose конфигурацию для микросервисной архитектуры.": {
            "en": "Design a Docker Compose configuration for a microservices architecture.",
            "uz": "Mikroservis arxitekturasi uchun Docker Compose konfiguratsiyasini loyihalang."
        },
        
        "Спроектируйте Docker Compose конфигурацию для микросервисной архитектуры.": {
            "en": "Design a Docker Compose configuration for a microservices architecture.",
            "uz": "Mikroservis arxitekturasi uchun Docker Compose konfiguratsiyasini loyihalang."
        },
        
        # Short-form variations from QuestionBank
        "Что такое Virtual DOM?": {
            "en": "What is Virtual DOM?",
            "uz": "Virtual DOM nima?"
        },
        "Создайте счетчик с useState.": {
            "en": "Create a counter with useState.",
            "uz": "useState bilan hisoblagich yarating."
        },
        "Объясните useEffect.": {
            "en": "Explain useEffect.",
            "uz": "useEffect-ni tushuntiring."
        },
        "Как избежать ререндеров?": {
            "en": "How to avoid re-renders?",
            "uz": "Qayta yuklanishlarni (re-renders) qanday oldini olish mumkin?"
        },
        "React Fiber.": {
            "en": "React Fiber.",
            "uz": "React Fiber."
        },
        "Микрофронтенды.": {
            "en": "Micro-frontends.",
            "uz": "Mikrofrontendlar."
        },
        "Обработка ошибок в Express.": {
            "en": "Error handling in Express.",
            "uz": "Express-da xatolarni qayta ishlash."
        },
        "Очереди в Node.js.": {
            "en": "Queues in Node.js.",
            "uz": "Node.js-da navbatlar."
        },
        "Что такое ORM в Django?": {
            "en": "What is ORM in Django?",
            "uz": "Django-da ORM nima?"
        },
        "Оптимизация запросов в Django.": {
            "en": "Query optimization in Django.",
            "uz": "Django-da so'rovlarni optimallashtirish."
        },
        "Система прав в Django.": {
            "en": "Permissions system in Django.",
            "uz": "Django-da ruxsatnomalar tizimi."
        },
        "Что такое индексы?": {
            "en": "What are indexes?",
            "uz": "Indekslar nima?"
        },
        "Оптимизация медленного SQL.": {
            "en": "Slow SQL optimization.",
            "uz": "Sekin SQL-ni optimallashtirish."
        },
        "INNER vs LEFT JOIN.": {
            "en": "INNER vs LEFT JOIN.",
            "uz": "INNER vs LEFT JOIN."
        },
        "Docker vs VM?": {
            "en": "Docker vs VM?",
            "uz": "Docker vs VM?"
        },
        "Multi-stage build.": {
            "en": "Multi-stage build.",
            "uz": "Multi-stage build."
        },
        "Docker Compose для микросервисов.": {
            "en": "Docker Compose for microservices.",
            "uz": "Mikroservislar uchun Docker Compose."
        },

        # Soft skills / psychology questions (QuestionBank stores RU; QuestionSelector translates via this dictionary)
        "Как вы относитесь к работе в коллективе? Что для вас важнее: личный результат или успех команды?": {
            "en": "How do you feel about working in a team? What is more important to you: personal results or the team’s success?",
            "uz": "Jamoada ishlashga qanday qaraysiz? Siz uchun nimasi muhimroq: shaxsiy natija yoki jamoa muvaffaqiyati?"
        },
        "Как бы вы описали свой тип личности: интроверт, экстраверт или амбиверт? Как это влияет на вашу работу?": {
            "en": "How would you describe your personality type: introvert, extrovert, or ambivert? How does it affect your work?",
            "uz": "O'zingizning shaxsiyatingizni qanday ta'riflaysiz: introvert, extrovert yoki ambivert? Bu ish faoliyatingizga qanday ta'sir qiladi?"
        },
        "Представьте, что у вас возник конфликт с коллегой по поводу технического решения. Ваши действия?": {
            "en": "Imagine you have a conflict with a colleague about a technical decision. What would you do?",
            "uz": "Tasavvur qiling, texnik yechim bo'yicha hamkasbingiz bilan kelishmovchilik yuz berdi. Nima qilasiz?"
        },
        "Что вас больше всего мотивирует в работе, кроме финансовой составляющей?": {
            "en": "What motivates you most at work besides financial compensation?",
            "uz": "Moliyaviy tomondan tashqari, ishda sizni eng ko'p nima motivatsiya qiladi?"
        },
        "Вам нужно сообщить руководителю о том, что вы не успеваете сдать проект в срок. Как вы это сделаете?": {
            "en": "You need to tell your manager that you won’t be able to deliver the project on time. How would you do it?",
            "uz": "Rahbaringizga loyihani belgilangan muddatda topshira olmasligingizni aytishingiz kerak. Qanday aytasiz?"
        },
        "Опишите идеальную для вас рабочую атмосферу и культуру компании.": {
            "en": "Describe the ideal work environment and company culture for you.",
            "uz": "Siz uchun ideal ish muhiti va kompaniya madaniyatini tasvirlab bering."
        },
        "Что для вас важно при выборе компании: продукт, команда, уровень зарплаты, возможности роста? Расставьте по приоритету.": {
            "en": "What matters to you when choosing a company: product, team, salary level, or growth opportunities? Rank them by priority.",
            "uz": "Kompaniyani tanlashda siz uchun nimalar muhim: mahsulot, jamoa, maosh darajasi yoki o‘sish imkoniyatlari? Ularni ustuvorlik bo‘yicha joylashtiring."
        },
        "Представьте, что ценности компании частично расходятся с вашими личными. Как вы будете действовать в такой ситуации?": {
            "en": "Imagine the company’s values partly conflict with your personal values. How would you act in this situation?",
            "uz": "Tasavvur qiling, kompaniya qadriyatlari sizning shaxsiy qadriyatlaringiz bilan qisman mos kelmaydi. Bunday vaziyatda qanday harakat qilasiz?"
        },
        "Какой стиль управления (микроменеджмент, доверие, гибкость) для вас наиболее комфортен и почему?": {
            "en": "Which management style (micromanagement, trust, flexibility) is the most comfortable for you and why?",
            "uz": "Qaysi boshqaruv uslubi (mikroboshqaruv, ishonch, moslashuvchanlik) siz uchun eng qulay va nima uchun?"
        },
        "Компания переживает период активных изменений (рост, смена приоритетов). Как вы обычно адаптируетесь к таким ситуациям?": {
            "en": "The company is going through a period of active change (growth, shifting priorities). How do you usually adapt to such situations?",
            "uz": "Kompaniya faol o‘zgarishlar davrini boshdan kechirmoqda (o‘sish, ustuvorliklarning o‘zgarishi). Bunday vaziyatlarga odatda qanday moslashasiz?"
        },
        "Опишите ситуацию, когда вы были не согласны с решением руководства. Как вы выстроили диалог и к чему это привело?": {
            "en": "Describe a situation when you disagreed with a management decision. How did you build the dialogue and what was the outcome?",
            "uz": "Rahbariyat qarori bilan rozi bo‘lmagan vaziyatni tasvirlab bering. Suhbatni qanday boshladingiz va natijasi qanday bo‘ldi?"
        },
        "Как вы понимаете 'здоровую корпоративную культуру'? Какие сигналы для вас говорят о том, что в компании с этим есть проблемы?": {
            "en": "What does a “healthy corporate culture” mean to you? What signals tell you that a company has problems with it?",
            "uz": "“Sog‘lom korporativ madaniyat”ni siz qanday tushunasiz? Qaysi belgilar kompaniyada bu borada muammolar borligini ko‘rsatadi?"
        },
        "Как вы относитесь к удалённому формату работы по сравнению с офисным? В чём плюсы и минусы для вас лично?": {
            "en": "How do you feel about remote work compared to office work? What are the pros and cons for you personally?",
            "uz": "Masofaviy ishga ofis ishiga nisbatan qanday qaraysiz? Siz uchun shaxsiy jihatdan afzalliklari va kamchiliklari nimalar?"
        },
        "Что помогает вам сохранять мотивацию и вовлечённость в долгосрочных проектах компании?": {
            "en": "What helps you maintain motivation and engagement in the company’s long-term projects?",
            "uz": "Kompaniyaning uzoq muddatli loyihalarida motivatsiya va ishtirokingizni saqlab qolishga nima yordam beradi?"
        },
        "Представьте, что вам не до конца понятна стратегия компании. Какие шаги вы предпримете, чтобы лучше её понять?": {
            "en": "Imagine you do not fully understand the company’s strategy. What steps would you take to understand it better?",
            "uz": "Tasavvur qiling, kompaniya strategiyasini to‘liq tushunmaysiz. Uni yaxshiroq tushunish uchun qanday qadamlar tashlaysiz?"
        },
        
        # Topic names
        "python": {"uz": "Python"},
        "javascript": {"uz": "JavaScript"},
        "react": {"uz": "React"},
        "node.js": {"uz": "Node.js"},
        "django": {"uz": "Django"},
        "postgresql": {"uz": "PostgreSQL"},
        "docker": {"uz": "Docker"},
        "sql": {"uz": "SQL"},
        
        # Topics
        "best practices": {"uz": "eng yaxshi amaliyotlar"},
        "basics": {"uz": "asoslar"},
        "syntax": {"uz": "sintaksis"},
        "optimization": {"uz": "optimallashtirish"},
        "patterns": {"uz": "patternlar"},
        "architecture": {"uz": "arxitektura"},
        "scalability": {"uz": "kengaytiriluvchanlik"},
        "performance": {"uz": "unumdorlik"}
    }
    
    @classmethod
    def translate(cls, text: str, target_lang: str) -> str:
        """Translate text if found in dictionary, else return as is."""
        if target_lang == "ru":
            return text
            
        # Try exact match
        if text in cls.DICTIONARY:
            return cls.DICTIONARY[text].get(target_lang, text)
            
        # Try case-insensitive skill/topic match
        text_lower = text.lower()
        if text_lower in cls.DICTIONARY:
            return cls.DICTIONARY[text_lower].get(target_lang, text)
            
        return text
