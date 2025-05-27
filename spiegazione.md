# Progetto di Graph Analytics: Analisi di Dati NBA

## 1. Introduzione e Scelta del Dataset

Il presente progetto si focalizza sull'applicazione di tecniche di Graph Analytics per esplorare e comprendere le dinamiche interne al mondo del basket professionistico americano (NBA). L'obiettivo primario è la costruzione di un database a grafo rappresentativo delle entità chiave (squadre, giocatori, partite) e delle loro interconnessioni, al fine di porre le basi per analisi complesse e la formulazione di research questions specifiche.

Per tale scopo, è stato selezionato un dataset pubblico reperibile sulla piattaforma Kaggle, denominato "NBA Games". Questo dataset comprende diverse tabelle CSV contenenti informazioni dettagliate su partite, statistiche dei giocatori, squadre e classifiche relative a numerose stagioni NBA.

## 2. Preparazione e Pulizia dei Dati

Prima di procedere alla costruzione del grafo, si è resa necessaria un'accurata fase di preparazione, pulizia e filtraggio dei dati. Queste operazioni sono state condotte utilizzando Python, con il supporto principale della libreria Pandas per la manipolazione dei DataFrame.

### 2.1 Filtraggio Temporale

Per concentrare l'analisi su un periodo specifico e gestibile, si è deciso di filtrare i dati per includere esclusivamente le stagioni NBA comprese tra il 2015 e il 2019 (inclusive). Questo filtraggio è stato applicato ai file CSV principali che contengono riferimenti stagionali, come `games.csv` (informazioni generali sulle partite) e `games_details.csv` (statistiche dettagliate dei giocatori per partita).

Ad esempio, per il file `games.csv`, il filtraggio è stato eseguito selezionando le righe la cui colonna `SEASON` rientrava nell'intervallo desiderato:

```python
# Esempio di codice Pandas per il filtraggio stagionale
start_season = 2015
end_season = 2019
games_df_filtered = games_df[(games_df['SEASON'] >= start_season) & (games_df['SEASON'] <= end_season)]
```

Da questo DataFrame filtrato, sono stati estratti gli identificativi unici delle partite (`GAME_ID`) per garantire che anche i dati di dettaglio (`games_details.csv`) fossero coerentemente limitati allo stesso periodo.

### 2.2 Analisi e Gestione dei Dati dei Giocatori

Il file contenente le informazioni anagrafiche dei giocatori (convenzionalmente `players.csv`) presentava una struttura in cui un giocatore poteva apparire più volte, tipicamente una volta per ogni combinazione stagione/squadra a cui era associato. Per la modellazione del grafo, tuttavia, si è stabilito di creare un nodo univoco per ciascun giocatore, identificato dal suo `PLAYER_ID`. Le informazioni contestuali relative alla squadra e alla stagione di appartenenza di un giocatore in un dato momento sono state demandate alla modellazione delle relazioni (descritte più avanti), piuttosto che essere attributi diretti del nodo `:Player`. Pertanto, durante l'importazione dei nodi `:Player` in Neo4j, le colonne `TEAM_ID` e `SEASON` presenti in questo specifico file sono state ignorate per la definizione delle proprietà del nodo giocatore.

### 2.3 Analisi e Pre-processamento dei Dettagli delle Partite

Il file `games_details.csv` (o la sua versione filtrata, `games_details_filtered.csv`), contenente le statistiche di ogni giocatore per ogni partita, ha richiesto particolare attenzione.

L'analisi preliminare ha rivelato la presenza di valori nulli in diverse colonne:
*   `NICKNAME`: Risultata completamente nulla per l'intervallo di stagioni considerato.
*   `START_POSITION`: Null per i giocatori partiti dalla panchina.
*   `COMMENT`: Null se non vi erano annotazioni specifiche (es. DNP - Did Not Play).
*   Colonne statistiche (es. `FGM`, `PTS`, `AST`, `REB`, `MIN`): Null per i giocatori registrati a referto ma non scesi in campo (DNP).

Si è deciso di escludere la colonna `NICKNAME` dall'importazione. Per le statistiche numeriche dei giocatori DNP, si è optato per una gestione che assegna il valore `0` (o `0.0`) in fase di importazione nel grafo, per mantenere la consistenza numerica delle proprietà.

#### 2.3.1 Gestione Colonna Minuti Giocati (`MIN`)

La colonna `MIN`, rappresentante i minuti giocati, si presentava in formato stringa "MM:SS" (es. "12:34") ed era di tipo `object` nel DataFrame Pandas. Questo formato non è direttamente utilizzabile per calcoli numerici o per un'agevole importazione in Neo4j come tipo numerico.

Pertanto, si è proceduto a un pre-processamento di questa colonna in Pandas per convertirla in un valore numerico intero rappresentante i **secondi totali giocati**. Questa scelta garantisce la massima precisione per analisi future. È stata creata una nuova colonna, `MIN_SECONDS`. I valori `NaN` originali (corrispondenti ai giocatori DNP) in questa nuova colonna sono stati sostituiti con `0`.

