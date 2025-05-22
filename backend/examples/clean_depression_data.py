import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import shutil
from examples.examples_constants import RAW_DATA_PATH, PREPARED_DATA_PATH

education_mapping = {
    'Neturintis jokio iðsilavinimo (neágyjæs pradinio iðsilavinimo)': 'EDUC_UP_all',
    'Pradinis iðsilavinimas': 'EDUC_P_all',
    'Pagrindinis iðsilavinimas': 'EDUC_B_all',
    'Vidurinis iðsilavinimas': 'EDUC_S_all',
    'Aukðtesnysis iðsilavinimas (ágytas aukðtesniojoje technikos mokykloje, politechnikume aukðtesniojoje kolegijos mokykloje, kolegijoje)': 'EDUC_PS_all',
    'Aukðtasis iðsilavinimas (baigtos bakalauro ar magistrantûros ar doktorantûros studijos)': 'EDUC_H_all', 
}

availability_mapping = {
    'Studentas, moksleivis': 'ACT_student',
    'Dirbantis asmuo': 'ACT_employees',
    'Kitas, nerpriklauso darbo jëgai (savanoris, nedirbantis pagal darbu sutartá; nëðèios ir gimdþiusios moterys neturinèios darbo santykio; ðauktinis/kariuomenës savanoris, neturintis darbo santykio; asmuo, kuris neturi darbo snatykio dël savo ðeimos nario nuolatinio slaugymo)': 'ACT_other',
    'Nedirbantis asmuo (uþsiregistravæs uþimtumo tarnyboje/darbo birþoje)': 'ACT_unemployed',
    'Pensijos ar kapitalo pajamø gavëjas': 'ACT_pension',
}

profession_mapping = {
  'Specialistas (chemikas, matematikas, biologas, fizikas, ekologas, inþinierius, gydytojas, vaistininkas, aukðtøjø mokyklø dëstytojas, mokytojas, verslo ir adminstravimo specialistas: buchalteris, finansø analitikas, vieðøjø ryðiø specialistas, sistemø analitikas, grafiniø sistemø analitikas, teisininkas, advokatas, teisëjas, teisininkø patarëjas, archyvaras, bibliotekininkas, ekonomistas, vertëjas, muzikantas ir t.t.)': 'PRF_professionals',
  'Árenginiø ir maðinø operatorius ir surinkëjas (plastikiniø gaminiø maðinø operatorius, mediniø gaminiø maðinø operatorius,  traktorininkas, kombainininkas, mechanizatorius ir t.t.)': 'PRF_operators',
  'Ginkluotø pajëgø profesijos atstovas (karevis, puskarininkis, jaunesnysis karininkas, vyresnysis karininkas, generolas, jûreivis ir t.t.)': 'PRF_armed',
  'Ginkluoti pajëgø profesijos (kareviai, puskarininkiai, jaunesnieji karininkai, vyresnieji karininkai,  generolai, jûreiviai ir t.t.)': 'PRF_armed',
  'Kvalifikuotas darbininkas ir amatininkas (mûrininkas, statybininkas, akmens raiþytojas, dailidë, stalius, betonuotojas, apdailininkas,  stogdengys, grindø bei plyteliø klojëjas, tinkuotojas, pastatø apðildytojas, stiklininkas, ðuliniø kasëjas, suvirintojas, kaminkrëtys, kalvis, drabuþiø siuvëjas, batø siuvëjas)': 'PRF_craft',
  'Kvalifikuotas þemës, miðkø ir þuvininkystës ûkio darbuotojas': 'PRF_agrivulture',
  'Nekvalifikuotas darbininkas (valytojas, namø padëjëjas, skalbëja, galvijø ðerikas, nekvalifikuotas sodininkystës darbuotojas, duobkasys, þemkasys, prekiø sandelio krovëjas, gatvës pardavëjas, buitiniø atliekø surinkëjas, kiemsargis, malkø rinkëjas, rûbininkas, priþiûrëtojas ir t.t.)': 'PRF_elementary',
  'Paslaugø sektoriaus darbuotojas ir pardavëjas (virëjas, padavëjas-batmenas, pardavëjas, ekskursijø vadovas, kelioniø vadovas,  kelioniø palydovas,  pirtininkas,  kirpëjas, batsiuvys, komendantas, namø ûkio ekonomas, pastatø priþiûrëtojas, degaliniø operatorius, bufetininkas ir t.t.)': 'PRF_service',
  'Paslaugø sektoriaus darbuotojas ir pardavëjas': 'PRF_service',
  'Specialistas (pavyzdþiui, þemës ûkio specialistas, nekilnojamojo turto specialistas, lazerinës fizikos specialistas, sveikatos prieþiûros specialistas, rinkodaros specialistas.)': 'PRF_professionals',
  'Tarnautojas (adresø sàraðo tvarkytojas, registratorius, sekterorius, raðtvedys, stenografininkas, maðininkas,  telegrafo operatorius, duomenø ávesties operatorius, kompiuteriø operatorius, kompiuterininkas, inkasatorius, valiutø keityklos kasininkas, skolø iðieðkotojas, kelioniø konsultantras, kelioniø organizatorius, telefonø registratorius, apklausø atlikëjæs, dispeèeris, vietinio keleivinio transporto kontrolierius, paðto kontrolierius, kolektorius ir t.t.)': 'PRF_clerics',
  'Technikas ir jaunesnysis specialistas (jaunesnysis fiziniø mokslø ir inþinerijos mokslø specialistas, jaunesnysis sveikatos specialistas, jaunesnysis verslo ir administravimo specialistas, jaunesnysis optikas, jaunesnysis vaistininkas, inspektorius, paðtininkas, bibliotekos tarnautojas, mokytojo padëjëjas, policijos patrulis, ugniagesys ir t.t.)': 'PRF_TAprofessionals',
  'Vadovas (ámonës vadovas, gamybos vadovai, statybø vadovas, prezidentas, seimo narys, ministras pirmininkas, seimo kancleris, prezidento patarëjas, mero padejëjas,  ambasadorius, konsulas, seniûnas t.t.)': 'PRF_managers'
}

