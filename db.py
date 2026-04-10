import sqlite3
import random

def setup_database():
    conn = sqlite3.connect('student_system.db')
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS college (
            college_code TEXT PRIMARY KEY,
            college_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS program (
            program_code TEXT PRIMARY KEY,
            program_name TEXT NOT NULL,
            college_code TEXT,
            FOREIGN KEY (college_code) REFERENCES college(college_code)
        );

        CREATE TABLE IF NOT EXISTS student (
            id TEXT PRIMARY KEY,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            program_code TEXT,
            year INTEGER,
            gender TEXT,
            FOREIGN KEY (program_code) REFERENCES program(program_code)
        );
    ''')

    colleges = [('CCS', 'College of Computer Studies'), ('COE', 'College of Engineering'), ('CASS', 'College of Arts and Social Sciences'), ('CHS', 'College of Health Sciences'), ('CSM', 'College of Science and Mathematics'), ('CED', 'College of Education'), ('CEBA', 'College of Economics, Business, and Accountancy')]
    cursor.executemany('INSERT OR IGNORE INTO college VALUES (?,?)', colleges)

    programs = [
        ('BSCS', 'Bachelor of Science in Computer Science', 'CCS'),
        ('BSIT', 'Bachelor of Science in Information Technology', 'CCS'),
        ('BSEcon', 'Bachelor of Science in Economics', 'CEBA'),
        ('BSCE', 'Bachelor of Science in Civil Engineering', 'COE'),
        ('BSCpE', 'Bachelor of Science in Computer Engineering', 'COE'),
        ('BSEcE', 'Bachelor of Science in Electronics & Communications Engineering', 'COE'),
        ('BSME', 'Bachelor of Science in Mechanical Engineering', 'COE'),
        ('BSMetE', 'Bachelor of Science in Metallurgical Engineering', 'COE'),
        ('BSBio (Microbiology)', 'Bachelor of Science in Biology (Majoring in Microbiology)', 'CSM'),
        ('BSBio (Animal Biology)', 'Bachelor of Science in Biology (Majoring in Animal Biology)', 'CSM'),
        ('BSBio (Plant Biology)', 'Bachelor of Science in Biology (Majoring in Plant Biology)', 'CSM'),
        ('BSBio (Marine Biology)', 'Bachelor of Science in Biology (Majoring in Marine Biology)', 'CSM'),
        ('BSBio (Biodiversity)', 'Bachelor of Science in Biology (Majoring in Biodiversity)', 'CSM'),
        ('BSChem', 'Bachelor of Science in Chemistry', 'CSM'),
        ('BSPhy', 'Bachelor of Science in Physics', 'CSM'),
        ('BSHM', 'Bachelor of Science in Hospitality Management', 'CEBA'),
        ('BSPsych', 'Bachelor of Science in Psychology', 'CASS'),
        ('BAPsych', 'Bachelor of Arts in Psychology', 'CASS'),
        ('BAEng', 'Bachelor of Arts in English Literature', 'CASS'),
        ('BAFil', 'Bachelor of Arts in Filipino Language and Literature', 'CASS'),
        ('BSEdMath', 'Bachelor of Secondary Education in Mathematics', 'CED'),
        ('BSEdEnglish', 'Bachelor of Secondary Education in English', 'CED'),
        ('BSEdTLE', "Bachelor of Secondary Education in Technology Livelihood Education", "CED"),
        ('BSEE', "Bachelor of Science in Electrical Engineering", "COE"),
        ('BSStat', "Bachelor of Science in Statistics", "CSM"),
        ('BSAccountancy', "Bachelor of Science in Accountancy", "CEBA"),
        ('BSEdSH', "Bachelor of Secondary Education in Social Sciences", "CED"),
        ("BSCA", " Bachelor of Science in Computer Application", "CCS"), 
        ("BSIS", "Bachelor of Science in Information Systems", "CCS"), 
        ("BSN", "Bachelor of Science in Nursing", "CHS")
    ]
    cursor.executemany('INSERT OR IGNORE INTO program VALUES (?,?,?)', programs)

    first_names = ["Jose", "Maria", "Juan", "Liza", "Datu", "Paolo", "Catriona", "Junel", "Ligaya", "Reynaldo",
        "Althea", "Danilo", "Marites", "Rico", "Noli", "Perla", "Agapito", "Imelda", "Efren", "Diwa",
        "Bayani", "Luningning", "Bituin", "Maki", "Kidlat", "Hiraya", "Tala", "Malaya", "Dakila", "Sinag",
        "Isagani", "Lualhati", "Silang", "Magiting", "Diwata", "Dalisay", "Mutya", "Sampaguita", "Mayumi", "Liwayway",
        "Makisig", "Bathala", "Amado", "Bernardo", "Conrado", "Diosdado", "Edgardo", "Fernando", "Gregorio", "Honesto",
        "Isidro", "Jacinto", "Kulas", "Lamberto", "Modesto", "Nicanor", "Oswaldo", "Pacito", "Quirino", "Ruperto",
        "Satur", "Teodoro", "Ursulo", "Vicente", "Wilfredo", "Xavier", "Yoyoy",
        "James", "Jennifer", "Robert", "Linda", "John", "Michael", "Sarah", "William", "Elizabeth", "David",
        "Jessica", "Thomas", "Karen", "Steven", "Nancy", "Kevin", "Lisa", "Brian", "Sandra", "George",
        "Ashley", "Edward", "Alice", "Jason", "Amy", "Gary", "Donna", "Timothy", "Michelle", "Ronald",
        "Dorothy", "Jeffrey", "Carol", "Ryan", "Amanda", "Jacob", "Melissa", "Gary", "Susan", "Nicholas",
        "Emily", "Eric", "Rachel", "Stephen", "Laura", "Jonathan", "Rebecca", "Larry", "Sharon", "Scott",
        "Cynthia", "Justin", "Kathleen", "Brandon", "Shirley", "Gregory", "Angela", "Samuel", "Emma", "Patrick",
        "Grace", "Jack", "Chloe", "Benjamin", "Mia", "Oliver", "Zoe",
        "Ahmed", "Fatima", "Omar", "Aisha", "Zayd", "Ali", "Hassan", "Layla", "Mustafa", "Mariam",
        "Youssef", "Sana", "Ibrahim", "Noor", "Hamza", "Amira", "Khalid", "Salma", "Tariq", "Hana",
        "Zain", "Farrah", "Malik", "Rania", "Bassem", "Habiba", "Nasir", "Yasmin", "Idris", "Karima",
        "Sami", "Nadia", "Rayan", "Mona", "Faris", "Latifa", "Walid", "Samira", "Qasim", "Zahra",
        "Bilal", "Jamilah", "Rashid", "Dalal", "Yasin", "Inaya", "Fahad", "Nura", "Hakim", "Soraya",
        "Tahir", "Amani", "Mansour", "Reem", "Anas", "Lulu", "Jabbar", "Huda", "Saif", "Bashir",
        "Khadija", "Hisham", "Muna", "Aziz", "Fayez", "Asma"]
    last_names = ["Rizal", "Dela Cruz", "Santos", "Panganiban", "Aquino", "Bautista", "Villanueva", "Lumad", "Magsaysay", "Recto",
        "Dagohoy", "Silang", "Mabini", "Dalisay", "Agoncillo", "Bonifacio", "Luna", "Del Pilar", "Malvar", "Llanera",
        "Tirona", "Guevarra", "Sakay", "Tecson", "Makabulos", "Ponce", "Jaena", "Valenzuela", "Arellano", "Adriatico",
        "Mapa", "Zobel", "Ayala", "Soriano", "Araneta", "Tuason", "Locsin", "Ledesma", "Montinola", "Golez",
        "Escudero", "Singson", "Fuentebella", "Madrigal", "Osmeña", "Roxas", "Quirino", "Garcia", "Macapagal", "Marcos",
        "Estrada", "Arroyo", "Duterte", "Robredo", "Legarda", "Cayetano", "Pimentel", "Guingona", "Trillanes", "Honasan",
        "Lacson", "Enrile", "Belmonte", "Binay", "Sotto", "Gordon", "Pangilinan",
        "Smith", "Johnson", "Williams", "Brown", "Miller", "Davis", "Wilson", "Anderson", "Taylor", "Moore",
        "White", "Harris", "Thompson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres",
        "Nguyen", "Hill", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter",
        "Roberts", "Gomez", "Phillips", "Evans", "Parker", "Stewart", "Edwards", "Collins", "Cook", "Murphy",
        "Rogers", "Morgan", "Peterson", "Cooper", "Reed", "Bailey", "Bell", "Gomez", "Kelly", "Howard",
        "Ward", "Cox", "Diaz", "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray", "James",
        "Reyes", "Cruz", "Hughes", "Price", "Myers", "Long", "Foster",
        "Mansour", "Hassan", "Al-Farsi", "Said", "Abbas", "Al-Zahrani", "Bakir", "Khoury", "Saleh", "Mustafa",
        "Habibi", "Gaddafi", "Al-Sayed", "Mahmoud", "Yassin", "Hamdan", "Al-Amri", "Hariri", "Sarkis", "Tahan",
        "Ghanem", "Karam", "Haddad", "Maalouf", "Khairallah", "Bitar", "Najjar", "Asaf", "Sader", "Antar",
        "Maloof", "Sabbag", "Kattan", "Zogby", "Shalhoub", "Jaber", "Moussa", "Darwish", "Farah", "Atiyeh",
        "Nader", "Baal", "Qasim", "Hakim", "Halabi", "Rashid", "Fahd", "Salem", "Bashara", "Amari",
        "Azzi", "Badour", "Cham", "Daher", "Elias", "Fakhoury", "Gibran", "Hage", "Issa", "Kouri",
        "Lahoud", "Mughrabi", "Nassar", "Rahal", "Tamer", "Ziad"]
    
    students = []
    generated_ids = set()

    while len(students) < 6767:
        year_part = random.randint(2018, 2026)
        num_part = random.randint(1, 2500)
        s_id = f"{year_part}-{num_part:04d}"
        if s_id not in generated_ids:
            generated_ids.add(s_id)
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            selected_program = random.choice(programs)
            program_code = selected_program[0]
            year_level = random.randint(1, 4) 
            gender = random.choice(['Male', 'Female', 'Other'])
            
            students.append((s_id, fn, ln, program_code, year_level, gender))

    cursor.executemany('INSERT OR IGNORE INTO student VALUES (?,?,?,?,?,?)', students)
    conn.commit()
    conn.close()
    print("Database initialized with 6767 students!")

if __name__ == "__main__":
    setup_database()