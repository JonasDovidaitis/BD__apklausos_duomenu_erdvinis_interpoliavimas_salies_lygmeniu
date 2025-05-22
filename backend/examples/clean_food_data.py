import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import shutil
from examples.examples_constants import RAW_DATA_PATH, PREPARED_DATA_PATH

education_mapping = {
    'Pradinis issilavinimas': 'EDUC_P_all',
    'Pagrindinis issilavinimas': 'EDUC_B_all',
    'Vidurinis issilavinimas': 'EDUC_S_all',
    'Aukstesnysis issilavinimas (igytas aukstesniojoje technikos mokykloje, politechnikume, aukstesniojoje kolegijos mokykloje, kolegijoje)': 'EDUC_PS_all',
    'Aukstasis issilavinimas (baigtos bakalauro ar magistranturos ar doktoranturos studijos)': 'EDUC_H_all', 
}

availability_mapping = {
    'Studentas, moksleivis': 'ACT_student',
    'Dirbantis asmuo': 'ACT_employees',
    'Kitas, nepriklauso darbo jegai (savanoris, nedirbantis pagal darbu sutarti; nescios ir gimdziusios moterys neturincios darbo santykio; sauktinis/kariuomenes savanoris, neturintis darbo santykio; asmuo, kuris neturi darbo santykio del savo seimos nario nuo': 'ACT_other',
    'Nedirbantis asmuo (uzsiregistraves uzimtumo tarnyboje/darbo birzoje)': 'ACT_unemployed',
}

gender_mapping = {
    'Moteris': 'FEMALE',
    'Vyras': 'MALE'
}

municipality_mapping = {
    'Vilniaus miesto savivaldybe': 'Vilniaus miesto savivaldybė',
    'Kauno miesto savivaldybe': 'Kauno miesto savivaldybė',
    'Pasvalio rajono savivaldybe': 'Pasvalio rajono savivaldybė',
    'Kaisiadoriu rajono savivaldybe': 'Kaišiadorių rajono savivaldybė',
    'Klaipedos miesto savivaldybe': 'Klaipėdos miesto savivaldybė',
    'Kalvarijos savivaldybe': 'Kalvarijos savivaldybė',
    'Vilkaviskio rajono savivaldybe': 'Vilkaviškio rajono savivaldybė',
    'Plunges rajono savivaldybe': 'Plungės rajono savivaldybė',
    'Raseiniu rajono savivaldybe': 'Raseinių rajono savivaldybė',
    'Siauliu miesto savivaldybe': 'Šiaulių miesto savivaldybė',
    'Anyksciu rajono savivaldybe': 'Anykščių rajono savivaldybė',
    'Kauno rajono savivaldybe': 'Kauno rajono savivaldybė',
    'Ignalinos rajono savivaldybe': 'Ignalinos rajono savivaldybė',
    'Panevezio miesto savivaldybe': 'Panevėžio miesto savivaldybė',
    'Elektrenu savivaldybe': 'Elektrėnų savivaldybė',
    'Sirvintu rajono savivaldybe': 'Širvintų rajono savivaldybė',
    'Vilniaus rajono savivaldybe': 'Vilniaus rajono savivaldybė',
    'Kedainiu rajono savivaldybe': 'Kėdainių rajono savivaldybė',
    'Alytaus miesto savivaldybe': 'Alytaus miesto savivaldybė',
    'Svencioniu rajono savivaldybe': 'Švenčionių rajono savivaldybė',
    'Lazdiju rajono savivaldybe': 'Lazdijų rajono savivaldybė',
    'Taurages rajono savivaldybe': 'Tauragės rajono savivaldybė',
    'Telsiu rajono savivaldybe': 'Telšių rajono savivaldybė',
    'Traku rajono savivaldybe': 'Trakų rajono savivaldybė',
    'Mazeikiu rajono savivaldybe': 'Mažeikių rajono savivaldybė',
    'Radviliskio rajono savivaldybe': 'Radviliškio rajono savivaldybė',
    'Druskininku savivaldybe': 'Druskininkų savivaldybė',
    'Kupiskio rajono savivaldybe': 'Kupiškio rajono savivaldybė',
    'Marijampoles savivaldybe': 'Marijampolės savivaldybė',
    'Birzu rajono savivaldybe': 'Biržų rajono savivaldybė',
    'Skuodo rajono savivaldybe': 'Skuodo rajono savivaldybė'
}