gender_mapping = {
    'Moteris': 'FEMALE',
    'Vyras': 'MALE'
}

municipality_mapping = {
    'Klaipëdos miesto savivaldybë': 'Klaipėdos miesto savivaldybė',
    'Kauno miesto savivaldybë': 'Kauno miesto savivaldybė',
    'Jonavos rajono savivaldybë': 'Jonavos rajono savivaldybė',
    'Panevëþio miesto savivaldybë': 'Panevėžio miesto savivaldybė',
    'Vilniaus miesto savivaldybë': 'Vilniaus miesto savivaldybė',
    'Vilniaus rajono savivaldybë': 'Vilniaus rajono savivaldybė',
    'Kelmës rajono savivaldybë': 'Kelmės rajono savivaldybė',
    'Radviliðkio rajono savivaldybë': 'Radviliškio rajono savivaldybė',
    'Telðiø rajono savivaldybë': 'Telšių rajono savivaldybė',
    'Utenos rajono savivaldybë': 'Utenos rajono savivaldybė',
    'Klaipëdos rajono savivaldybë': 'Klaipėdos rajono savivaldybė',
    'Kauno rajono savivaldybë': 'Kauno rajono savivaldybė',
    'Akmenës rajono savivaldybë': 'Akmenės rajono savivaldybė',
    'Marijampolës savivaldybë': 'Marijampolės savivaldybė',
    'Ukmergës rajono savivaldybë': 'Ukmergės rajono savivaldybė',
    'Kaiðiadoriø rajono savivaldybë': 'Kaišiadorių rajono savivaldybė',
    'Kretingos rajono savivaldybë': 'Kretingos rajono savivaldybė',
    'Anykðèiø rajono savivaldybë': 'Anykščių rajono savivaldybė',
    'Kazlø Rûdos savivaldybë': 'Kazlų Rūdos savivaldybė',
    'Vilkaviðkio rajono savivaldybë': 'Vilkaviškio rajono savivaldybė',
    'Ðiauliø miesto savivaldybë': 'Šiaulių miesto savivaldybė',
    'Ðiauliø rajono savivaldybë': 'Šiaulių rajono savivaldybė',
    'Ðilalës rajono savivaldybë': 'Šilalės rajono savivaldybė',
    'Lazdijø rajono savivaldybë': 'Lazdijų rajono savivaldybė',
    'Këdainiø rajono savivaldybë': 'Kėdainių rajono savivaldybė',
    'Trakø rajono savivaldybë': 'Trakų rajono savivaldybė',
    'Birþø rajono savivaldybë': 'Biržų rajono savivaldybė',
    'Kupiðkio rajono savivaldybë': 'Kupiškio rajono savivaldybė',
    'Pasvalio rajono savivaldybë': 'Pasvalio rajono savivaldybė',
    'Panevëþio rajono savivaldybë': 'Panevėžio rajono savivaldybė',
    'Ðvenèioniø rajono savivaldybë': 'Švenčionių rajono savivaldybė',
    'Alytaus miesto savivaldybë': 'Alytaus miesto savivaldybė',
    'Jurbarko rajono savivaldybë': 'Jurbarko rajono savivaldybė',
    'Prienø rajono savivaldybë': 'Prienų rajono savivaldybė',
    'Pakruojo rajono savivaldybë': 'Pakruojo rajono savivaldybė',
    'Druskininkø savivaldybë': 'Druskininkų savivaldybė',
    'Molëtø rajono savivaldybë': 'Molėtų rajono savivaldybė',
    'Varënos rajono savivaldybë': 'Varėnos rajono savivaldybė',
    'Kalvarijos savivaldybë': 'Kalvarijos savivaldybė',
    'Plungës rajono savivaldybë': 'Plungės rajono savivaldybė',
    'Skuodo rajono savivaldybë': 'Skuodo rajono savivaldybė',
    'Zarasø rajono savivaldybë': 'Zarasų rajono savivaldybė',
    'Ðirvintø rajono savivaldybë': 'Širvintų rajono savivaldybė',
    'Rokiðkio rajono savivaldybë': 'Rokiškio rajono savivaldybė',
    'Ðilutës rajono savivaldybë': 'Šilutės rajono savivaldybė',
    'Raseiniø rajono savivaldybë': 'Raseinių rajono savivaldybė',
    'Neringos savivaldybë': 'Neringos savivaldybė',
    'Maþeikiø rajono savivaldybë': 'Mažeikių rajono savivaldybė',
    'Tauragës rajono savivaldybë': 'Tauragės rajono savivaldybė',
    'Ignalinos rajono savivaldybë':'Ignalinos rajono savivaldybė',
    'Ðalèininkø rajono savivaldybë': 'Šalčininkų rajono savivaldybė'
}

