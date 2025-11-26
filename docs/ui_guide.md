# 🎨 UI Implementation Guide - Training Grounds

Guide z **Streamlit cheat sheetem** i instrukcjami bez gotowego kodu!

---

## 🎯 Nowy Flow (LEPSZY!)

```
1. Login (hasło) → już działa ✅
2. Profile Selection Screen → NOWY! 
3. Main App (chat + challenges)
```

**Zmiana koncepcji**: Profile wybierasz **NA POCZĄTKU**, nie w sidebarze!

---

## 📚 STREAMLIT CHEAT SHEET

### 🔹 Layout & Containers

#### `st.columns()`
Tworzy kolumny obok siebie
```python
col1, col2, col3 = st.columns(3)  # 3 równe kolumny
col1, col2 = st.columns([2, 1])   # 2:1 ratio

with col1:
    st.write("Lewa kolumna")
with col2:
    st.write("Prawa kolumna")
```

#### `st.container()`
Grupuje elementy
```python
with st.container():
    st.write("Element 1")
    st.write("Element 2")
```

#### `st.expander()`
Zwijana sekcja
```python
with st.expander("Kliknij aby rozwinąć"):
    st.write("Ukryta treść")
```

#### `st.form()`
Formularz (wszystko submit razem)
```python
with st.form("my_form"):
    name = st.text_input("Imię")
    age = st.number_input("Wiek")
    submitted = st.form_submit_button("Zapisz")
    if submitted:
        st.write(f"{name}, {age}")
```

---

### 🔹 Input Widgets

#### `st.text_input()`
Pole tekstowe
```python
name = st.text_input("Podaj imię", value="", max_chars=50)
```

#### `st.number_input()`
Pole numeryczne
```python
age = st.number_input("Wiek", min_value=0, max_value=100, value=10)
```

#### `st.selectbox()`
Dropdown lista
```python
option = st.selectbox("Wybierz", ["Opcja 1", "Opcja 2", "Opcja 3"])
```

#### `st.radio()`
Radio buttons
```python
choice = st.radio("Poziom", ["Łatwy", "Średni", "Trudny"])
```

#### `st.checkbox()`
Checkbox
```python
agree = st.checkbox("Zgadzam się")
if agree:
    st.write("Zaznaczone!")
```

#### `st.button()`
Przycisk
```python
if st.button("Kliknij mnie"):
    st.write("Kliknięto!")
```

---

### 🔹 Display Elements

#### `st.write()` / `st.markdown()`
Wyświetl tekst
```python
st.write("Zwykły tekst")
st.markdown("**Pogrubiony** *kursywa*")
```

#### `st.title()` / `st.header()` / `st.subheader()`
Nagłówki
```python
st.title("🎨 Duży tytuł")
st.header("Średni nagłówek")
st.subheader("Mały nagłówek")
```

#### `st.success()` / `st.error()` / `st.warning()` / `st.info()`
Kolorowe alerty
```python
st.success("✅ Sukces!")
st.error("❌ Błąd!")
st.warning("⚠️ Uwaga!")
st.info("ℹ️ Info")
```

#### `st.metric()`
Metryka (jak XP)
```python
st.metric(label="XP", value=150, delta=10)  # 150 (+10)
```

#### `st.divider()`
Linia pozioma
```python
st.divider()
```

---

### 🔹 Session State

Przechowywanie danych między reruns
```python
# Inicjalizacja
if "counter" not in st.session_state:
    st.session_state.counter = 0

# Odczyt
value = st.session_state.counter

# Zapis
st.session_state.counter = 10
st.session_state["new_key"] = "wartość"
```

---

### 🔹 Control Flow

#### `st.stop()`
Zatrzymaj wykonanie (jak return w funkcji)
```python
if not logged_in:
    st.warning("Zaloguj się!")
    st.stop()  # Reszta kodu się nie wykona
```

#### `st.spinner()`
Loading spinner
```python
with st.spinner("Ładowanie..."):
    time.sleep(3)  # Długa operacja
st.success("Gotowe!")
```

#### `st.rerun()`
Odśwież całą aplikację
```python
if st.button("Refresh"):
    st.rerun()
```

---

### 🔹 Sidebar

```python
with st.sidebar:
    st.header("Sidebar")
    option = st.selectbox("Wybór", ["A", "B"])
```

---

## 📋 Krok 1: Setup & Imports

**Importy do dodania**:
```python
from services.challenge_service import ChallengeService
from services.db_service import DbService
```

