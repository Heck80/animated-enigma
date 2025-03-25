# IntegriTEX – App 1 & App 2

Zwei miteinander verbundene Streamlit-Apps zur Analyse und Vorhersage von Marker-Dosierungen in Textilfasern anhand von Emissionsdaten.

---

## 📦 Inhalt

| Datei | Beschreibung |
|-------|--------------|
| `app.py` | App 1 – Datenerfassung und Verwaltung von Referenzdaten |
| `app2.py` | App 2 – Smarte gewichtete Regression + PDF-Export |
| `referenzdaten.csv` | Beispieldatei mit Referenzwerten |
| `IntegriTEX-Logo.png` | Logo für den PDF-Export |

---

## 🚀 Nutzung

### 1. Voraussetzungen installieren

```bash
pip install streamlit pandas numpy matplotlib scikit-learn reportlab
```

### 2. App 1 starten (Referenzdaten eingeben)

```bash
streamlit run app.py
```

### 3. App 2 starten (Vorhersage & PDF-Export)

```bash
streamlit run app2.py
```

---

## 🧠 Funktionen in App 2

- Smarte Regression basierend auf 100 %-Daten oder Top-3-Nachbarn
- Gewichtete Mischung aus Faseranteilen (White / Black / Natural / Indigo)
- Automatischer PDF-Export mit Logo & Ergebnisdaten
- Visualisierung der Regressionslinien
- Modell-Statusübersicht & Confidence-Indikator

---

## 📸 Screenshot

![Screenshot App2](https://via.placeholder.com/800x400?text=Hier+k%C3%B6nnte+ein+Screenshot+sein)

---

## 🛠️ Entwicklerhinweis

Stelle sicher, dass `referenzdaten.csv` und `IntegriTEX-Logo.png` im selben Ordner wie die Apps liegen.  
Beim Export wird die PDF automatisch im selben Verzeichnis gespeichert (`prediction_report.pdf`).

---

> Erstellt mit ❤️ für IntegriTEX – Tobias Herzog & Team