# Leasing Tracker für Home Assistant

Eine Custom Integration für Home Assistant, um Leasingfahrzeuge zu überwachen und verbleibende Kilometer zu berechnen.

## Features

✅ **Übersichtliche UI-Konfiguration** - Alle Einstellungen über die Home Assistant UI  
✅ **Automatische Berechnungen** - Verbleibende KM pro Monat, Jahr und Gesamtlaufzeit  
✅ **Detaillierte Statistiken** - Durchschnittswerte, Fortschritt und Status  
✅ **Mehrere Fahrzeuge** - Beliebig viele Leasingverträge gleichzeitig überwachen  
✅ **HACS kompatibel** - Einfache Installation und Updates über HACS  

## Sensoren

Die Integration erstellt folgende Sensoren:

### Verbleibende Kilometer
- **Verbleibende KM Gesamt** - Wie viele Kilometer noch bis zum Vertragsende gefahren werden können
- **Verbleibende KM dieses Jahr** - Geschätzte verbleibende KM für das aktuelle Kalenderjahr
- **Verbleibende KM diesen Monat** - Geschätzte verbleibende KM für den aktuellen Monat

### Zeitinformationen
- **Verbleibende Tage** - Tage bis zum Vertragsende
- **Verbleibende Monate** - Monate bis zum Vertragsende
- **Leasingdauer in Tagen** - Gesamte Vertragslaufzeit

### Gefahrene Kilometer
- **Gefahrene KM** - Seit Vertragsbeginn gefahrene Kilometer
- **Durchschnitt KM pro Tag** - Durchschnittlich gefahrene Kilometer pro Tag
- **Durchschnitt KM pro Monat** - Durchschnittlich gefahrene Kilometer pro Monat

### Vertragsdaten
- **Erlaubte KM Gesamt** - Gesamte erlaubte Kilometer über die Vertragslaufzeit
- **Erlaubte KM pro Monat** - Durchschnittlich erlaubte Kilometer pro Monat

### Status & Fortschritt
- **Fortschritt** - Prozentuale Vertragsabwicklung (Zeit-basiert)
- **KM Differenz zum Plan** - Differenz zwischen tatsächlich gefahrenen und geplanten KM
- **Status** - Textuelle Statusanzeige (Im Plan, Über Plan, etc.)

## Installation

### Methode 1: HACS (empfohlen)

1. Öffne HACS in Home Assistant
2. Klicke auf "Integrationen"
3. Klicke auf die drei Punkte (⋮) oben rechts
4. Wähle "Benutzerdefinierte Repositories"
5. Füge die URL hinzu: `https://github.com/DEIN-USERNAME/leasing_tracker`
6. Kategorie: "Integration"
7. Klicke auf "Hinzufügen"
8. Suche nach "Leasing Tracker"
9. Klicke auf "Herunterladen"
10. Starte Home Assistant neu

### Methode 2: Manuell

1. Lade die neueste Version herunter
2. Entpacke das Archiv
3. Kopiere den `leasing_tracker` Ordner nach `custom_components/` in deinem Home Assistant Konfigurationsverzeichnis
4. Verzeichnisstruktur sollte sein: `custom_components/leasing_tracker/`
5. Starte Home Assistant neu

## Konfiguration

### Schritt 1: Kilometerstand-Sensor erstellen

Zuerst benötigst du einen Sensor, der den aktuellen Kilometerstand deines Fahrzeugs enthält. Dieser kann z.B. von deinem Auto-API kommen oder manuell gepflegt werden.

**Option A: Manueller Input (für Testing)**

Füge in `configuration.yaml` hinzu:

```yaml
input_number:
  car_mileage:
    name: "Auto Kilometerstand"
    min: 0
    max: 500000
    step: 1
    unit_of_measurement: "km"
    icon: mdi:counter
```

**Option B: Template Sensor (wenn du bereits eine Quelle hast)**

```yaml
template:
  - sensor:
      - name: "Auto Kilometerstand"
        state: "{{ states('sensor.dein_auto_km') }}"
        unit_of_measurement: "km"
        device_class: distance
```

Nach dem Hinzufügen: Home Assistant neu laden oder neu starten.

