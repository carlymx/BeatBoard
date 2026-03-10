# BeatBoard Benutzerhandbuch

![main](../../imgs/beatboard_002.png)

## Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Erste Schritte](#erste-schritte)
3. [Benutzeroberfläche](#benutzeroberfläche)
4. [Beats verwalten](#beats-verwalten)
5. [Verbindungen zwischen Beats](#verbindungen-between-beats)
6. [Leinwand-Werkzeuge](#leinwand-werkzeuge)
7. [Anpassung](#anpassung)
8. [Export und Speichern](#export-und-speichern)
9. [Tastenkürzel](#tastenkürzel)
10. [Fehlerbehebung](#fehlerbehebung)

---

## Einführung

BeatBoard ist eine virtuelle Desktop-Whiteboard-Anwendung für Schriftsteller, inspiriert vom Beat Board von Final Draft. Es ist ein Werkzeug, das speziell für Drehbuchautoren, Kurzgeschichten- und Romanautoren entwickelt wurde, die die Struktur ihrer Geschichten visualisieren müssen.

Mit BeatBoard können Sie:
- Eine unbegrenzte Leinwand zum Organisieren Ihrer Ideen erstellen
- Beat-Karten mit Titel und Inhalt erstellen
- Beats mit gekrümmten Flusslinien verbinden
- Ihre Elemente visuell organisieren und neu anordnen
- Das Erscheinungsbild mit Themen und Farben anpassen
- Ihre Arbeit als PDF oder Text exportieren

---

## Erste Schritte

### Installation

So führen Sie BeatBoard aus:

1. **Aus dem Quellcode**:
   ```bash
   cd BeatBoard
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate  # Windows
   pip install pyside6
   python -m beatboard.app.main
   ```

2. **Vorkompilierte ausführbare Datei**:
   Laden Sie die ausführbare Datei von der Release-Seite herunter und führen Sie sie direkt aus.

### Ihr Erstes Projekt erstellen

Beim Start von BeatBoard wird automatisch ein leeres Projekt erstellt. Sie können sofort Beats auf der Leinwand erstellen.

So speichern Sie Ihr Projekt:
1. Gehen Sie zu **Datei > Speichern** (oder drücken Sie **Strg+S**)
2. Wählen Sie den Speicherort und den Namen für Ihre Datei
3. BeatBoard-Projekte haben die Erweiterung `.bbp`

---

## Benutzeroberfläche

![beatboard_interface](../../imgs/manual/0001.png)

Die BeatBoard-Oberfläche ist in folgende Bereiche unterteilt:

### Symbolleiste

![beatboard_interface](../../imgs/manual/0002.png)

Die Symbolleiste bietet schnellen Zugriff auf die am häufigsten verwendeten Funktionen:

| Schaltfläche | Funktion | Tastenkürzel |
|--------------|----------|--------------|
| Neu | Neues Projekt erstellen | Strg+N |
| Öffnen | Vorhandenes Projekt öffnen | Strg+O |
| Speichern | Projekt speichern | Strg+S |
| + (Vergrößern) | Zoom erhöhen | Strg++ |
| - (Verkleinern) | Zoom verringern | Strg+- |
| Zoom | Flächenauswahl-Zoom | Z |
| Anpassen | Ansicht an Inhalt anpassen | Strg+0 |
| Zentrieren | Ansicht auf Ursprung zentrieren | - |
| Verbinden | Verbindungsmodus aktivieren | C |

### Eigenschaftenpanel

![beatboard_interface](../../imgs/manual/0003.png)

Das Eigenschaftenpanel (rechts) ermöglicht das Bearbeiten des ausgewählten Elements:

- **Kein Beat ausgewählt**: Zeigt eine Meldung "Nichts ausgewählt"
- **Ein Beat ausgewählt**: Ermöglicht das Bearbeiten von Titel, Inhalt, Farbe und Titelanzeige
- **Mehrere Beats ausgewählt**: Ermöglicht das Bearbeiten gemeinsamer Eigenschaften
- **Verbindung ausgewählt**: Ermöglicht das Bearbeiten von Farbe, Liniendicke, Knotenform und Beschriftung

### Statusleiste

Die untere Leiste zeigt nützliche Informationen:
- Anzahl der Beats im Projekt
- Aktueller Zoomlevel
- Projektstatus (Geändert/Gespeichert)
- Cursorposition auf der Leinwand

---

## Beats verwalten

![beatboard_interface](../../imgs/manual/0004.png)

### Einen Beat erstellen

**Methode 1 - Doppelklick**:
1. Doppelklicken Sie auf einen leeren Bereich der Leinwand
2. Ein neuer Beat wird an dieser Position erstellt

### Einen Beat bearbeiten

![beatboard_interface](../../imgs/manual/0005.png)

**Schnellbearbeitung**:
1. Doppelklicken Sie auf den Beat, den Sie bearbeiten möchten
2. Der Beat-Bearbeitungsdialog wird geöffnet

![beatboard_interface](../../imgs/manual/0006.png)

**Bearbeitung über das Eigenschaftenpanel**:
1. Wählen Sie den Beat
2. Bearbeiten Sie den Titel oder Inhalt direkt im Eigenschaftenpanel
3. Änderungen werden automatisch angewendet

**Vollständiger Editor**:
1. Wählen Sie den Beat
2. Klicken Sie im Eigenschaftenpanel auf "Vollständigen Editor öffnen"
3. Der Dialog mit erweiterten Formatierungsoptionen wird geöffnet

### Der Beat-Editor

Der Beat-Editor bietet folgende Formatierungswerkzeuge:

#### Formatierungsleiste
- **B** (Fett): Wendet Fettformatierung auf den ausgewählten Text an
- *I* (Kursiv): Wendet Kursivformatierung an
- **U** (Unterstrichen): Wendet Unterstreichung an
- **Schriftgröße**: Schriftgrößenauswahl (8-32pt)
- **H1, H2, H3**: Überschriften verschiedener Ebenen einfügen
- **•** (Aufzählungspunkte): Aufzählungsliste einfügen
- **A** (Textfarbe): Farbe des ausgewählten Textes ändern
- **█** (Hervorhebung): Hintergrundfarbe auf Text anwenden
- **[Link]**: Hyperlink einfügen
- **[Code]**: Text mit Code-Formatierung einfügen
- **[Quote]**: Zitat einfügen

#### Editor-Felder
- **Titel**: Beat-Name (optional)
- **Inhalt**: Detaillierte Beat-Beschreibung (unterstützt Rich-Formatierung)
- **Farbe**: Beat-Farbauswahl

### Einen Beat verschieben

1. Klicken Sie auf den Beat
2. Ziehen Sie den Beat an die neue Position
3. Lassen Sie die Maustaste los

### Mehrfachauswahl

**Mehrere Beats auswählen**:
- Halten Sie die **Strg**-Taste gedrückt und klicken Sie auf jeden Beat
- Oder ziehen Sie ein Auswahlrechteck um die gewünschten Beats

**Mehrere Beats verschieben**:
1. Wählen Sie mehrere Beats aus
2. Ziehen Sie einen davon
3. Alle ausgewählten Beats werden zusammen verschoben

### Kopieren und Einfügen

- **Kopieren**: Wählen Sie den Beat und drücken Sie **Strg+C**
- **Ausschneiden**: Wählen Sie den Beat und drücken Sie **Strg+X**
- **Einfügen**: Drücken Sie **Strg+V**, um eine Kopie in der Mitte der Leinwand zu erstellen

### Einen Beat löschen

1. Wählen Sie den Beat (oder die Beats)
2. Drücken Sie **Entf** oder mit **Rechtsklick > Löschen**

### Z-Reihenfolge (Tiefe)

![beatboard_interface](../../imgs/manual/0007.png)

BeatBoard ermöglicht die Steuerung, welche Beats vor anderen angezeigt werden:

| Aktion | Tastenkürzel | Beschreibung |
|--------|--------------|--------------|
| In den Vordergrund bringen | Strg+Pos1 | Verschiebt den Beat in die oberste Ebene |
| In den Hintergrund senden | Strg+Ende | Verschiebt den Beat in die unterste Ebene |
| Nach oben | Strg+BildAuf | Tauscht die Position mit dem Beat direkt darüber |
| Nach unten | Strg+BildAb | Tauscht die Position mit dem Beat direkt darunter |

### Beat-Farben

![beatboard_interface](../../imgs/manual/0008.png)

BeatBoard bietet 10 vordefinierte Farben und 3 anpassbare:

| Taste | Farbe |
|-------|-------|
| 1 | Gelb |
| 2 | Blau |
| 3 | Grün |
| 4 | Rot |
| 5 | Orange |
| 6 | Lila |
| 7 | Grau |
| 8 | Anpassbar 1 |
| 9 | Anpassbar 2 |
| 0 | Anpassbar 3 |

**Farbe mit Tastatur ändern**:
1. Wählen Sie einen oder mehrere Beats
2. Drücken Sie eine Taste von 1 bis 0

**Farben anpassen**:
1. Wählen Sie einen Beat und öffnen Sie den **Vollständigen Editor**
2. Doppelklicken Sie auf eine der drei anpassbaren Farben und bearbeiten Sie sie

---

## Verbindungen zwischen Beats

![beatboard_interface](../../imgs/manual/0009.png)

Verbindungen sind gekrümmte Linien, die zwei Beats verbinden und den Fluss der Geschichte zeigen.

### Eine Verbindung erstellen

**Methode 1 - Symbolleiste**:
1. Klicken Sie auf die Schaltfläche "Verbinden" in der Symbolleiste (oder drücken Sie **C**)
2. Der Cursor wird zu einem Kreuz
3. Klicken Sie auf den Quell-Beat
4. Klicken Sie auf den Ziel-Beat
5. Die Verbindung wird automatisch erstellt
6. Drücken Sie **Esc**, um den Verbindungsmodus zu beenden

**Hinweis**: Wenn der Verbindungsmodus aktiv ist, erscheint ein Banner am unteren Rand der Leinwand mit der Aufschrift "Verbindungsmodus aktiviert".

### Eine Verbindung bearbeiten

**Verbindung auswählen**:
- Klicken Sie direkt auf die Verbindungslinie
- Die Verbindung wird mit einem blauen Rand hervorgehoben

![beatboard_interface](../../imgs/manual/0010.png)

**Verbindungseigenschaften** (im Eigenschaftenpanel):
- **Farbe**: Linienfarbe (rot, blau, grün, gelb, orange, lila, dunkelgrau)
- **Dicke**: Liniendicke (0,5 - 10 px)
- **Knotenform**: Form des Abschlusses an den Enden:
  - Kreis
  - Quadrat
  - Pfeil
  - Keine
- **Beschriftung**: Text, der in der Mitte der Verbindung erscheint

### Bearbeitbare Knoten

![beatboard_interface](../../imgs/manual/0011.png)

Verbindungen haben Kontrollpunkte, mit denen Sie ihre Krümmung ändern können:

1. Wählen Sie die Verbindung
2. Zwei Griffe (Punkte) erscheinen auf der Linie
3. Ziehen Sie die Griffe, um die Kurve anzupassen
4. Doppelklicken Sie auf einen Griff, um die Standardkrümmung wiederherzustellen

### Eine Verbindung löschen

1. Wählen Sie die Verbindung
2. Drücken Sie **Entf**

---

## Leinwand-Werkzeuge

### Zoom

**Vergrößern**:
- Gehen Sie zu **Ansicht > Vergrößern**
- Drücken Sie **Strg++**
- Oder verwenden Sie die Schaltfläche "+" in der Symbolleiste

**Verkleinern**:
- Gehen Sie zu **Ansicht > Verkleinern**
- Drücken Sie **Strg+-**
- Oder verwenden Sie die Schaltfläche "-" in der Symbolleiste

**An Inhalt anpassen**:
- Gehen Sie zu **Ansicht > An Inhalt anpassen**
- Drücken Sie **Strg+0**
- Oder verwenden Sie die Schaltfläche "Anpassen" in der Symbolleiste

**Flächenauswahl-Zoom**:
1. Drücken Sie **Z** oder klicken Sie auf die Zoom-Schaltfläche in der Symbolleiste
2. Ziehen Sie ein Rechteck um den Bereich, den Sie sehen möchten
3. Die Ansicht wird zentriert und an den ausgewählten Bereich angepasst
4. Drücken Sie **Esc** zum Abbrechen

### Schwenken

**Mit Tastatur**:
- Halten Sie die **Leertaste** gedrückt
- Ziehen Sie die Maus, um die Leinwand zu verschieben

**Mit Maus**:
- Halten Sie die mittlere Maustaste gedrückt
- Ziehen Sie, um die Leinwand zu verschieben

### Raster

Das Raster hilft Beats visuell auszurichten.

**Anzeigen/Ausblenden**:
- Gehen Sie zu **Ansicht > Raster anzeigen**
- Oder verwenden Sie das konfigurierte Tastenkürzel

**Raster anpassen**:
1. Gehen Sie zu **Ansicht > Rasteroptionen**
2. **Zellengröße**: Wählen Sie zwischen 50, 100, 150, 200 oder 250 px
3. **Rasterfarbe**: 
   - Auto: Passt sich dem Thema an
   - Vordefinierte Farben: Gelb, Blau, Grün, Rot, Orange, Lila, Grau
   - Benutzerdefiniert: Wählen Sie Ihre eigene Farbe

### Mittelpunkt

![beatboard_interface](../../imgs/manual/0012.png)

Der Mittelpunkt (Ursprung 0,0) wird als kleines Kreuz in der Mitte der Leinwand angezeigt. Klicken Sie auf die Schaltfläche "Zentrieren" in der Symbolleiste, um die Ansicht zum Ursprung zu verschieben.

---

## Anpassung

### Themen

BeatBoard bietet 9 verschiedene Themen:

**Helle Themen**:
- Hell (Standard)
- Solarized Light
- GitHub Light
- PaperColor

**Dunkle Themen**:
- Dunkel (Standard)
- Dracula
- Nord
- One Dark
- Material Dark

**Thema anwenden**:
1. Gehen Sie zu **Einstellungen > Thema**
2. Wählen Sie das gewünschte Thema
3. Sie können auch "System" wählen, um das Thema Ihres Betriebssystems zu verwenden

### Hintergrundfarbe der Leinwand

Sie können die Hintergrundfarbe der Leinwand anpassen:

1. Gehen Sie zu **Einstellungen > Hintergrundfarbe**
2. Wählen Sie aus:
   - Weiß
   - Hellgrau
   - Grau
   - Dunkelgrau
   - Creme
   - Dunkel
   - Schwarz
   - Benutzerdefiniert (wählen Sie Ihre eigene Farbe)

**Themenfarben zurücksetzen**:
- Wählen Sie "Themenfarben zurücksetzen", um zu den Standardfarben des aktuellen Themas zurückzukehren

### Standardwerte speichern

Aktivieren Sie die Option **"Größe und Farbe des letzten Beats merken"** in den Einstellungen, damit neue Beats die Größe und Farbe des zuletzt erstellten Beats erben.

### Sprache

BeatBoard ist in 4 Sprachen verfügbar:
- Englisch (English)
- Spanisch (Español)
- Französisch (Français)
- Deutsch

So ändern Sie die Sprache:
1. Gehen Sie zu **Einstellungen > Sprache**
2. Wählen Sie die gewünschte Sprache
3. Starten Sie die Anwendung neu, um die Änderung anzuwenden

### Rechtschreibprüfung

BeatBoard enthält eine integrierte Rechtschreibprüfung:

**Aktivieren**:
1. Gehen Sie zu **Einstellungen > Rechtschreibprüfung > Rechtschreibprüfung aktivieren**

**Wörterbuchsprache**:
1. Gehen Sie zu **Einstellungen > Rechtschreibprüfung > Wörterbuchsprache**
2. Wählen Sie die Sprache: Englisch, Spanisch, Französisch oder Deutsch

**Rechtschreibprüfung verwenden**:
- Falsche Wörter werden rot unterstrichen
- Klicken Sie mit der rechten Maustaste auf ein Wort, um Vorschläge zu sehen

---

## Export und Speichern

### Dateiformat

BeatBoard-Projekte werden im `.bbp`-Format (JSON) gespeichert. Dieses Format enthält:
- Alle Beats (Titel, Inhalt, Position, Größe, Farbe)
- Alle Verbindungen
- Leinwand-Einstellungen

### Projekt speichern

- **Speichern**: **Strg+S** (speichert in der aktuellen Datei)
- **Speichern unter**: **Strg+Umschalt+S** (wählt Speicherort und Namen)

### Als PDF exportieren

- In Entwicklung

### Als Text exportieren

1. Gehen Sie zu **Datei > Als Text exportieren**
2. Wählen Sie den Speicherort und den Namen für die Datei
3. Eine Textdatei mit allen Beats wird erstellt

### Zuletzt verwendete Dateien

BeatBoard führt eine Liste der zuletzt 10 geöffneten Dateien:

1. Gehen Sie zu **Datei > Zuletzt verwendet**
2. Wählen Sie die gewünschte Datei

Wenn eine Datei in der Liste nicht mehr existiert, werden Sie gefragt, ob Sie sie aus der Liste entfernen möchten.

### Automatisches Speichern

BeatBoard kann Ihr Projekt automatisch speichern:

1. Gehen Sie zu **Einstellungen > Backup-Optionen**
2. Konfigurieren Sie:
   - **Backup beim Öffnen**: Erstellt eine Kopie beim Öffnen des Projekts
   - **Automatisches Speichern**: Automatisches Speichern aktivieren/deaktivieren
   - **Intervall**: Wie oft speichern (1, 2, 5, 10, 15 oder 30 Minuten)
   - **Maximale Backups**: Anzahl der zu behaltenden Backups

---

## Tastenkürzel

### Datei

| Tastenkürzel | Funktion |
|--------------|----------|
| Strg+N | Neues Projekt |
| Strg+O | Projekt öffnen |
| Strg+S | Projekt speichern |
| Strg+Umschalt+S | Speichern unter |
| Strg+W | Projekt schließen |
| Strg+Q | Beenden |

### Bearbeiten

| Tastenkürzel | Funktion |
|--------------|----------|
| Strg+Z | Rückgängig |
| Strg+Y | Wiederholen |
| Strg+A | Alles auswählen |
| Strg+C | Kopieren |
| Strg+X | Ausschneiden |
| Strg+V | Einfügen |
| Entf | Auswahl löschen |
| Strg+Pos1 | In den Vordergrund bringen |
| Strg+Ende | In den Hintergrund senden |
| Strg+BildAuf | Nach oben |
| Strg+BildAb | Nach unten |

### Ansicht

| Tastenkürzel | Funktion |
|--------------|----------|
| Strg++ | Vergrößern |
| Strg+- | Verkleinern |
| Strg+0 | An Inhalt anpassen |
| Leertaste | Schiebemodus (gedrückt halten) |

### Sonstige Tastenkürzel

| Tastenkürzel | Funktion |
|--------------|----------|
| 1-0 | Farbe der Auswahl ändern |
| C | Verbindungsmodus umschalten (keine Auswahl) |
| Z | Auswahl-Zoom (keine Auswahl) |
| Esc | Abbrechen / Auswahl aufheben |
| Doppelklick (Leinwand) | Neuen Beat erstellen |
| Doppelklick (Beat) | Beat bearbeiten |

---

## Fehlerbehebung

### Das Programm startet nicht

1. Stellen Sie sicher, dass Python 3.10+ installiert ist
2. Stellen Sie sicher, dass Sie PySide6 installiert haben: `pip install pyside6`
3. Überprüfen Sie die Konsole auf Fehler

### Beats werden nicht gespeichert

1. Stellen Sie sicher, dass Sie Schreibrechte für den Ordner haben
2. Stellen Sie sicher, dass Sie das Projekt vor dem Schließen speichern (Strg+S)
3. Überprüfen Sie den Projektstatus in der Statusleiste (sollte "Gespeichert" sagen)

### Raster wird nicht angezeigt

1. Stellen Sie sicher, dass das Raster aktiviert ist: **Ansicht > Raster anzeigen**
2. Versuchen Sie, die Rasterfarbe in **Ansicht > Rasteroptionen** zu ändern

### Rechtschreibprüfung funktioniert nicht

1. Stellen Sie sicher, dass sie in **Einstellungen > Rechtschreibprüfung** aktiviert ist
2. Stellen Sie sicher, dass Sie die richtige Wörterbuchsprache ausgewählt haben

### Benutzerdefinierte Farben werden nicht gespeichert

1. Benutzerdefinierte Farben werden in den Einstellungen gespeichert, nicht im Projekt
2. Sie werden automatisch auf zukünftige Beats gemäß der Konfiguration angewendet

---

## Zusätzliche Informationen

### Maus-Kürzel

- **Doppelklick auf Leinwand**: Neuen Beat erstellen
- **Doppelklick auf Beat**: Beat bearbeiten
- **Einzelklick**: Element auswählen
- **Strg + Klick**: Zur Auswahl hinzufügen
- **Ziehen (Auswahl)**: Auswahlrechteck erstellen
- **Ziehen (Beat)**: Beat verschieben
- **Mausrad**: Zoom (mit gedrückter Strg-Taste)
- **Mittlere Maustaste**: Schwenken

### Glossar

- **Beat**: Einzelne Karte auf der Leinwand, die eine Szene oder einen Moment der Geschichte darstellt
- **Verbindung**: Gekrümmte Linie, die zwei Beats verbindet
- **Leinwand**: Der Arbeitsbereich, auf dem Beats platziert werden
- **Z-Reihenfolge**: Tiefe oder Ebene eines Elements (was über was erscheint)
- **Thema**: Farbsatz und Stile, die das Erscheinungsbild der Anwendung definieren
- **Eigenschaftenpanel**: Seitenleiste, in der die Eigenschaften des ausgewählten Elements bearbeitet werden

---

## Danksagung

BeatBoard wurde von CarlyMx erstellt und ist von Final Draft Beat Board inspiriert.

Weitere Informationen, Updates und Support finden Sie im GitHub-Repository.

---

*Handbuch erstellt für BeatBoard Version 1.0.27*
