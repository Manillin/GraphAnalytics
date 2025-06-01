# Codice per una NUOVA cella del notebook Jupyter.
# Analisi delle vittorie per stagione (2015-2019), con focus su GSW.
# Assicurarsi che 'driver' e 'db_name' siano definiti e pandas sia importato (pd).

print(
    f"--- Analisi Vittorie per Stagione (2015-2019) - Database: '{db_name}' ---")

seasons_to_analyze = [2015, 2016, 2017, 2018, 2019]
all_seasons_data = []

try:
    with driver.session(database=db_name) as session:
        for season in seasons_to_analyze:
            print(f"\n--- Analisi Stagione: {season} ---")

            query_wins_per_team = """
            MATCH (g:Game)
            WHERE g.season = $target_season 
              AND g.homeTeamWins IS NOT NULL 
              AND g.ptsHome IS NOT NULL 
              AND g.ptsAway IS NOT NULL
            
            // Determina l'ID della squadra vincente
            WITH g,
                 CASE
                     WHEN g.homeTeamWins = 1 THEN g.HOME_TEAM_ID 
                     ELSE g.VISITOR_TEAM_ID 
                 END AS winningTeamId
            
            MATCH (winner:Team {teamId: winningTeamId})
            RETURN winner.abbreviation AS teamAbbreviation, 
                   winner.nickname AS teamNickname, 
                   count(g) AS wins
            ORDER BY wins DESC
            """

            results = session.run(query_wins_per_team, target_season=season)
            season_wins_data = [dict(record) for record in results]

            if not season_wins_data:
                print(
                    f"Nessun dato di vittorie trovato per la stagione {season}.")
                continue

            df_season_wins = pd.DataFrame(season_wins_data)

            print(f"Classifica Vittorie Stagione {season} (Top 5):")
            print(df_season_wins.head().to_string(index=False))

            top_team_season = df_season_wins.iloc[0]
            print(
                f"Squadra con più vittorie nella stagione {season}: {top_team_season['teamNickname']} ({top_team_season['teamAbbreviation']}) con {top_team_season['wins']} vittorie.")

            # Dati GSW per la stagione
            gsw_data_season = df_season_wins[df_season_wins['teamAbbreviation'] == 'GSW']
            if not gsw_data_season.empty:
                gsw_wins = gsw_data_season.iloc[0]['wins']
                gsw_rank = gsw_data_season.index[0] + 1  # L'indice è 0-based
                print(
                    f"Golden State Warriors (GSW) nella stagione {season}: {gsw_wins} vittorie (Rank: {gsw_rank}).")
            else:
                print(
                    f"Golden State Warriors (GSW) non trovati nei dati di vittorie per la stagione {season}.")

            # Opzionale: per un DataFrame aggregato successivo
            all_seasons_data.extend(df_season_wins.to_dict('records'))

    # Opzionale: Creare un DataFrame con tutti i dati di tutte le stagioni se necessario per ulteriori analisi
    # if all_seasons_data:
    #     df_all_seasons_wins = pd.DataFrame(all_seasons_data)
    #     print("\n--- Riepilogo Completo (per ulteriori analisi) ---")
    #     print(df_all_seasons_wins.head())

except Exception as e:
    print(
        f"Si è verificato un errore durante l'analisi delle vittorie per stagione: {e}")
    # import traceback
    # print(traceback.format_exc())