### Schritt 2: Leasing Tracker hinzufügen

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **+ Integration hinzufügen**
3. Suche nach "**Leasing Tracker**"
4. Fülle das Formular aus:
   - **Name**: z.B. "BMW 3er Leasing"
   - **Aktueller Kilometerstand**: Wähle deinen KM-Sensor (z.B. `input_number.car_mileage`)
   - **Start-Datum**: Datum des Leasingbeginns
   - **End-Datum**: Datum des Leasingendes
   - **Kilometerstand bei Start**: KM-Stand zu Vertragsbeginn
   - **Erlaubte Kilometer pro Jahr**: z.B. 10000
5. Klicke auf **Senden**

### Schritt 3: Sensoren nutzen

Alle Sensoren erscheinen automatisch unter dem Gerät "Leasing Tracker" und können in:
- Dashboards
- Automatisierungen
- Benachrichtigungen
- Grafiken

verwendet werden.

## Beispiel Dashboard

Hier ist ein Beispiel für ein Lovelace-Dashboard:

```yaml
type: entities
title: BMW 3er Leasing
entities:
  - entity: sensor.mein_leasing_status
  - entity: sensor.mein_leasing_verbleibende_km_monat
  - entity: sensor.mein_leasing_verbleibende_km_jahr
  - entity: sensor.mein_leasing_verbleibende_km_gesamt
  - entity: sensor.mein_leasing_km_differenz_zum_plan
  - entity: sensor.mein_leasing_fortschritt
  - type: divider
  - entity: sensor.mein_leasing_gefahrene_km
  - entity: sensor.mein_leasing_durchschnitt_km_pro_monat
  - entity: input_number.car_mileage
```

## Beispiel Automatisierung

Benachrichtigung bei zu vielen gefahrenen Kilometern:

```yaml
automation:
  - alias: "Leasing KM Warnung"
    trigger:
      - platform: numeric_state
        entity_id: sensor.mein_leasing_km_differenz_zum_plan
        above: 500
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Leasing Warnung"
          message: "Du bist {{ states('sensor.mein_leasing_km_differenz_zum_plan') }} km über dem Plan!"
```

## Für andere bereitstellen (GitHub Repository)

### Schritt 1: GitHub Repository erstellen

1. Gehe zu [GitHub](https://github.com) und erstelle ein neues Repository
2. Name: z.B. `leasing_tracker`
3. Beschreibung: "Home Assistant Custom Integration for Leasing Car Tracking"
4. Public Repository
5. Initialisiere mit README

### Schritt 2: Dateien hochladen

1. Klone das Repository lokal:
   ```bash
   git clone https://github.com/DEIN-USERNAME/leasing_tracker.git
   cd leasing_tracker
   ```

2. Kopiere alle Dateien aus `custom_components/leasing_tracker/` in das Repository

3. Erstelle eine `.github/workflows/` Struktur für automatische Releases (optional)

4. Committe und pushe:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push
   ```

### Schritt 3: HACS Integration beantragen

1. Erstelle einen `hacs.json` im Root des Repositories:

```json
{
  "name": "Leasing Tracker",
  "render_readme": true,
  "domains": ["leasing_tracker"]
}
```

2. Gehe zu [HACS Default Repository Submission](https://github.com/hacs/default/issues/new?template=integration.yml)

3. Fülle das Formular aus:
   - Repository URL: `https://github.com/DEIN-USERNAME/leasing_tracker`
   - Beschreibung der Integration
   - Screenshots (optional aber empfohlen)

4. Warte auf Approval (kann einige Tage dauern)

### Schritt 4: Releases erstellen

Für Updates erstelle GitHub Releases:

1. Gehe zu "Releases" in deinem Repository
2. Klicke "Create a new release"
3. Tag: `v1.0.0` (verwende semantische Versionierung)
4. Beschreibe die Änderungen
5. Publish release

HACS erkennt automatisch neue Releases und bietet Updates an.

## Support

Bei Problemen oder Fragen:
- Öffne ein [Issue auf GitHub](https://github.com/DEIN-USERNAME/leasing_tracker/issues)
- Diskutiere im [Home Assistant Community Forum](https://community.home-assistant.io/)

## Lizenz

MIT License - siehe LICENSE Datei

## Credits

Entwickelt für die Home Assistant Community 🏠
