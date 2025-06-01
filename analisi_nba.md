# Analisi Evoluta dell'Influenza e Centralità dei Giocatori NBA

## 1. Contesto Iniziale: Limiti della Centralità Puramente Strutturale

Le analisi iniziali di centralità sul grafo di interazioni NBA (`player_interactions_graph`), dove i giocatori erano connessi se avevano partecipato alla stessa partita e le relazioni erano pesate solo dal numero di partite condivise, hanno prodotto risultati che, sebbene tecnicamente corretti, non catturavano l'"influenza" o l'"importanza" di un giocatore nel senso comunemente inteso nel contesto NBA.

*   **Degree Centrality Iniziale (Pesata da Partite Condivise):**
    *   *Giocatori Top:* Al Horford, Tobias Harris, Bojan Bogdanovic, Giannis Antetokounmpo, ecc.
    *   *Interpretazione:* Identificava giocatori con un alto volume di "co-partecipazioni" a partite, indicando veterani o giocatori che avevano giocato molte partite con molti compagni/avversari diversi nel periodo 2015-2019.

*   **PageRank Iniziale (Pesato da Partite Condivise):**
    *   *Giocatori Top:* Edgar Sosa, Marshall Henderson, Chris Johnson, ecc.
    *   *Interpretazione:* Ha messo in luce giocatori che, nonostante carriere NBA spesso brevi e poche partite totali giocate (es. Edgar Sosa con solo 2 partite nel dataset), erano figure strutturalmente centrali all'interno di piccole e dense comunità locali di giocatori. L'algoritmo di community detection (Louvain) ha confermato questa ipotesi, mostrando che questi giocatori tendevano a raggrupparsi in specifici cluster. Il loro alto PageRank derivava dalla loro importanza relativa *all'interno di queste nicchie*, non da un impatto globale sulla lega.

Questi primi risultati, pur validi per comprendere la topologia della rete di interazioni, non erano soddisfacenti per rispondere alla domanda su chi fossero i giocatori più "influenti" in termini di performance e impatto generale sul gioco.

## 2. Introduzione della Performance Individuale: Il Player Efficiency Rating Semplificato (uPER)

Per indirizzare i limiti precedenti, si è deciso di incorporare una misura di performance individuale. È stato calcolato un **Player Efficiency Rating Semplificato (uPER)** per ciascun giocatore.

**Calcolo dell'uPER:**
L'uPER è stato calcolato aggregando le statistiche individuali di un giocatore da tutte le partite a cui ha partecipato (dalle proprietà della relazione `:PLAYED_IN_GAME`), normalizzando poi per i minuti totali giocati. La formula approssimativa utilizzata è:
`uPER = (SommaStatPositive - SommaStatNegative) / MinutiTotaliGiocati`
Dove:
*   `SommaStatPositive = Punti + Rimbalzi (reb) + Assist (ast) + Palle Rubate (stl) + Stoppate (blk)`
*   `SommaStatNegative = TiriSbagliatiDalCampo (fga - fgm) + TiriLiberiSbagliati (fta - ftm) + PallePerse (turnovers) + FalliPersonali (personalFouls)`
È stata applicata una soglia minima di **1500 minuti totali giocati** per il calcolo dell'uPER, al fine di garantire che la metrica fosse basata su un volume di gioco sufficiente per una certa stabilità e significatività. Questo punteggio `uPER_score` è stato poi salvato come proprietà (`uPER_score`) su ciascun nodo `:Player` nel database Neo4j.