```python
# Esempio concettuale della funzione di conversione in Pandas
def convert_min_to_seconds(time_str):
    if pd.isna(time_str):
        return 0 # O np.nan se si preferisce gestire i nulli diversamente prima del fillna
    try:
        parts = str(time_str).split(':')
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = int(parts[1])
            return (minutes * 60) + seconds
        # Altre logiche per formati imprevisti o già numerici
        return 0 # Valore di fallback
    except ValueError:
        return 0 # Valore di fallback

# Applicazione
games_details_filtered_df['MIN_SECONDS'] = games_details_filtered_df['MIN'].apply(convert_min_to_seconds)
```

### 2.4 Esclusione Colonne Specifiche e Salvataggio Dati Processati

Oltre a `NICKNAME`, si è deciso di non caricare la colonna `ARENACAPACITY` dal file delle squadre, come da specifiche iniziali del progetto.
Tutti i DataFrame Pandas, una volta filtrati e pre-processati (in particolare `games_details_filtered.csv` con la nuova colonna `MIN_SECONDS`), sono stati salvati come nuovi file CSV, pronti per la fase di importazione nel database a grafo.

## 3. Costruzione del Database a Grafo in Neo4j

La fase successiva ha riguardato la creazione e il popolamento del database a grafo utilizzando Neo4j.

### 3.1 Configurazione dell'Ambiente Neo4j

È stato utilizzato Neo4j Desktop per la gestione locale dell'ambiente. All'interno di un progetto dedicato ("GraphAnalyticsNBA"), è stato creato un nuovo database DBMS, a cui è stato assegnato il nome `nba`. Successivamente, è stata installata la libreria Graph Data Science (GDS) come plugin per questo database, in previsione delle analisi grafiche avanzate. La connessione al database da script Python è stata gestita tramite la libreria ufficiale `neo4j`.

### 3.2 Definizione dello Schema del Grafo

Prima dell'importazione, è stato definito uno schema concettuale per il grafo, identificando le principali entità e le loro relazioni:

*   **Nodi:**
    *   `:Team`: Rappresenta una squadra NBA (es. proprietà: `teamId`, `nickname`, `city`).
    *   `:Player`: Rappresenta un giocatore (es. proprietà: `playerId`, `name`).
    *   `:Game`: Rappresenta una singola partita (es. proprietà: `gameId`, `date`, `season`, punteggi).
*   **Relazioni:**
    *   `[:HOSTED_GAME]`: Collega un nodo `:Team` (squadra di casa) a un nodo `:Game`.
    *   `[:VISITED_GAME]`: Collega un nodo `:Team` (squadra ospite) a un nodo `:Game`.
    *   `[:PLAYED_IN_GAME]`: Collega un nodo `:Player` a un nodo `:Game`. Questa relazione è arricchita con proprietà che descrivono la performance del giocatore in quella partita (es. `points`, `rebounds`, `assists`, `minutesPlayed`, `teamId` per cui ha giocato).

### 3.3 Creazione dei Vincoli (Constraints)

Per garantire l'integrità dei dati e ottimizzare le prestazioni durante l'importazione (specialmente per le operazioni di `MERGE`), sono stati creati dei vincoli di unicità (constraints) sulle proprietà identificative dei nodi principali:

*   `CONSTRAINT ON (t:Team) ASSERT t.teamId IS UNIQUE`
*   `CONSTRAINT ON (p:Player) ASSERT p.playerId IS UNIQUE`
*   `CONSTRAINT ON (g:Game) ASSERT g.gameId IS UNIQUE`

Questi comandi sono stati eseguiti una tantum tramite query Cypher da Python.

### 3.4 Processo di Importazione dei Dati

L'importazione dei dati dai file CSV processati è avvenuta in modo incrementale, utilizzando il comando Cypher `LOAD CSV`. Per un corretto funzionamento, i file CSV sono stati preventivamente copiati nella sottocartella `import` della directory del database `nba` gestito da Neo4j Desktop.

#### 3.4.1 Importazione Nodi Squadra (`:Team`)