**Inicjalizacja serwisów**:
```python
@st.cache_resource
def get_challenge_service(api_key):
    return ChallengeService(api_key)

@st.cache_resource  
def get_db_service():
    return DbService()

challenge_service = get_challenge_service(st.secrets["GOOGLE_API_KEY"])
db_service = get_db_service()
```

---

## 📋 Krok 2: Profile Selection Screen

**Koncept**: Po loginie, przed main app, pokaż ekran wyboru profilu

### A. Application State Logic

```python
# Po AuthService.require_auth()

# Sprawdź czy profil wybrany
if "current_profile" not in st.session_state:
    show_profile_selection()  # Nowa funkcja!
    st.stop()  # Zatrzymaj - nie pokazuj reszty
    
# Jeśli profil wybrany, pokazuj main app
show_main_app()
```

### B. Profile Selection Screen

**Design**:
```
🧮 Witaj w Korepetytorze Matmy!

Kto dzisiaj się uczy?

┌──────────┐ ┌──────────┐ ┌──────────┐
│ 👤 Ania  │ │ 👤 Bartek│ │ + Dodaj  │
│ ⭐ 150XP │ │ ⭐ 85 XP │ │  nowy    │
│ Podstawa │ │ Średnia  │ │  profil  │
│[Wybierz] │ │[Wybierz] │ │          │
└──────────┘ └──────────┘ └──────────┘
```

**Pytania**:
1. Jak pobrać wszystkie profile z DB?
   - Hint: `db_service.get_all_profiles()`
   
2. Jak zrobić kartki obok siebie?
   - Hint: `st.columns(len(profiles) + 1)`
   
3. Co wyświetlić w każdej kartce?
   - Nickname
   - XP (użyj `st.metric()`)
   - Education level (czytelnie!)
   - Button "Wybierz"
   
4. Co się dzieje po kliknięciu "Wybierz"?
   - Zapisz profil do `st.session_state["current_profile"]`
   - `st.rerun()` żeby przeładować app

### C. "Dodaj profil" formularz

**Pytania**:
1. Czy użyć `st.form()` czy osobne inputy?
   - Hint: `st.form()` lepsze - submit wszystko razem
   
2. Jakie pola?
   - `st.text_input()` dla nickname
   - `st.radio()` dla education_level
   
3. Opcje education_level (mapowanie):
   ```python
   levels = {
       "Klasy 1-3": "podstawowka_1_3",
       "Klasy 4-8": "podstawowka_4_8",  
       "Szkoła średnia": "szkola_srednia",
       "Studia": "studia"
   }
   ```
   
4. Po zapisie:
   - Wywołaj `db_service.create_profile(nickname, level)`
   - Automatycznie wybierz nowy profil?
   - `st.rerun()` żeby odświeżyć listę

---

## 📋 Krok 4: Challenge Generator (Main Area)

**Lokalizacja**: Po sekcji czatu, przed końcem pliku

**Layout**:

### A. Divider
- `st.divider()` żeby oddzielić od czatu

### B. Header
- "🎯 Tryb Treningowy" lub podobny

### C. Category Selector
**Pytania**:
- Jakie kategorie? (Algebra, Geometria, Arytmetyka?)
- `st.selectbox` czy `st.radio`?
- Jak zapisać wybór?

### D. "Generuj Zadanie" Button
**Funkcjonalność**:
```
Przy kliknięciu:
1. Sprawdź czy profil wybrany (jeśli nie → error)
2. Wywołaj challenge_service.generate_challenge(profile_id, category)
3. Zapisz wynik w st.session_state["current_challenge"]
4. Wyświetl problem
```

**Pytania**:
- Jak pokazać loading spinner podczas generowania? (`st.spinner`?)
- Co jeśli generowanie zajmie 20s? User czeka?
- Jak obsłużyć błędy (np. Gemini timeout)?

### E. Problem Display
**Koncept**: Jeśli `st.session_state.get("current_challenge")` istnieje:

**Elementy**:
- Wyświetl `problem_text` (duży font, może `st.subheader`?)
- Input dla odpowiedzi (`st.text_input`)
- Button "Sprawdź odpowiedź"

**Pytania**:
- Czy pokazać hints na tym samym ekranie?
- Czy pokazać difficulty?

### F. Submit Answer
**Funkcjonalność**:
```
Przy kliknięciu "Sprawdź":
1. Pobierz user_answer z input
2. Wywołaj challenge_service.submit_answer(...)
3. Wyświetl feedback (st.success lub st.error)
4. Jeśli correct → pokazać konfetti? 🎊
5. Refresh profil (XP updated)
```

**Pytania**:
- Jak wyświetlić różny feedback dla correct vs incorrect?
- `st.success()` dla correct, `st.error()` dla wrong?
- Czy wyczyścić input po submit?

