# Codice per una NUOVA cella del notebook Jupyter.
# Assicurarsi che 'driver' sia una variabile globale già inizializzata con la connessione Neo4j
# e che pandas sia importato come pd.
# Assicurarsi che 'db_name' sia definita (es. db_name = "neo4j" o il nome del database specifico)

print(
    f"--- Analisi Approfondita Squadre: Blowout e Partite Combattute (Database: '{db_name}') ---")

try:
    with driver.session(database=db_name) as session:

        # --- 1. Calcolo dello Scarto Medio Generale per Partita ---
        query_avg_margin = """
        MATCH (g:Game)
        WHERE g.ptsHome IS NOT NULL AND g.ptsAway IS NOT NULL
        RETURN abs(g.ptsHome - g.ptsAway) AS margin
        """
        results_avg_margin = session.run(query_avg_margin)
        margins = [record["margin"]
                   for record in results_avg_margin if record["margin"] is not None]

        mean_overall_margin = 0.0
        if not margins:
            print(
                "Nessun dato sulle partite trovato per calcolare lo scarto medio generale.")
        else:
            mean_overall_margin = sum(margins) / len(margins)
            print(
                f"\nScarto Medio Generale (differenza assoluta di punti per partita): {mean_overall_margin:.2f} punti")

        # --- 2. Analisi Blowout (vittorie con scarto >= 40 punti) per Squadra ---
        print("\n--- Squadre con Maggior Numero di Blowout (Vittorie con Scarto >= 40 punti) ---")
        query_blowouts_by_team = """
        MATCH (g:Game)
        WHERE g.ptsHome IS NOT NULL AND g.ptsAway IS NOT NULL AND g.homeTeamWins IS NOT NULL
        WITH g,
             CASE
                 WHEN g.homeTeamWins = 1 THEN g.ptsHome - g.ptsAway
                 ELSE g.ptsAway - g.ptsHome
             END AS winningMargin
        WHERE winningMargin >= 40
        MATCH (winningTeam:Team)-[r]->(g)
        WHERE (g.homeTeamWins = 1 AND type(r) = 'HOSTED_GAME')
           OR (g.homeTeamWins = 0 AND type(r) = 'VISITED_GAME')
        RETURN winningTeam.abbreviation AS teamAbbreviation, 
               winningTeam.nickname AS teamNickname, 
               count(g) AS blowoutWins
        ORDER BY blowoutWins DESC
        """
        results_blowouts = session.run(query_blowouts_by_team)
        records_blowouts = [dict(record) for record in results_blowouts]
        if not records_blowouts:
            df_blowouts_teams = pd.DataFrame(
                columns=['teamAbbreviation', 'teamNickname', 'blowoutWins'])
        else:
            df_blowouts_teams = pd.DataFrame(records_blowouts)

        if df_blowouts_teams.empty:
            print(
                "Nessuna squadra trovata con blowout (vittorie con >= 40 punti di scarto).")
        else:
            print("\nClassifica Squadre per Numero di Blowout:")
            print(df_blowouts_teams[['teamAbbreviation', 'teamNickname', 'blowoutWins']].head(
            ).to_string(index=False))

            gsw_blowouts_data = df_blowouts_teams[df_blowouts_teams['teamAbbreviation'] == 'GSW']
            if not gsw_blowouts_data.empty:
                gsw_blowout_count = gsw_blowouts_data.iloc[0]['blowoutWins']
                gsw_nickname = gsw_blowouts_data.iloc[0]['teamNickname']
                print(
                    f"\nI {gsw_nickname} (GSW) hanno effettuato {gsw_blowout_count} blowout.")
                print(
                    f"Confronto per GSW: {gsw_blowout_count} blowout vs Scarto Medio Generale di {mean_overall_margin:.2f} punti.")
            else:
                print("\nGolden State Warriors (GSW) non hanno registrato blowout (vittorie con >= 40 punti di scarto) o non sono presenti nei dati analizzati.")

            top_blowout_team_abbr = df_blowouts_teams.iloc[0]['teamAbbreviation']
            top_blowout_team_name = df_blowouts_teams.iloc[0]['teamNickname']
            top_blowout_team_count = df_blowouts_teams.iloc[0]['blowoutWins']
            print(
                f"\nLa squadra con il maggior numero di blowout è {top_blowout_team_name} ({top_blowout_team_abbr}) con {top_blowout_team_count} blowout.")
            print(
                f"Confronto per {top_blowout_team_abbr}: {top_blowout_team_count} blowout vs Scarto Medio Generale di {mean_overall_margin:.2f} punti.")

        # --- 3. Analisi Vittorie Combattute (vittorie con scarto = 1 punto) per Squadra ---
        print(
            "\n--- Squadre con Maggior Numero di Vittorie Combattute (Scarto = 1 punto) ---")
        query_close_wins_by_team = """
        MATCH (g:Game)
        WHERE g.ptsHome IS NOT NULL AND g.ptsAway IS NOT NULL AND g.homeTeamWins IS NOT NULL
        WITH g,
             CASE
                 WHEN g.homeTeamWins = 1 THEN g.ptsHome - g.ptsAway
                 ELSE g.ptsAway - g.ptsHome
             END AS winningMargin
        WHERE winningMargin = 1
        MATCH (winningTeam:Team)-[r]->(g)
        WHERE (g.homeTeamWins = 1 AND type(r) = 'HOSTED_GAME')
           OR (g.homeTeamWins = 0 AND type(r) = 'VISITED_GAME')
        RETURN winningTeam.abbreviation AS teamAbbreviation, 
               winningTeam.nickname AS teamNickname, 
               count(g) AS closeWins
        ORDER BY closeWins DESC
        """
        results_close_wins = session.run(query_close_wins_by_team)
        records_close_wins = [dict(record) for record in results_close_wins]
        if not records_close_wins:
            df_close_wins_teams = pd.DataFrame(
                columns=['teamAbbreviation', 'teamNickname', 'closeWins'])
        else:
            df_close_wins_teams = pd.DataFrame(records_close_wins)

        if df_close_wins_teams.empty:
            print("Nessuna squadra trovata con vittorie per 1 punto.")
        else:
            print("\nClassifica Squadre per Numero di Vittorie Combattute (1 punto):")
            print(df_close_wins_teams[[
                  'teamAbbreviation', 'teamNickname', 'closeWins']].head().to_string(index=False))

            top_close_wins_team_abbr = df_close_wins_teams.iloc[0]['teamAbbreviation']
            top_close_wins_team_name = df_close_wins_teams.iloc[0]['teamNickname']
            top_close_wins_team_count = df_close_wins_teams.iloc[0]['closeWins']
            print(
                f"\nLa squadra con il maggior numero di vittorie per 1 punto è {top_close_wins_team_name} ({top_close_wins_team_abbr}) con {top_close_wins_team_count} vittorie.")
            print(
                f"Confronto per {top_close_wins_team_abbr}: {top_close_wins_team_count} vittorie per 1 punto vs Scarto Medio Generale di {mean_overall_margin:.2f} punti.")

except Exception as e:
    print(f"Si è verificato un errore durante l'analisi: {e}")
    # Per un debug più dettagliato, puoi decommentare le righe seguenti:
    # import traceback
    # print(traceback.format_exc())
