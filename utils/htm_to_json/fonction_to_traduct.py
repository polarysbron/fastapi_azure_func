import re
from datetime import datetime

def mapping_period(value, cat):

    if re.search(r"^(Fév\.|Mars |Avr\.|Mai |Juin |Jul\.|Août |Sep\.|Oct\.|Nov\.|Déc\.)@", value):
        if cat == "def":
            return "mois_an"
        else:
            if re.search(r"/", value):
                return "mois_an"
            else:
                return "mois_an_complet" 
    
    elif re.search(r"^Jan\. à @", value) :
        if cat == "def":
            return 'cumul_an'
        else:
            if re.search(r"/", value):
                return "cumul_an"
            else:
                return "cumul_an_complet"

    
    elif re.search(r"à", value) :
        return "cumul_12_mois_an"
    
    elif re.search(r"Ann\.", value):
        return "an_moins_1"
    # Périodes trimestrielles
    elif re.search(r"^[1|2|3|4] Trim\.", value):
        return "trimX4_an"
    
    # Périodes semestrielles
    elif re.search(r"^[1|2] Sems\.", value):
        return "semX2_an"
    
    elif re.search(r"^Jan\.@", value):
        return "moisX12_an"
    
    else:
        return None


def are_consecutives_values(lst, val1="Jan.@", val2="Fév.@") :
    verif = False
    liste_index = []
    for i in range(len(lst) - 1):
        if val1 in lst[i] and val2 in lst[i+1]:
            verif = True
            liste_index.append(i)
    if verif:
        return True, liste_index
    else :
        return False, None


def fonction_date_arrete (date, periode_cat) :
    if periode_cat == "def" :
        date = datetime.strptime(date, '%Y-%m-%d')
        if date.month == 1 :
            return datetime(date.year - 1, 12, 1).strftime('%Y-%m-%d')
        else :
            return datetime(date.year, date.month - 1, 1).strftime('%Y-%m-%d')
    else :
        return date


def format_element(element):
    return element + ' ' * (5 - len(element))


def decompo_element(element) :
    if element.endswith("FR"):
        return ["FRANCE"]
    elif element.endswith("OM"):
        return ["DOM"]
    elif element.endswith("XXS"):
        return ["FRANCE", "DOM"]


