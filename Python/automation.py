"""
Python script to automate fetching raw data for matches.
It uses beautiful soup for parsing data and retrieving matches parameters.
"""

# FIXME:
#  add parsing utr matches

import requests as r
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from googlesearch import search


def get_matches():
    """
    Gets all relevant atp matches from tennisexplorer.com
    Outputs matches in following format:
    ["date, first_player, second_player, first_rank, second_rank, first_coef, second_coef", ...]

    @rtype list
    @return list of matches
    """

    matches = []
    url = "https://www.tennisexplorer.com"
    page = r.get(url)
    check_status_code(page)

    # parse web page and get link to the tournament matches
    parser = BeautifulSoup(page.text, 'html.parser')
    tr_tags = parser.find_all("tr", {"class": "head"})
    atp_men_block = tr_tags[0].td.parent.parent
    rows = atp_men_block.find_all("tr")

    # for each tournament page parse get matches
    for row in rows:
        try:
            # go to tournament page
            path = row.td.a['href']

            # skip utr tournaments
            if 'utr' in path:
                continue

            tournament_page = r.get(url + path)
            check_status_code(tournament_page)
            tournament_parser = BeautifulSoup(tournament_page.text, 'html.parser')

            try:
                table = tournament_parser.find_all('div', {'id': 'tournamentTabs-1-data'})[0].tbody
            except IndexError:
                table = tournament_parser.find_all('table', {'class': 'result'})[0].tbody

            table_matches = table.find_all('tr')
            # go to match page
            for match in table_matches:
                try:
                    match_path = match.find_all('td', {'class': 't-name'})[0].a['href']
                    match_page = r.get(url + match_path)
                    check_status_code(match_page)
                    match_parser = BeautifulSoup(match_page.text, 'html.parser')

                    # get date
                    date = match_parser.find('div', {'id': 'center'}).find_all('div', {'class': 'box'})[0]
                    time = date.text.split(',')[0] + date.text.split(',')[1]

                    # get ranking
                    result_table = match_parser.find_all('table', {'class': 'gDetail'})
                    first_rank = result_table[0].tbody.find_all('td', {'class': 'tr'})[0].text
                    first_rank = first_rank[:-1]
                    second_rank = result_table[0].tbody.find_all('td', {'class': 'tl'})[0].text
                    second_rank = second_rank[:-1]

                    # get player names
                    players = match_parser.find_all('th', {'class': 'plName'})
                    first_player = players[0].a.text
                    second_player = players[1].a.text

                    # get coefficients
                    coeff_rows = match_parser.find('div', {'id': 'oddsMenu-1-data'})
                    for coeff_row in coeff_rows.find_all('a'):
                        if 'bet365' in coeff_row['href']:
                            bet365 = coeff_row.parent.parent
                            try:
                                first_coef = bet365.find('td', {'class': 'k1'}).find('div', {'class': 'oup'}).text
                                second_coef = bet365.find('td', {'class': 'k2'}).find('div', {'class': 'odown'}).text
                            except AttributeError:
                                first_coef = bet365.find('td', {'class': 'k1'}).find_all('div', {'class': 'odds-in'})[0].text
                                second_coef = bet365.find('td', {'class': 'k2'}).find_all('div', {'class': 'odds-in'})[0].text

                            first_coef = first_coef[0:4]
                            second_coef = second_coef[0:4]

                            # skip if coeff is too high (5 or higher)
                            if float(first_coef) >= 5 or float(second_coef) >= 5:
                                continue

                            # get elo ranking
                            first_player = first_player.replace('-', ' ')
                            second_player = second_player.replace('-', ' ')
                            player_names = [first_player, second_player]
                            player_elo = get_elo_ranking(player_names)
                            if player_elo[0] is None or player_elo[1] is None:
                                continue

                            # get total amount of wins
                            try:
                                first_player_wins = get_total_amount_of_wins(first_player)
                                second_player_wins = get_total_amount_of_wins(second_player)
                            except Exception as e:
                                print('Error while parsing total wins for players:', first_player, second_player, e)
                                continue

                            result = time + ', ' + first_player + ', ' + second_player + ', ' + \
                                     first_rank + ', ' + second_rank + ', ' + \
                                     first_coef + ', ' + second_coef + ', ' + \
                                     player_elo[0] + ', ' + player_elo[1] + ', ' + \
                                     str(first_player_wins) + ', ' + str(second_player_wins) + ', ' + path.split('/')[1].upper()
                            matches.append(result)
                except IndexError:
                    pass
        except TypeError:
            pass
    if len(matches) == 0:
        print('No matches found.')
    return matches


def get_elo_ranking(player_names: list):
    """
    Gets player's elo ranking by name.

    @param player_names list of player's name
    @type player_names list
    @rtype list
    @return list of elo ranking
    """

    url = 'http://tennisabstract.com/reports/atp_elo_ratings.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    page = r.get(url, headers=headers)
    check_status_code(page)

    # parse web page and extract elo ranking
    parser = BeautifulSoup(page.text, 'html.parser')
    links = parser.find_all('a')

    elo_list = []

    for player in player_names:
        # split name to check if 'a' tag contains this in no order
        name = player.split(" ")[0]
        surname = player.split(" ")[1]

        # if player's name consists of 3 words
        if len(player.split(" ")) > 2:
            patronymic = player.split(" ")[2]

            for link in links:
                url = link['href']

                if re.search(name, url, re.IGNORECASE) and re.search(name, url, re.IGNORECASE):
                    row = link.parent.parent
                    elo = row.contents[3].string
                    elo_list.append(elo)
                    break
                elif re.search(name, url, re.IGNORECASE) and re.search(patronymic, url, re.IGNORECASE):
                    row = link.parent.parent
                    elo = row.contents[3].string
                    elo_list.append(elo)
                    break
                if links.index(link) + 1 == len(links):
                    print("Not found elo for player:", player)
            continue

        # iterate via 'a' tags to find the one with player name in its href attribute
        for link in links:
            url = link['href']
            if re.search(name, url, re.IGNORECASE) and re.search(surname, url, re.IGNORECASE):
                row = link.parent.parent
                elo = row.contents[3].string
                elo_list.append(elo)
                break
            elif links.index(link) + 1 == len(links):
                print("Not found elo for player:", player)
    return elo_list


def get_total_amount_of_wins(name: str):
    """
    Retrieves total amount of wins for specified player.
    Parsing atptour.com page.
    @param name player's name
    @type name string
    @rtype string
    @return total amount of wins
    """
    url = "https://www.atptour.com/en/content/ajax/player-match-record-page?matchRecordType=tour&playerId="
    url += str(player_id(name))

    driver = webdriver.Chrome()
    driver.get(url)
    data = driver.find_element_by_css_selector(
        "table.mega-table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(4) > table:nth-child(1)")
    amount_of_wins = int(data.text.split('-')[0].strip())
    amount_of_loses = int(data.text.split('-')[1].strip())
    return amount_of_wins-amount_of_loses


# FIXME:
#  - not take the first page, but page about this player
def player_id(name: str):
    """
    Retrieves player's id for atptour.com.
    @rtype string
    @return player's id
    """
    query = 'atp tour ' + name
    for j in search(query, tld="co.in", num=1, stop=1, pause=2):
        return j.split('/overview')[0].split('/')[6]


def check_status_code(page: r.Response):
    """
    Checks response status code.
    If value is not 200 then print error message.
    @param page request response
    @type page request.model.Response
    """
    if page.status_code != 200:
        print("Error, status code: " + str(page.status_code) + " url: " + page.url)


print(get_total_amount_of_wins('Auger Aliassime'))