elderly_municipality_mapping = {
    'Zirmunu seniunija': 'Žirmūnų seniūnija',
    'Senamiescio seniunija': 'Senamiesčio seniūnija',
    'Antakalnio seniunija': 'Antakalnio seniūnija',
    'Pasilaiciu seniunija': 'Pašilaičių seniūnija',
    'Fabijoniskiu seniunija': 'Fabijoniškių seniūnija',
    'Naujamiescio seniunija': 'Naujamiesčio seniūnija',
    'Adutiskio seniunija': 'Adutiškio seniūnija',
    'Kurkliu seniunija': 'Kurklių seniūnija',
    'Dainavos seniunija': 'Dainavos seniūnija',
    'Silainiu seniunija': 'Šilainių seniūnija',
    'Sanciu seniunija': 'Šančių seniūnija',
    'Gatauciu seniunija': 'Gataučių seniūnija',
    'Panemunes seniunija': 'Panemunės seniūnija',
    'Eiguliu seniunija': 'Eigulių seniūnija',
    'Varniu seniunija': 'Varnių seniūnija',
    'Aleksoto seniunija': 'Aleksoto seniūnija',
    'Akademijos seniunija': 'Akademijos seniūnija',
    'Ringaudu seniunija': 'Ringaudų seniūnija',
    'Kaisiadoriu apylinkes seniunija': 'Kaišiadorių apylinkės seniūnija',
    'Zaliakalnio seniunija': 'Žaliakalnio seniūnija',
    'Pasvalio miesto seniunija': 'Pasvalio miesto seniūnija',
    'Ziezmariu apylinkes seniunija': 'Žiežmarių apylinkės seniūnija',
    'Klausuciu seniunija': 'Klausučių seniūnija',
    'Kaisiadoriu miesto seniunija': 'Kaišiadorių miesto seniūnija',
    'Graziskiu seniunija': 'Gražiškių seniūnija',
    'Alsedziu seniunija': 'Alsėdžių seniūnija',
    'Plunges miesto seniunija': 'Plungės miesto seniūnija',
    'Raseiniu miesto seniunija': 'Raseinių miesto seniūnija',
    'Kavarsko seniunija': 'Kavarsko seniūnija',
    'Vilainiu seniunija': 'Vilainių seniūnija',
    'Kulautuvos seniunija': 'Kulautuvos seniūnija',
    'Griciupio seniunija': 'Gričiupio seniūnija',
    'Vidiskiu seniunija': 'Vidiškių seniūnija',
    'Giluciu seniunija': 'Gilučių seniūnija',
    'Sirvintu miesto seniunija': 'Širvintų miesto seniūnija',
    'Grigiskiu seniunija': 'Griškabūdžio seniūnija',
    'Nemencines seniunija': 'Nemenčinės seniūnija',
    'Zujunu seniunija': 'Zujūnų seniūnija',
    'Kedainiu miesto seniunija': 'Kėdainių miesto seniūnija',
    'Alytaus seniunija': 'Alytaus seniūnija',
    'Taujenu seniunija': 'Taujėnų seniūnija',
    'Sveksnos seniunija': 'Švėkšnos seniūnija',
    'Raseiniu seniunija': 'Raseinių seniūnija',
    'Lazdiju seniunija': 'Lazdijų seniūnija',
    'Kuktiskiu seniunija': 'Kuktiškių seniūnija',
    'Kulupenu seniunija': 'Kūlupėnų seniūnija',
    'Kupiskio seniunija': 'Kupiškio seniūnija',
    'Kuliu seniunija': 'Kulių seniūnija',
    'Taurages seniunija': 'Tauragės seniūnija',
    'Ryskenu seniunija': 'Ryškėnų seniūnija', 
    'Luokes seniunija': 'Luokės seniūnija', 
    'Traku seniunija': 'Trakų seniūnija',
    'Rudiskiu seniunija': 'Rudiškių seniūnija',
    'Mazeikiu seniunija': 'Mažeikių seniūnija',
    'Pakalniskiu seniunija': 'Pakalniškių seniūnija',
    'Vieciunu seniunija': 'Viečiūnų seniūnija',
    'Kuciunu seniunija': 'Kučiūnų seniūnija',
    'Kursenu miesto seniunija': 'Kuršėnų miesto seniūnija',
    'Krosnos seniunija': 'Krosnos seniūnija',
    'Kruonio seniunija': 'Kruonio seniūnija',
    'Lazdynu seniunija': 'Lazdynų seniūnija',
    'Surviliskio seniunija': 'Surviliškio seniūnija'  
}