elderly_municipality_mapping = {
    "Akmenës seniûnija": "Akmenės seniūnija",
    "Alantos seniûnija": "Alantos seniūnija",
    "Alðënø seniûnija": "Alšėnų seniūnija",
    "Aleksoto seniûnija": "Aleksoto seniūnija",
    "Alizavos seniûnija": "Alizavos seniūnija",
    "Alytaus seniûnija": "Alytaus seniūnija",
    "Antakalnio seniûnija": "Antakalnio seniūnija",
    "Antazavës seniûnija": "Antazavės seniūnija",
    "Anykðèiø seniûnija": "Anykščių seniūnija",
    "Ariogalos seniûnija": "Ariogalos seniūnija",
    "Aviþieniø seniûnija": "Avižienių seniūnija",
    "Bartninkø seniûnija": "Bartninkų seniūnija",
    "Ðaèiø seniûnija": "Šačių seniūnija",
    "Dainavos seniûnija": "Dainavos seniūnija",
    "Ðanèiø seniûnija": "Šančių seniūnija",
    "Darbënø seniûnija": "Darbėnų seniūnija",
    "Ðateikiø seniûnija": "Šateikių seniūnija",
    "Ðatrininkø seniûnija": "Šatrininkų seniūnija",
    "Ðeðkinës seniûnija": "Šeškinės seniūnija",
    "Ðeðtokø seniûnija": "Šeštokų seniūnija",
    "Degaièiø seniûnija": "Degaičių seniūnija",
    "Deguèiø seniûnija": "Degučių seniūnija",
    "Ðiaulënø seniûnija": "Šiaulėnų seniūnija",
    "Ðiauliø kaimiðkoji seniûnija": "Šiaulių kaimiškoji seniūnija",
    "Ðilainiø seniûnija": "Šilainių seniūnija",
    "Ðilutës seniûnija": "Šilutės seniūnija",
    "Ðimoniø seniûnija": "Šimonių seniūnija",
    "Domeikavos seniûnija": "Domeikavos seniūnija",
    "Dovilø seniûnija": "Dovilų seniūnija",
    "Dûkðto seniûnija": "Dūkšto seniūnija",
    "Ðvenèionëliø seniûnija": "Švenčionėlių seniūnija",
    "Eiguliø seniûnija": "Eigulių seniūnija",
    "Fabijoniðkiø seniûnija": "Fabijoniškių seniūnija",
    "Gargþdø seniûnija": "Gargždų seniūnija",
    "Gaurës seniûnija": "Gaurės seniūnija",
    "Gerviðkiø seniûnija": "Gerviškių seniūnija",
    "Ignalinos miesto seniûnija": "Ignalinos miesto seniūnija",
    "Ignalinos seniûnija": "Ignalinos seniūnija",
    "Jaðiûnø seniûnija": "Jadūnų seniūnija",
    "Jonavos miesto seniûnija": "Jonavos miesto seniūnija",
    "Kaiðiadoriø apylinkës seniûnija": "Kaišiadorių apylinkės seniūnija",
    "Kaiðiadoriø miesto seniûnija": "Kaišiadorių miesto seniūnija",
    'Kalvarijos seniûnija': 'Kalvarijos seniūnija',
    "Kazlø Rûdos seniûnija": "Kazlų Rūdos seniūnija",
    "Këdainiø miesto seniûnija": "Kėdainių miesto seniūnija",
    "Kretingalës seniûnija": "Kretingalės seniūnija",
    "Kretingos miesto seniûnija": "Kretingos miesto seniūnija",
    "Kretingos seniûnija": "Kretingos seniūnija",
    "Kudirkos Naumiesèio seniûnija": "Kudirkos Naumiesčio seniūnija",
    "Kulautuvos seniûnija": "Kulautuvos seniūnija",
    "Kupiðkio seniûnija": "Kupiškio seniūnija",
    "Kuþiø seniûnija": "Kužių seniūnija",
    "Lapiø seniûnija": "Lapių seniūnija",
    "Laukuvos seniûnija": "Laukuvos seniūnija",
    "Lazdijø seniûnija": "Lazdijų seniūnija",
    "Lazdynø seniûnija": "Lazdynų seniūnija",
    "Lekëèiø seniûnija": "Lekėčių seniūnija",
    "Lentvario seniûnija": "Lentvario seniūnija",
    "Lyduokiø seniûnija": "Lyduokių seniūnija",
    'Marijampolës seniûnija': 'Marijampolės seniūnija',
    "Maþeikiø seniûnija": "Mažeikių seniūnija",
    "Maþonø seniûnija": "Mažonų seniūnija",
    "Meðkuièiø seniûnija": "Meškuičių seniūnija",
    "Mickûnø seniûnija": "Mickūnų seniūnija",
    "Naujamiesèio seniûnija": "Naujamiesčio seniūnija",
    "Naujininkø seniûnija": "Naujininkų seniūnija",
    "Naujosios Vilnios seniûnija": "Naujosios Vilnios seniūnija",
    "Nemenèinës seniûnija": "Nemenčinės seniūnija",
    "Nemëþio seniûnija": "Nemėžio seniūnija",
    "Onuðkio seniûnija": "Onuškio seniūnija",
    "Paástrio seniûnija": "Paįstrio seniūnija",
    "Paberþës seniûnija": "Paberžės seniūnija",
    "Pabirþës seniûnija": "Pabiržės seniūnija",
    "Pabradës seniûnija": "Pabradės seniūnija",
    "Paðilaièiø seniûnija": "Pašilaičių seniūnija",
    "Pagiriø seniûnija": "Pagirių seniūnija",
    "Pajûrio seniûnija": "Pajūrio seniūnija",
    "Pakruojo seniûnija": "Pakruojo seniūnija",
    "Pakuonio seniûnija": "Pakuonio seniūnija",
    "Panemunës seniûnija": "Panemunės seniūnija",
    "Panevëþio seniûnija": "Panevėžio seniūnija",
    "Pasvalio miesto seniûnija": "Pasvalio miesto seniūnija",
    "Pernaravos seniûnija": "Pernaravos seniūnija",
    "Petraðiûnø seniûnija": "Petrašiūnų seniūnija",
    "Pilaitës seniûnija": "Pilaitės seniūnija",
    "Pilviðkiø seniûnija": "Pilviškių seniūnija",
    "Plungës miesto seniûnija": "Plungės miesto seniūnija",
    "Priekulës seniûnija": "Priekulės seniūnija",
    "Pumpënø seniûnija": "Pumpėnų seniūnija",
    "Radviliðkio seniûnija": "Radviliškio seniūnija",
    "Raseiniø miesto seniûnija": "Raseinių miesto seniūnija",
    "Rasø seniûnija": "Rasų seniūnija",
    "Raudondvario seniûnija": "Raudondvario seniūnija",
    "Rieðës seniûnija": "Riešės seniūnija",
    "Ringaudø seniûnija": "Ringaudų seniūnija",
    "Rokiðkio miesto seniûnija": "Rokiškio miesto seniūnija",
    "Rokø seniûnija": "Rokų seniūnija",
    "Rudaminos seniûnija": "Rudaminos seniūnija",
    "Saugëlaukio seniûnija": "Saugėlaukio seniūnija",
    "Sendvario seniûnija": "Sendvario seniūnija",
    "Seredþiaus seniûnija": "Seredžiaus seniūnija",
    "Siesikø seniûnija": "Siesikų seniūnija",
    "Skirsnemunës seniûnija": "Skirsnemunės seniūnija",
    "Skuodo seniûnija": "Skuodo seniūnija",
    'Sudervës seniûnija': 'Sudervės seniūnija',
    "Svëdasø seniûnija": "Svėdasų seniūnija",
    'Tauragës seniûnija': 'Tauragės seniūnija',
    "Telðiø miesto seniûnija": "Telšių miesto seniūnija",
    "Þalgirio seniûnija": "Žalgirio seniūnija",
    "Þaliakalnio seniûnija": "Žaliakalnio seniūnija",
    "Þemaièiø Naumiesèio seniûnija": "Žemaičių Naumiesčio seniūnija",
    "Þirmûnø seniûnija": "Žirmūnų seniūnija",
    "Þygaièiø seniûnija": "Žygaičių seniūnija",
    'Trakø seniûnija': 'Trakų seniūnija',
    'Tytuvënø seniûnija': 'Tytuvėnų seniūnija',
    'Ukmergës miesto seniûnija': 'Ukmergės miesto seniūnija',
    'Utenos miesto seniûnija': 'Utenos miesto seniūnija',
    'Utenos seniûnija': 'Utenos seniūnija',
    'Uþliedþiø seniûnija': 'Užliedžių seniūnija',
    'Uþusaliø seniûnija': 'Užusalių seniūnija',
    'Varënos seniûnija': 'Varėnos seniūnija',
    'Veisiejø seniûnija': 'Veisiejų seniūnija',
    'Verkiø seniûnija': 'Verkių seniūnija',
    'Vieèiûnø seniûnija': 'Viečiūnų seniūnija',
    'Vilijampolës seniûnija': 'Vilijampolės seniūnija',
    "Zapyðkio seniûnija": "Zapyškio seniūnija",
    "Zarasø miesto seniûnija": "Zarasų miesto seniūnija",
    "Zujûnø seniûnija": "Zujūnų seniūnija"
}

