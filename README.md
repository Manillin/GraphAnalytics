# Graph Analytics

Questo progetto utilizza un database Neo4j contenente dati di partite, giocatori e squadre NBA (stagioni 2015-2019) per condurre diverse analisi esplorative e specifiche. I dati sono stati originariamente importati da file CSV derivati da dataset pubblicamente disponibili (Kaggle: https://www.kaggle.com/datasets/nathanlauga/nba-games).

## Struttura del Repository

*   **`nba_dataset.ipynb`**: Notebook Jupyter principale che contiene le analisi dei dati NBA.
*   **`clean_data.ipynb`**: Notebook Jupyter utilizzato per la pulizia iniziale e la preparazione dei dati CSV prima dell'importazione in Neo4j.
*   **`schema.md`**: Descrive lo schema del database Neo4j (nodi, proprietà, relazioni).
*   **File CSV**: Dati puliti pronti per essere importati in Neo4j.

## Schema del Database Neo4j

Il database Neo4j è strutturato attorno a tre tipi principali di nodi:

*   **`:Team`**: Rappresenta una squadra NBA con proprietà come `teamId`, `nickname`, `city`, `yearFounded`, ecc.
*   **`:Player`**: Rappresenta un giocatore NBA con proprietà come `playerId` e `name`.
*   **`:Game`**: Rappresenta una singola partita NBA con proprietà come `gameId`, `date`, `season`, e statistiche di squadra per la partita (es. `ptsHome`, `fgPctAway`).

Le relazioni principali includono:

*   **`[:PLAYED_SEASON]`**: Tra `:Team` e `:Player`, indica la partecipazione di un giocatore a una squadra per una stagione.
*   **`[:HOSTED_GAME]` / `[:VISITED_GAME]`**: Tra `:Team` e `:Game`, indicano la squadra di casa e ospite per una partita.
*   **`[:PLAYED_IN_GAME]`**: Tra `:Player` e `:Game`, include le statistiche dettagliate di un giocatore per quella partita (punti, rimbalzi, assist, minuti giocati, ecc.).

Per i dettagli completi, si rimanda al file `schema.md`.

## Utilizzo dei Notebook

### 1. `clean_data.ipynb`

Questo notebook è responsabile delle seguenti operazioni:

*   Caricamento dei dataset NBA grezzi (presumibilmente da file CSV).
*   Pulizia dei dati: gestione dei valori mancanti, correzione dei tipi di dati, rimozione di dati irrilevanti o duplicati.
*   Trasformazione dei dati: ad esempio, conversione di formati di data, calcolo di nuove colonne se necessario.
*   Filtraggio dei dati per includere solo le stagioni rilevanti (2015-2019) e le partite di regular season/playoff.
*   Salvataggio dei dati puliti in nuovi file CSV (es. `games_filtered.csv`, `players_for_neo4j.csv`, ecc.) che sono poi utilizzati per popolare il database Neo4j.

**Nota**: L'esecuzione di questo notebook è un prerequisito per avere i dati pronti per l'importazione in Neo4j, c
### 2. `nba_dataset.ipynb`

Questo notebook si connette a un'istanza Neo4j già popolata con i dati NBA (utilizzando i dati prodotti da `clean_data.ipynb`). Contiene diverse analisi, tra cui:

*   **Connessione al Database**: Impostazione della connessione con il driver Neo4j.
*   **Analisi Esplorativa dei Dati (EDA) - Distribuzione dei Gradi**:
*   **Calcolo del Player Efficiency Rating Semplificato (uPER)**:
    *   Una metrica di performance individuale (`uPER_score`) viene calcolata per ogni giocatore basandosi sulle sue statistiche aggregate per minuto e salvata come proprietà del nodo `:Player`. Viene applicata una soglia minima di minuti giocati.
*   **Analisi dell'Influenza e Centralità dei Giocatori**:
    *   Vengono confrontate diverse metriche di centralità (Degree Centrality, PageRank) calcolate su un grafo di interazioni tra giocatori.
    *   Inizialmente, le interazioni sono pesate solo dal numero di partite condivise.
    *   Successivamente, il grafo viene modificato per pesare le interazioni in base sia al numero di partite condivise sia alla media degli `uPER_score` dei due giocatori interagenti.
    *   I risultati di queste diverse misure di centralità vengono analizzati per comprendere meglio differenti aspetti dell'"influenza" di un giocatore.
*   **Analisi degli Archetipi di Costruzione delle Squadre e Correlazione con il Successo**:
    *   Vengono definite feature a livello di squadra-stagione: `avg_uPER` (qualità media del roster) e `num_stars_uPER` (numero di giocatori stella, basato su una soglia di `uPER_score`).
    *   Viene utilizzato l'algoritmo K-Means per raggruppare le squadre-stagioni in archetipi basati su `avg_uPER` e `num_stars_uPER`.
    *   I cluster risultanti vengono analizzati in relazione al numero totale di vittorie (`total_wins`) per identificare strategie di costruzione del roster più o meno efficaci.

*   **Mobilità dei Giocatori**: 
    * Si identificheranno i giocatori che hanno militato nel maggior numero di squadre diverse e quelli che sono rimasti affiliati a una singola squadra durante l'arco temporale considerato
    * Per entrambi i gruppi, analizzeremo la loro performance individuale, misurata tramite il `uPER_score` (Player Efficiency Rating Semplificato e Normalizzato), per investigare se esiste una correlazione tra la tendenza a cambiare squadra e il livello di performance.

**Prerequisiti per `nba_dataset.ipynb`**:
*   Avere un'istanza Neo4j attiva e accessibile.
*   Il database Neo4j deve essere stato popolato con i dati NBA seguendo lo schema definito (presumibilmente utilizzando i CSV generati da `clean_data.ipynb`).
*   Le librerie Python necessarie devono essere installate (pandas, matplotlib, neo4j, sklearn, ecc.).