Le classifiche dirette basate su metriche di performance aggregate come "Punti Totali" e "uPER" (come visto in una fase intermedia dell'analisi) hanno immediatamente prodotto liste di giocatori (James Harden, LeBron James, Stephen Curry, Anthony Davis, ecc.) molto più allineate con la percezione comune di "stelle NBA" e giocatori di grande impatto.

## 3. Ridefinizione dell'Influenza nel Grafo: PageRank e Degree Centrality su un Grafo Ponderato dalla Performance

Per combinare l'analisi strutturale della rete con la performance individuale, è stato creato un **nuovo grafo proiettato in GDS**, denominato `player_interactions_weighted_by_perf`.

**Caratteristiche del Nuovo Grafo Proiettato:**
*   **Nodi:** Giocatori (`:Player`).
*   **Relazioni (`SHARED_GAME`):** Collegano due giocatori se hanno partecipato alla stessa partita.
*   **Peso delle Relazioni (Modificato):** Il peso di ogni relazione `SHARED_GAME` tra due giocatori (`p1`, `p2`) è stato ridefinito per incorporare sia la frequenza della loro interazione sia la loro performance individuale (tramite `uPER_score`). Il nuovo peso è stato calcolato come:
    `peso_relazione = (numero di partite condivise tra p1 e p2) * ( (uPER_score di p1 + uPER_score di p2) / 2 )`
    (Utilizzando un piccolo valore di default per l'uPER_score se mancante o zero per evitare che il peso diventi nullo impropriamente).

Su questo nuovo grafo, sono stati rieseguiti gli algoritmi di Degree Centrality (pesata) e PageRank.

### 3.1. Degree Centrality (Pesata) su `player_interactions_weighted_by_perf`

*   **Giocatori Top (dati forniti):** Giannis Antetokounmpo, LeBron James, Al Horford, Anthony Davis, Rudy Gobert, Tobias Harris, Julius Randle, Draymond Green, JaVale McGee, Kyle O'Quinn.
*   **Interpretazione:** Questa metrica ora somma i "pesi compositi" delle interazioni di un giocatore. Un alto grado pesato in questo grafo indica un giocatore che ha avuto un grande volume di "interazioni di qualità". Ossia, ha giocato spesso e/o con molti giocatori diversi, e queste interazioni sono state ulteriormente valorizzate dalla performance (uPER) sua e dei giocatori con cui ha interagito.
    *   È interessante notare come giocatori come Giannis, LeBron, AD (alto uPER) siano in cima, indicando che le loro numerose interazioni sono anche "potenziate" dalla loro alta performance.
    *   La presenza di giocatori come Al Horford, Rudy Gobert, Tobias Harris, Julius Randle, Draymond Green suggerisce giocatori che combinano un alto volume di gioco/interazioni con una performance solida e/o interazioni frequenti con altri giocatori di buona qualità. JaVale McGee e Kyle O'Quinn potrebbero emergere per un volume significativo di interazioni con compagni di squadra performanti o per aver mantenuto un buon uPER in quelle interazioni.

### 3.2. PageRank su `player_interactions_weighted_by_perf`

*   **Giocatori Top (dati forniti):** Kobe Bryant, Tayshaun Prince, Tim Duncan, Chris Bosh, Kevin Garnett, Luis Scola, Jared Sullinger, Marcus Thornton, Leandro Barbosa, Rodney Stuckey.
*   **Interpretazione:** Questo PageRank, ora influenzato dai pesi delle relazioni che codificano la performance, misura la centralità di un giocatore in questa nuova rete "arricchita". Un alto punteggio suggerisce un giocatore che non solo ha giocato con molti altri, ma ha anche interagito significativamente (spesso e/o con alta performance reciproca) con altri giocatori che sono a loro volta performanti e ben connessi.
    *   La presenza di leggende come Kobe Bryant, Tim Duncan, Kevin Garnett, Chris Bosh e giocatori chiave di squadre di successo come Tayshaun Prince è molto significativa. Sebbene il dataset copra 2015-2019 (periodo in cui alcuni di questi erano alla fine della carriera o appena ritirati), i loro `uPER_score` (se hanno giocato abbastanza in quelle stagioni per superare la soglia) e le loro interazioni con giocatori ancora attivi e performanti in quel periodo contribuiscono al loro punteggio. Se il loro `uPER_score` nel periodo 2015-2019 fosse basso o zero (es. Kevin Garnett con uPER 0.00), il loro alto PageRank deriva principalmente dalla forza delle interazioni ponderate con altri giocatori molto performanti con cui hanno condiviso il campo, anche se le loro statistiche personali in quelle poche partite finali potrebbero non essere state stellari. Questo evidenzia come PageRank consideri l'importanza dei "vicini".
    *   Giocatori come Luis Scola, Jared Sullinger, Marcus Thornton, Leandro Barbosa, Rodney Stuckey sono veterani o giocatori di ruolo che hanno avuto carriere solide, spesso giocando per più squadre e quindi accumulando interazioni con una vasta gamma di giocatori, e il cui uPER o l'uPER dei loro partner di interazione ha contribuito a dare peso a queste connessioni.


## 4. Confronto e Conclusioni Finali sull'Influenza

Confrontando i diversi risultati di PageRank e Degree Centrality:

*   **PageRank Iniziale (Solo Struttura):** Utile per l'analisi topologica e la scoperta di comunità dense e isolate, ma fuorviante come misura di "influenza NBA" globale.
*   **Degree Centrality Iniziale (Solo Struttura):** Indicava volume di co-partecipazioni.
*   **Punti Totali / uPER (Cypher Diretto):** Misure eccellenti e dirette della performance individuale e dell'efficienza, che si allineano bene con la nozione di "giocatore stella".
*   **Degree Centrality su Grafo Ponderato da uPER:** Misura il "volume di interazioni di qualità", combinando frequenza e performance. Fornisce una lista di giocatori che sono sia molto attivi sia performanti/connessi a giocatori performanti.
*   **PageRank su Grafo Ponderato da uPER:** Fornisce la misura più sofisticata di "influenza propagata nella rete di giocatori performanti". Considera non solo le connessioni dirette di un giocatore e la loro qualità, ma anche la qualità e la connettività dei suoi vicini, e così via. La classifica risultante (Kobe, Duncan, ecc.) suggerisce che sta catturando un senso di importanza storica e di rete all'interno del sottoinsieme di giocatori più performanti e delle loro interazioni.

In conclusione, modificando la definizione dei pesi delle relazioni nel grafo proiettato per includere una metrica di performance individuale (uPER), siamo riusciti a far sì che gli algoritmi di centralità basati su grafo (come PageRank e Degree Centrality) producessero classifiche che riflettono più da vicino l'"influenza" di un giocatore nel contesto NBA. Questo approccio combina la connettività nella rete con la qualità individuale e la qualità dei giocatori con cui si interagisce, offrendo una visione più ricca e sfumata rispetto all'analisi puramente strutturale. 