depression_category_mapping = {
    'Depresijos simptomai minimalûs': 0,
    'Menkai iðreikðti depresijos simptomai': 1,
    'Vidutiniðkai iðreikðti depresijos simptomai': 2,
    'Sunkûs depresijos simptomai': 3,
    'Labai sunkûs depresijos simptomai': 4
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

def clean_depression_data():
    df = pd.read_csv(f'{RAW_DATA_PATH}/surveys/depression/depression.csv', encoding='latin1')
    df = df[['gender', 'age', 'education', 'availability', 'Profession', 'municipality', 'elderly_municipality', 'depression_category', 'PHQ']]
    df['gender'] = df['gender'].replace(gender_mapping)
    df['age'] = df['age'].apply(categorize_age)
    df['education'] = df['education'].replace(education_mapping)
    df['availability'] = df['availability'].replace(availability_mapping)
    df['Profession'] = df['Profession'].replace(profession_mapping)
    df['municipality'] = df['municipality'].replace(municipality_mapping)
    df['elderly_municipality'] = df['elderly_municipality'].replace(elderly_municipality_mapping)
    df['depression_category'] = df['depression_category'].replace(depression_category_mapping)
    dst_dir = f'{PREPARED_DATA_PATH}/depression_survey'
    os.makedirs(dst_dir, exist_ok=True)
    df.to_csv(f'{dst_dir}/depression.csv', index=False, encoding='ISO-8859-13')

    dest_path = os.path.join(PREPARED_DATA_PATH, 'depression_config.json')
    shutil.copy2(f'{RAW_DATA_PATH}/surveys/depression/config.json', dest_path)