Dal file `teams_for_neo4j.csv`, sono stati creati i nodi `:Team`. Ogni riga del CSV ha portato alla creazione (o all'aggiornamento, grazie a `MERGE`) di un nodo `:Team`, utilizzando `TEAM_ID` come chiave univoca. Le altre colonne del CSV (eccetto `ARENACAPACITY`) sono diventate proprietà del nodo.

```cypher
// Frammento concettuale della query di importazione per i Team
LOAD CSV WITH HEADERS FROM 'file:///teams_for_neo4j.csv' AS row
MERGE (t:Team {teamId: toInteger(row.TEAM_ID)})
ON CREATE SET
    t.nickname = row.NICKNAME,
    t.city = row.CITY,
    // ... altre proprietà
ON MATCH SET // Opzionale: per aggiornare se il nodo esiste già
    t.nickname = row.NICKNAME,
    // ... altre proprietà
```

#### 3.4.2 Importazione Nodi Giocatore (`:Player`)

Successivamente, dal file `players_for_neo4j.csv`, sono stati importati i nodi `:Player`. Nonostante il file CSV potesse contenere più righe per lo stesso giocatore (relative a diverse stagioni/squadre), l'utilizzo di `MERGE (p:Player {playerId: toInteger(row.PLAYER_ID)})` ha garantito la creazione di un unico nodo `:Player` per ogni `PLAYER_ID` distintivo. La proprietà `name` è stata impostata con il valore di `PLAYER_NAME` dal CSV. Le colonne `TEAM_ID` e `SEASON` di questo file sono state ignorate per la definizione del nodo `:Player`.

#### 3.4.3 Importazione Nodi Partita (`:Game`) e Relative Connessioni alle Squadre

Il file `games_filtered.csv` è stato utilizzato per creare i nodi `:Game`. Per ogni riga:
1.  Sono stati cercati (tramite `MATCH`) i nodi `:Team` esistenti per la squadra di casa (`HOME_TEAM_ID`) e la squadra ospite (`VISITOR_TEAM_ID`).
2.  È stato creato (tramite `MERGE`) un nodo `:Game` utilizzando `GAME_ID` come chiave. Le proprietà del gioco (data, stagione, punteggi, esito) sono state popolate dalle rispettive colonne del CSV. La colonna `GAME_DATE_EST` è stata convertita in un tipo `date` di Neo4j e `HOME_TEAM_WINS` in un tipo `boolean`.
3.  Sono state create le relazioni `(homeTeam)-[:HOSTED_GAME]->(gameNode)` e `(visitorTeam)-[:VISITED_GAME]->(gameNode)`.

```cypher
// Frammento concettuale della query di importazione per Game e relazioni Team-Game
LOAD CSV WITH HEADERS FROM 'file:///games_filtered.csv' AS row
MATCH (homeTeam:Team {teamId: toInteger(row.HOME_TEAM_ID)})
MATCH (visitorTeam:Team {teamId: toInteger(row.VISITOR_TEAM_ID)})
MERGE (g:Game {gameId: toInteger(row.GAME_ID)})
ON CREATE SET
    g.date = date(row.GAME_DATE_EST),
    g.homeTeamWins = (toInteger(row.HOME_TEAM_WINS) = 1)
    // ... altre proprietà del gioco
MERGE (homeTeam)-[:HOSTED_GAME]->(g)
MERGE (visitorTeam)-[:VISITED_GAME]->(g)
```

#### 3.4.4 Importazione Performance dei Giocatori (Relazioni `:PLAYED_IN_GAME`)

Infine, il file più dettagliato, `games_details_for_neo4j_processed.csv` (contenente la colonna `MIN_SECONDS` pre-processata), è stato utilizzato per creare le relazioni `:PLAYED_IN_GAME`. Per ogni riga:
1.  Sono stati cercati i nodi `:Player` e `:Game` corrispondenti tramite `PLAYER_ID` e `GAME_ID`.
2.  È stata creata (tramite `MERGE`) una relazione `(player)-[played_in:PLAYED_IN_GAME]->(game)`.
3.  Tutte le statistiche individuali del giocatore per quella partita (`MIN_SECONDS` come `minutesPlayed`, `PTS` come `points`, `AST` come `ast`, `REB` come `reb`, ecc.), il `TEAM_ID` per cui ha giocato, e altre informazioni contestuali come `START_POSITION` e `COMMENT` (se presenti) sono state impostate come proprietà della relazione `played_in`. La colonna `NICKNAME` è stata esclusa. I valori nulli per le statistiche sono stati gestiti con `coalesce(toFloat(row.STAT_COLUMN), 0.0)` per impostarli a `0.0`.

```cypher
// Frammento concettuale della query di importazione per le performance dei giocatori
LOAD CSV WITH HEADERS FROM 'file:///games_details_for_neo4j_processed.csv' AS row
MATCH (p:Player {playerId: toInteger(row.PLAYER_ID)})
MATCH (g:Game {gameId: toInteger(row.GAME_ID)})
MERGE (p)-[played_in:PLAYED_IN_GAME]->(g)
ON CREATE SET
    played_in.teamId = toInteger(row.TEAM_ID),
    played_in.minutesPlayed = toInteger(row.MIN_SECONDS),
    played_in.points = coalesce(toFloat(row.PTS), 0.0),
    played_in.ast = coalesce(toFloat(row.AST), 0.0),
    played_in.reb = coalesce(toFloat(row.REB), 0.0)
    // ... tutte le altre statistiche come proprietà della relazione
```

## 4. Stato Attuale del Database e Passi Successivi

Al termine di queste fasi di importazione, il database Neo4j `nba` contiene una rappresentazione strutturata delle squadre, dei giocatori e delle partite per le stagioni 2015-2019, incluse le performance dettagliate dei giocatori in ciascun incontro. La struttura del grafo è ora considerata completa per quanto riguarda i dati di base.

I passi successivi consisteranno nella formulazione e nell'esplorazione di specifiche research questions, utilizzando query Cypher e gli algoritmi disponibili nella libreria Graph Data Science (GDS) per analizzare il grafo e derivare insight significativi.