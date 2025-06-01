# Analisi RQ2: Archetipi di Costruzione delle Squadre NBA e Correlazione con il Successo

## 1. Obiettivo della Research Question (RQ2)

L'obiettivo di questa seconda analisi era investigare come differenti archetipi di costruzione delle squadre NBA, definiti in base alla qualità media dei giocatori e alla presenza di "stelle", si correlano con il successo della squadra, misurato in termini di numero totale di vittorie in una stagione (come rappresentato nel dataset).

## 2. Feature Engineering per Squadra-Stagione

Per caratterizzare ogni squadra in ogni stagione considerata (2015-2019), sono state definite e calcolate le seguenti feature a livello di squadra-stagione:

*   **`avg_uPER`**: La media del Player Efficiency Rating Semplificato (uPER) di tutti i giocatori che hanno giocato per una squadra in una data stagione e che avevano un `uPER_score` calcolato e positivo. Questa metrica rappresenta la "qualità media" del talento a disposizione della squadra.
*   **`num_stars_uPER`**: Il numero di giocatori in una squadra, per una data stagione, il cui `uPER_score` superava una soglia predefinita (`UPER_STAR_THRESHOLD = 0.60`). Questa metrica quantifica la presenza di giocatori d'élite o "stelle".
*   **`total_wins`**: Il numero totale di partite vinte da una squadra in una data stagione, considerando tutte le partite presenti nel dataset per quella `SEASON` (che include regular season e potenzialmente pre-stagione e playoff). Questo calcolo ha richiesto un'attenta verifica dello schema del database, in particolare della proprietà `homeTeamWins` (risultata essere booleana `true`/`false`) e del corretto collegamento tra giocatori, squadre e partite per stagione.


## 3. Analisi Esplorativa dei Dati (EDA) delle Feature Calcolate

Una volta ottenuto il DataFrame `df_team_season_features` contenente queste tre metriche per 150 combinazioni squadra-stagione, è stata condotta un'analisi esplorativa:

*   **Distribuzioni delle Feature**:
    *   `avg_uPER` ha mostrato una distribuzione approssimativamente normale.
    *   `num_stars_uPER` (valori da 0 a 4) ha mostrato che la maggior parte delle squadre-stagioni ha 0, 1 o 2 stelle, con poche squadre aventi 3 o più stelle.
    *   `total_wins` ha anch'essa mostrato una distribuzione quasi normale.
*   **Relazioni tra Feature (Scatter Plots)**:
    *   È emersa una tendenza positiva tra `avg_uPER` e `total_wins`.
    *   Similmente, è stata osservata una tendenza positiva tra `num_stars_uPER` e `total_wins`.
    *   Anche `avg_uPER` e `num_stars_uPER` hanno mostrato una relazione positiva.
*   **Matrice di Correlazione**:
    *   `avg_uPER` vs `total_wins`: Correlazione positiva moderata (0.44).
    *   `num_stars_uPER` vs `total_wins`: Correlazione positiva (0.35).
    *   `avg_uPER` vs `num_stars_uPER`: Correlazione positiva moderata (0.45), indicando che le due feature per il clustering non erano eccessivamente ridondanti.

L'EDA ha confermato che le feature scelte erano sensate e mostravano relazioni attese con il successo della squadra.

## 4. Clustering delle Squadre-Stagioni (K-Means)

Per identificare gli archetipi di costruzione delle squadre, è stato utilizzato l'algoritmo di clustering K-Means, basandosi sulle feature `avg_uPER` e `num_stars_uPER`.

*   **Standardizzazione delle Feature**: Prima del clustering, le due feature sono state standardizzate (media 0, deviazione standard 1) usando `StandardScaler` per assicurare che entrambe contribuissero equamente al calcolo delle distanze.
*   **Scelta del Numero di Cluster (k)**: Il metodo "Elbow" (o curva del gomito) è stato utilizzato per determinare un numero ottimale di cluster. Analizzando il grafico dell'inerzia (WCSS) rispetto al numero di cluster, `k=4` è stato scelto come valore che bilanciava bene la riduzione della varianza intra-cluster con la complessità del modello.
*   **Esecuzione di K-Means**: L'algoritmo K-Means è stato eseguito con `k=4` sui dati standardizzati. Le etichette dei cluster risultanti sono state aggiunte al DataFrame `df_team_season_features`.

## 5. Analisi e Interpretazione dei Cluster (Archetipi di Squadra)

I 4 cluster identificati sono stati analizzati esaminando le caratteristiche medie di `avg_uPER`, `num_stars_uPER` e, soprattutto, `total_wins` per ciascun gruppo. Questo ha permesso di definire i seguenti archetipi di squadra:

*   **Cluster 3 ("Squadre d'Élite / Super-Team")**:
    *   `avg_uPER` medio: ~0.426 (il più alto)
    *   `num_stars_uPER` medio: ~2.52 (2-3 stelle)
    *   `total_wins` medio: **~58.04** (il più alto)
    *   *Interpretazione*: Squadre con alta qualità media e un numero significativo di stelle, associate al maggior successo.

*   **Cluster 0 ("Squadre Solide con una Stella Guida")**:
    *   `avg_uPER` medio: ~0.398 (buono)
    *   `num_stars_uPER` medio: ~1.26 (circa 1 stella)
    *   `total_wins` medio: **~46.70** (secondo più alto)
    *   *Interpretazione*: Squadre competitive costruite attorno a una stella principale e un buon cast di supporto.

*   **Cluster 2 ("Squadre Coese Senza Stelle d'Élite")**:
    *   `avg_uPER` medio: ~0.400 (buono, simile al Cluster 0)
    *   `num_stars_uPER` medio: 0.00 (nessuna stella secondo la soglia)
    *   `total_wins` medio: **~44.04** (terzo più alto)
    *   *Interpretazione*: Squadre senza stelle definite dalla soglia uPER, ma con una buona qualità media generale. Raggiungono un successo rispettabile, probabilmente grazie a profondità e gioco di squadra.

*   **Cluster 1 ("Squadre in Difficoltà / Ricostruzione")**:
    *   `avg_uPER` medio: ~0.364 (il più basso)
    *   `num_stars_uPER` medio: ~0.44 (poche o nessuna stella)
    *   `total_wins` medio: **~34.38** (il più basso)
    *   *Interpretazione*: Squadre con bassa qualità media e mancanza di talento d'élite, associate al minor numero di vittorie.

## 6. Conclusioni per la RQ2

L'analisi dei cluster ha permesso di rispondere alla Research Question:

1.  La strategia di **concentrare talento d'élite (più stelle) combinata con un'alta qualità media dei giocatori (alto `avg_uPER`)** è quella che si correla più fortemente con un elevato numero di vittorie (Archetipo "Squadre d'Élite / Super-Team").
2.  Avere **una stella principale supportata da una buona qualità generale del roster** è anch'essa una strategia efficace per ottenere un numero significativo di vittorie (Archetipo "Squadre Solide con una Stella Guida").
3.  È possibile ottenere un **successo moderato anche senza giocatori che superano la soglia di "stella"**, a patto che la **qualità media complessiva del roster sia sufficientemente alta** (Archetipo "Squadre Coese Senza Stelle d'Élite"). Questo sottolinea l'importanza della profondità e del talento diffuso.
4.  Infine, squadre con **bassa qualità media generale e assenza di stelle tendono ad avere il minor numero di vittorie** (Archetipo "Squadre in Difficoltà / Ricostruzione").

Questa analisi fornisce quindi spunti su come diverse filosofie di costruzione del roster possono tradursi in differenti livelli di successo sul campo, basandosi sulle metriche derivate dal dataset NBA.