food_category_mapping = {
    'Fair': 0,
    'Good': 1,
    'Excellent': 2,
}

def categorize_age(age):
    if 0 <= age <= 4:
        return 'all_00_04'
    elif 5 <= age <= 9:
        return 'all_05_09'
    elif 10 <= age <= 14:
        return 'all_10_14'
    elif 15 <= age <= 19:
        return 'all_15_19'
    elif 20 <= age <= 24:
        return 'all_20_24'
    elif 25 <= age <= 29:
        return 'all_25_29'
    elif 30 <= age <= 34:
        return 'all_30_34'
    elif 35 <= age <= 39:
        return 'all_35_39'
    elif 40 <= age <= 44:
        return 'all_40_44'
    elif 45 <= age <= 49:
        return 'all_45_49'
    elif 50 <= age <= 54:
        return 'all_50_54'
    elif 55 <= age <= 59:
        return 'all_55_59'
    elif 60 <= age <= 64:
        return 'all_60_64'
    elif 65 <= age <= 69:
        return 'all_65_69'
    elif 70 <= age <= 74:
        return 'all_70_74'
    elif 75 <= age <= 79:
        return 'all_75_79'
    elif 80 <= age <= 84:
        return 'all_80_84'
    elif age >= 85:
        return 'all_85_plius'
    else:
        return None

def clean_food_data():
    df = pd.read_csv(f'{RAW_DATA_PATH}/surveys/food_scoring/food_scoring.csv', encoding='latin1')
    df.rename(
        columns={
            'Q1A1': 'gender',
            'Q2A1': 'age',
            'Q3A1': 'education',
            'Q4A1': 'availability',
            'Q5A1': 'municipality',
            'Q6A1': 'elderly_municipality',
            'EatingHabitCategory': 'eating_habit_category'
        }, 
        inplace=True
    )
    df = df[['gender', 'age', 'education', 'availability', 'municipality', 'elderly_municipality', 'eating_habit_category', 'EatingHabitTotalScore']]
    df['gender'] = df['gender'].replace(gender_mapping)
    df['age'] = df['age'].apply(categorize_age)
    df['education'] = df['education'].replace(education_mapping)
    df['availability'] = df['availability'].replace(availability_mapping)
    df['municipality'] = df['municipality'].replace(municipality_mapping)
    df['municipality'] = df['municipality'].replace(municipality_mapping)
    df['elderly_municipality'] = df['elderly_municipality'].replace(elderly_municipality_mapping)
    df['eating_habit_category'] = df['eating_habit_category'].replace(food_category_mapping)
    dst_dir = f'{PREPARED_DATA_PATH}/food_survey'
    os.makedirs(dst_dir, exist_ok=True)
    df.to_csv(f'{dst_dir}/food_scoring.csv', index=False, encoding='ISO-8859-13')
    dest_path = os.path.join(PREPARED_DATA_PATH, 'food_config.json')
    shutil.copy2(f'{RAW_DATA_PATH}/surveys/food_scoring/config.json', dest_path)