def clean_string(s):
    # Remplace les sauts de ligne et les espaces consécutifs par un seul espace
    s = re.sub(r'\n+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def html_to_dict(soup):

    # The outer table contains rows that represent each variable.
    outer_table_rows = soup.select('table > tbody > tr')
    
    result = {}
    
    for row in outer_table_rows[1:]:

        is_colspan_here = False

        # Get all td elements in the current row
        tds = row.find_all('td')

        for td in tds:
            if td.has_attr('colspan') and td['colspan'] == "2":
                is_colspan_here = True
        # Extract the variable name, which is the content of the first <td> in each row.
        variable_name = row.td.text.strip()
        
        # The details for each variable are in a sub-table. We extract the rows of this sub-table.
        inner_table_rows = row.select('table > tbody > tr')
        
        details = []
        if is_colspan_here :
            for inner_row in inner_table_rows :
                libelle = inner_row.select_one('td:nth-of-type(1)').text.strip()
                valeur = inner_row.select_one('td:nth-of-type(2)').text.strip()
                
                # Split the "valeur" on "ET" to handle multiple conditions.
                # Clean up the string to remove unwanted characters like "\n" and then split them.
                conditions = [clean_string(cond) for cond in valeur.split(" ET ")]
                
                details.append({
                    'libelle': libelle,
                    'valeur': conditions
                })
            
            result[variable_name] = details
        
    return result


def consecutive_months_count(months_list):
    # Dictionnaire pour convertir le nom du mois en numéro
    month_to_num = {
        'Jan.': 1, 'Fév.': 2, 'Mars': 3, 'Avr.': 4,
        'Mai': 5, 'Juin': 6, 'Jul.': 7, 'Août': 8,
        'Sep.': 9, 'Oct.': 10, 'Nov.': 11, 'Déc.': 12
    }
    
    # Extraire les mois et les années
    months_and_years = []
    for item in months_list:
        match = re.search(r"(\w+\.?)\s?@\s?(\d{4})", item)
        if match:
            month = month_to_num.get(match.group(1), 0)
            year = int(match.group(2))
            months_and_years.append((month, year))
    
    # Compter les mois consécutifs pour la même année
    max_count = 0
    count = 1
    for i in range(1, len(months_and_years)):
        if months_and_years[i][1] == months_and_years[i-1][1] and months_and_years[i][0] == months_and_years[i-1][0] + 1:
            count += 1
            max_count = max(max_count, count)
        else:
            break

    return max_count


def consecutive_trim_count(trimesters_list):
        # Dictionnaire pour convertir le nom du mois en numéro
    trimester_to_num = {
        '1 Trim.': 1, '2 Trim.': 2, '3 Trim.': 3, '4 Trim.': 4
    }
    
    # Extraire les mois et les années
    trims_and_years = []
    for item in trimesters_list:
        match = re.search(r"(\d\s?Trim\.)\s?@\s?(\d{4})", item)
        if match:
            trim = trimester_to_num.get(match.group(1), 0)
            year = int(match.group(2))
            trims_and_years.append((trim, year))
    
    # Compter les mois consécutifs pour la même année
    max_count = 0
    count = 1
    for i in range(1, len(trims_and_years)):
        if trims_and_years[i][1] == trims_and_years[i-1][1] and trims_and_years[i][0] == trims_and_years[i-1][0] + 1:
            count += 1
            max_count = max(max_count, count)
        else:
            break

    return max_count


def consecutive_sems_count(trimesters_list):
        # Dictionnaire pour convertir le nom du mois en numéro
    semester_to_num = {
        '1 Sems.': 1, '2 Sems.': 2
    }
    
    # Extraire les mois et les années
    sems_and_years = []
    for item in trimesters_list:
        match = re.search(r"(\d\s?Sems\.)\s?@\s?(\d{4})", item)
        if match:
            sems = semester_to_num.get(match.group(1), 0)
            year = int(match.group(2))
            sems_and_years.append((sems, year))
    
    # Compter les mois consécutifs pour la même année
    max_count = 0
    count = 1
    for i in range(1, len(sems_and_years)):
        if sems_and_years[i][1] == sems_and_years[i-1][1] and sems_and_years[i][0] == sems_and_years[i-1][0] + 1:
            count += 1
            max_count = max(max_count, count)
        else:
            break

    return max_count

def transformation_filtre (filtre) :

    dict_operator={"<": "lt", ">": "gt", "<=": "le", ">=": "ge", "==": "eq", "!=": "ne"}
    result_filter = []

    for key, value in filtre.items() :
        operator = "in"
        if re.search(r"sauf", key) :
            operator = "not in"
            key = key.split('sauf')[0].strip()
        if len(value) == 1 :
            # Rechercher l'opérateur dans l'expression
            match = re.search(r"(<|>|<=|>=|==|!=)", value[0])
            if match:
                operator_init = match.group(0)  # Récupérer l'opérateur correspondant
                operator = dict_operator.get(operator_init, None)  # Traduire l'opérateur
                value = value[0].split(operator_init)[1].strip()  # Récupérer la clé
        filtre_operator = {"operator": operator, "value": value}
        result_filter.append({key: filtre_operator})
    return {"and": result_filter}

#Permet de convertir l'ancien type utilisé vers le nouveau format de regroupement (s'applique également aux renommages)
def format_regroupement(regroupement):
    formatted_regroup = {}
    for key, regroups in regroupement.items():

        formatted_data = []
        for group in regroups:

            new_group = {}
            # Vérifiez si l'une des valeurs contient "De"
            if any("De" in val for val in group["Valeurs"]):  
                
                for val in group["Valeurs"]:
                    new_group = {}
                    # Récupération des limites de l'intervalle pour chaque valeur.
                    limits = [int(s) for s in val.split() if s.isdigit()]
                    new_group["nom"] = val
                    new_group["operator"] = "between"
                    new_group["valeur"] = limits
                    formatted_data.append(new_group)

            else:  # Sinon, c'est une liste de valeurs.
                new_group["nom"] = group["nom"]
                new_group["operator"] = "in"
                new_group["valeur"] = group["Valeurs"]
                formatted_data.append(new_group)
        formatted_regroup[key] = formatted_data
    return formatted_regroup

#Permet de faire correspondre le nom de la colonne dans le bordereau avec le nom de la colonne dans la table snowflake
mapping_bordereau_to_table_snowflake = {
    "DEPART": "CODE_DEPARTEMENT",
    "CARROSSERIE": "CARROSSERIE_SAS",
    "MARQUE_STT_VN": "ADMIN__MARQUE_STT_VN",
    "GENRE_MOT": "ADMIN__GENRE_MOT",
    "DEPARTEMENT": "NOM_DEPARTEMENT",
}