---

## 📋 Krok 5: Historia (Optional dla MVP)

**Lokalizacja**: Pod challenge generator

**Koncept**: 
- Pobierz ostatnie 5 submissions dla profilu
- Wyświetl jako tabelka lub lista

**Pytania**:
- `st.table()` czy `st.dataframe()`?
- Jakie kolumny pokazać?
  - ✅/❌ icon
  - Problem text (skrócony do 50 znaków)
  - XP earned
  - Timestamp
- Czy dodać pagination (więcej niż 5)?

**Advanced**: Czy użyć `st.expander()` żeby historia była zwijana?

---

## 🎨 Design Tips

### Kolory i ikony
- ✅ Użyj emoji dla wizualnej przyjemności
- Profile: 👤
- XP: ⭐ lub 🏆
- Correct: 🎉 lub ✅
- Wrong: ❌ lub 💪

### Layout
```
Sidebar:
├─ 📸 Materiały (już jest)
├─ 👤 Profil
└─ 🐞 Debug mode

Main:
├─ 💬 Chat (już jest)
├─ ➖ Divider
└─ 🎯 Tryb Treningowy
    ├─ Category picker
    ├─ Generate button
    ├─ Problem display
    └─ 📊 Historia (zwijana)
```

### Session State Management

**Potrzebne keys**:
```python
st.session_state["current_profile"]  # Dict z profile data
st.session_state["current_challenge"]  # Dict z problem + challenge_id
st.session_state["messages"]  # Już jest (chat)
```

**Pytanie**: Czy wyczyścić `current_challenge` po submit? A może zostawić żeby user widział co rozwiązywał?

---

## 🐛 Error Handling

### Scenariusze do obsłużenia:

1. **Brak profilu**
```
User klika "Generuj" bez wyboru profilu
→ st.warning("Najpierw wybierz profil!")
```

2. **Generowanie failed**
```
Agent B timeout lub error
→ st.error("Nie udało się wygenerować. Spróbuj ponownie.")
```

3. **Database offline**
```
Supabase nie odpowiada
→ st.error("Problem z połączeniem. Sprawdź internet.")
```

4. **Pusta odpowiedź**
```
User klika submit bez wpisania nic
→ Grader już to obsługuje, ale możesz dodać check przed wywołaniem
```

---

## ✅ Acceptance Criteria

Przed testowaniem upewnij się że:

- [ ] Profile dropdown działa i ładuje z DB
- [ ] Można dodać nowy profil przez formularz
- [ ] XP się wyświetla dla wybranego profilu
- [ ] Category selector ma sensowne opcje
- [ ] "Generuj" button wywołuje Agent A → B
- [ ] Problem się wyświetla czytelnie
- [ ] Input dla odpowiedzi działa
- [ ] Submit button wywołuje grading
- [ ] Feedback jest czytelny (różne kolory dla correct/wrong)
- [ ] XP się actualizuje po correct answer
- [ ] Historia pokazuje ostatnie próby

---

## 🎯 Testing Flow

**Manualny test**:
```
1. Start app → login
2. Sidebar: wybierz profil "Ania"
3. Zobacz XP: 0
4. Main: wybierz "Algebra"
5. Kliknij "Generuj Zadanie"
6. Czekaj ~10-20s
7. Problem się pojawia
8. Wpisz POPRAWNĄ odpowiedź
9. Kliknij "Sprawdź"
10. Zobacz: ✅ + feedback + XP: 10
11. Historia: 1 wpis z ✅

Po błędnej:
1. Generuj nowe zadanie
2. Wpisz ZŁĄ odpowiedź
3. Zobacz: ❌ + feedback + XP: 0 (no change)
```

---

## 💡 Dodatkowe pomysły (po MVP)

- **Countdown timer**: "Rozwiąż w 60s!"
- **Streak system**: X zadań z rzędu correct
- **Daily challenge**: Jedno specjalne dziennie
- **Leaderboard**: Ranking rodziny
- **Achievement badges**: "10 zadań correct!"
- **Hint button**: Wywołanie Agent E (po implementacji)

---

## 🚀 Kolejność implementacji

Polecam robić **krok po kroku**:

1. **Start simple**: Tylko profile selector (bez formularza add)
2. **Test DB**: Czy profile się ładują?
3. **Add category picker** + generate button
4. **Test generation**: Czy problem się generuje?
5. **Add answer input** + submit
6. **Test grading**: Czy działa?
7. **Add XP display** + refresh po submit
8. **Add historia** (ostatnie)

**Nie rób wszystkiego naraz!** Testuj każdy element osobno! 🎯

Powodzenia! 🚀
