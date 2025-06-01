# Schema del Database Neo4j per l'Analisi NBA

Questo documento descrive la struttura del database Neo4j creato per l'analisi delle partite NBA, includendo i tipi di nodi, le loro proprietà, i tipi di relazioni e le loro proprietà.

## 1. Nodi (Labels)

### 1.1. `:Team`
Rappresenta una squadra NBA.

*   **Proprietà:**
    *   `teamId`: `INTEGER` (Chiave primaria, identificatore univoco dal CSV `teams_for_neo4j.csv`. Esempio: `1610612739`)
    *   `abbreviation`: `STRING` (Abbreviazione della squadra. Esempio: `"CLE"`)
    *   `nickname`: `STRING` (Nickname della squadra. Esempio: `"Cavaliers"`)
    *   `yearFounded`: `INTEGER` (Anno di fondazione. Esempio: `1970`)
    *   `city`: `STRING` (Città della squadra. Esempio: `"Cleveland"`)
    *   `arena`: `STRING` (Nome dell'arena. Esempio: `"Rocket Mortgage FieldHouse"`)
    *   `owner`: `STRING` (Proprietario della squadra. Esempio: `"Dan Gilbert"`)
    *   `generalManager`: `STRING` (General Manager. Esempio: `"Koby Altman"`)
    *   `headCoach`: `STRING` (Allenatore capo. Esempio: `"J.B. Bickerstaff"`)
    *   `dLeagueAffiliation`: `STRING` (Affiliazione alla D-League/G-League. Esempio: `"Cleveland Charge"`)
    *   `leagueId`: `INTEGER` (ID della lega, probabilmente costante per l'NBA. Esempio: `0`)
    *   `minYear`: `INTEGER` (Anno minimo di attività registrato nel file `teams.csv`)
    *   `maxYear`: `INTEGER` (Anno massimo di attività registrato nel file `teams.csv`)
*   **Constraint:** `UNIQUE` su `teamId`.

### 1.2. `:Player`
Rappresenta un giocatore NBA.

*   **Proprietà:**
    *   `playerId`: `INTEGER` (Chiave primaria, identificatore univoco dal CSV `players_for_neo4j.csv`. Esempio: `201939`)
    *   `name`: `STRING` (Nome completo del giocatore. Esempio: `"Stephen Curry"`)
*   **Constraint:** `UNIQUE` su `playerId`.

### 1.3. `:Game`
Rappresenta una singola partita NBA.

*   **Proprietà:**
    *   `gameId`: `INTEGER` (Chiave primaria, identificatore univoco dal CSV `games_filtered.csv`. Esempio: `21900001`)
    *   `date`: `DATE` (Data della partita. Formato: `YYYY-MM-DD`. Derivata da `GAME_DATE_EST`)
    *   `season`: `INTEGER` (Stagione della partita, es. `2019` per la stagione 2019-2020)
    *   `statusText`: `STRING` (Stato della partita. Esempio: `"Final"`)
    *   `ptsHome`: `FLOAT` (Punti segnati dalla squadra di casa)
    *   `fgPctHome`: `FLOAT` (Percentuale dal campo della squadra di casa)
    *   `ftPctHome`: `FLOAT` (Percentuale ai tiri liberi della squadra di casa)
    *   `fg3PctHome`: `FLOAT` (Percentuale da tre punti della squadra di casa)
    *   `astHome`: `FLOAT` (Assist della squadra di casa)
    *   `rebHome`: `FLOAT` (Rimbalzi della squadra di casa)
    *   `ptsAway`: `FLOAT` (Punti segnati dalla squadra ospite)
    *   `fgPctAway`: `FLOAT` (Percentuale dal campo della squadra ospite)
    *   `ftPctAway`: `FLOAT` (Percentuale ai tiri liberi della squadra ospite)
    *   `fg3PctAway`: `FLOAT` (Percentuale da tre punti della squadra ospite)
    *   `astAway`: `FLOAT` (Assist della squadra ospite)
    *   `rebAway`: `FLOAT` (Rimbalzi della squadra ospite)
    *   `homeTeamWins`: `INTEGER` (1 se la squadra di casa ha vinto, 0 se la squadra ospite ha vinto)
*   **Constraint:** `UNIQUE` su `gameId`.

## 2. Relazioni (Types)

### 2.1. `(t:Team)-[ps:PLAYED_SEASON]->(p:Player)`
Indica che un giocatore ha fatto parte di una squadra per una specifica stagione.

*   **Direzione:** Dal `:Team` al `:Player`.
*   **Creata da:** `players_for_neo4j.csv`.
*   **Proprietà sulla relazione `ps`:**
    *   `season`: `INTEGER` (La stagione in cui il giocatore ha giocato per quella squadra. Esempio: `2019`)

### 2.2. `(ht:Team)-[:HOSTED_GAME]->(g:Game)`
Collega la squadra di casa (`ht`) a una partita (`g`) che ha ospitato.

*   **Direzione:** Dal `:Team` (squadra di casa) al `:Game`.
*   **Creata da:** `games_filtered.csv` (utilizzando `HOME_TEAM_ID`).
*   **Proprietà:** Nessuna proprietà specifica su questa relazione.

### 2.3. `(vt:Team)-[:VISITED_GAME]->(g:Game)`
Collega la squadra ospite (`vt`) a una partita (`g`) a cui ha partecipato come visitatore.

*   **Direzione:** Dal `:Team` (squadra ospite) al `:Game`.
*   **Creata da:** `games_filtered.csv` (utilizzando `VISITOR_TEAM_ID`).
*   **Proprietà:** Nessuna proprietà specifica su questa relazione.

### 2.4. `(p:Player)-[played_in:PLAYED_IN_GAME]->(g:Game)`
Rappresenta la partecipazione e le statistiche di un giocatore in una specifica partita.

*   **Direzione:** Dal `:Player` al `:Game`.
*   **Creata da:** `games_details_filtered.csv`.
*   **Proprietà sulla relazione `played_in`:**
    *   `teamId`: `INTEGER` (ID della squadra per cui il giocatore ha giocato in quella partita)
    *   `teamAbbreviation`: `STRING` (Abbreviazione della squadra del giocatore in quella partita)
    *   `teamCity`: `STRING` (Città della squadra del giocatore in quella partita)
    *   `startPosition`: `STRING` (Posizione di partenza del giocatore, es. `"F"`, `"G"`, `"C"`. Può essere `null` o una stringa vuota se non titolare o non specificato)
    *   `comment`: `STRING` (Eventuali commenti sulla partecipazione, es. `"DNP - Coach's Decision"`. Può essere `null` o una stringa vuota)
    *   `minutesPlayed`: `INTEGER` (Minuti giocati in secondi. Convertito da "MM:SS" a secondi interi)
    *   `points`: `FLOAT` (Punti segnati dal giocatore. Nome CSV: `PTS`)
    *   `rebounds`: `FLOAT` (Rimbalzi totali del giocatore. Nome CSV: `REB`)
    *   `assists`: `FLOAT` (Assist del giocatore. Nome CSV: `AST`)
    *   `steals`: `FLOAT` (Palle rubate dal giocatore. Nome CSV: `STL`)
    *   `blocks`: `FLOAT` (Stoppate effettuate dal giocatore. Nome CSV: `BLK`)
    *   `turnovers`: `FLOAT` (Palle perse dal giocatore. Nome CSV: `TO`)
    *   `personalFouls`: `FLOAT` (Falli personali commessi. Nome CSV: `PF`)
    *   `FGM`: `FLOAT` (Tiri dal campo realizzati)
    *   `FGA`: `FLOAT` (Tiri dal campo tentati)
    *   `FG_PCT`: `FLOAT` (Percentuale tiri dal campo)
    *   `FG3M`: `FLOAT` (Tiri da tre punti realizzati)
    *   `FG3A`: `FLOAT` (Tiri da tre punti tentati)
    *   `FG3_PCT`: `FLOAT` (Percentuale tiri da tre punti)
    *   `FTM`: `FLOAT` (Tiri liberi realizzati)
    *   `FTA`: `FLOAT` (Tiri liberi tentati)
    *   `FT_PCT`: `FLOAT` (Percentuale tiri liberi)
    *   `OREB`: `FLOAT` (Rimbalzi offensivi)
    *   `DREB`: `FLOAT` (Rimbalzi difensivi)
    *   `plusMinus`: `FLOAT` (Statistica Plus/Minus. Nome CSV: `PLUS_MINUS`)

## 3. Constraints Definiti

Per garantire l'integrità dei dati e ottimizzare le query, sono stati definiti i seguenti constraint di unicità:

*   `CREATE CONSTRAINT unique_team_id IF NOT EXISTS FOR (t:Team) REQUIRE t.teamId IS UNIQUE;`
*   `CREATE CONSTRAINT unique_player_id IF NOT EXISTS FOR (p:Player) REQUIRE p.playerId IS UNIQUE;`
*   `CREATE CONSTRAINT unique_game_id IF NOT EXISTS FOR (g:Game) REQUIRE g.gameId IS UNIQUE;`

Questo schema dovrebbe rappresentare fedelmente la struttura del database Neo4j che abbiamo costruito.