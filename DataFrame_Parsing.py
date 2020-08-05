# Import libraries

import xml
import re
import os
import json
import numpy
import pandas as pd
import xml.etree.ElementTree as ET
import time
start_time = time.time()

# Definition of the paths of the diferent files to parse
path = "/data"
art_def ='data/ArtDefinitions.xml'
abities = 'data/Abilities.xml'
cards = 'data/Templates.xml'


# Definition of the game variables

FACTION_ID = {'1':'Neutral',
              '2':'Monsters',
              '4':'Nilfgaard',
              '8':'Northern Realms',
              '16':'Scoiatael',
              '32':'Skellige',
              '64':'Syndicate'}

RARITY = {'1':'Common',
          '2':'Rare',
          '4':'Epic',
          '8':'Legendary'
         }
TYPE = {'1':'Leader',
        '2':'Spell',
        '4':'Unit',
        '8':'Artifact',
        '16':'Stratagem'}
TIER ={'1':'Leader',
       '2':'Bronce',
       '8':'Gold'}

AVIABILITY={'0':'Non-Ownable',
            '1':'Base set',
            '2':'Tutorial set',
            '3':'Thronebreaker set',
            '10':'Unmillable set (aka Starter Set)',
            '11':'Crimsom Curse set',
            '12':'Novigrad set',
            '13':'Iron Judgment set',
            '14':'Merchants of Ofier',
            '15':'Master Mirror'
}

# This function fixes the codification on the categories of the cards, the value is on decimal and it has to convert it binary
# count the number of zeros until the first one of the number in binary. In case the categorie is from a e1 child, it needs to 
# add a 64 value, if not the category asigned will be incorrect.

def conversion(e,num,tipo): 
    
    valor_cat=[]
    if num ==0:
        valor_cat ='0'
    else:
        for cat, bit in  enumerate('{0:b}'.format(num)[::-1]):
            if bit == '1':
                if e =='e0':
                    valor_cat = tipo + '_{0}'.format(cat)
                else:
                    valor_cat = tipo + '_{0}'.format((cat + 64))
    return valor_cat

# Cards Parsing

cards = 'data/Templates.xml'
tree = ET.parse(cards)
root = tree.getroot()
cards = []
valores=[]
for child in root:

    card_templates = {
                    "ID": [],
                    "Name": [],
                    "Available": [],
                    "ArtId": [],
                    "Placement":[] 
                     }
    card_templates["ID"] = child.attrib['Id']
    card_templates["Name"] = child.attrib['DebugName']
    card_templates["Available"] = child.attrib['Availability']
    card_templates["ArtId"] = child.attrib['ArtId']
    for subchild in child:
 

        card_templates[subchild.tag] = subchild.text
        for value in ['PrimaryCategory','Categories','SemanticTags']:
            e0= int(child.find(value).find('e0').attrib['V'])
            e1= int(child.find(value).find('e1').attrib['V'])
            e2= int(child.find(value).find('e2').attrib['V'])

            
            if value == 'SemanticTags':

                card_templates[value + '_0'] =conversion('e0',e0,'semantic_category')
                card_templates[value + '_1'] =conversion('e1',e1,'semantic_category')
                card_templates[value + '_2'] =conversion('e2',e2,'semantic_category')
                
            else:
                if e0 == 0 and e1 != 0 :
                    card_templates[value + '_0'] =conversion('e1',e1,'card_category')
                    card_templates[value + '_1'] =conversion('e2',e2,'card_category')
                    card_templates[value + '_2'] ='0'
 
 
                else:
                    
                    card_templates[value + '_0'] =conversion('e0',e0,'card_category')
                    card_templates[value + '_1'] =conversion('e1',e1,'card_category')
                    card_templates[value + '_2'] =conversion('e2',e2,'card_category')
       
        if subchild.tag == 'Placement':
            playerside = child.find('Placement').attrib
            valor= playerside['PlayerSide']

            if valor !='0':
                card_templates['Placement'] = 'Loyal'
            else:
                card_templates['Placement'] = 'Disloyal'
        
    cards.append(card_templates)
df_cartas = pd.DataFrame(cards).drop_duplicates(subset= ['ID'],keep='last')
df_cartas = df_cartas[df_cartas['ID'].map(len) ==6 ].reset_index(drop = True) # To remove the "cards" that define each faction, these one are not real cards.




# Art Parsing

art_def ='data/ArtDefinitions.xml'
tree = ET.parse(art_def)
root = tree.getroot()

artes = []
valores=[]
vanity = []
for child in root:

    try:
        try:
            arts = {"Type": [],
                    "ArtId": [],
                    'ArtistName':[],
                    "StandardMask": [],
                    "PremiumMask": [],
                    "PremiumTexMask":[],
                    "VanitySkins_0": [],
                    "VanitySkins_1": [],
                    "VanitySkins_2": [],
                    "VanitySkins_3": []
                    }
            arts["Type"] = child.attrib['Type']
            arts["ArtId"] = child.attrib['ArtId']
            arts["ArtistName"] = child.attrib['ArtistName']
            arts["StandardMask"] = child.attrib['StandardMask']
            arts["PremiumMask"] = child.attrib['PremiumMask']
            arts["PremiumTexMask"] = child.attrib['PremiumTexMask']
            for subchild in child:
                if subchild.tag =='VanitySkins':

                    e0 = child.find('VanitySkins').find('e0').attrib
                    e1 = child.find('VanitySkins').find('e1').attrib

                    try:

                        e2 = child.find('VanitySkins').find('e2').attrib
                        try:
                            e3 = child.find('VanitySkins').find('e3').attrib
                            arts["VanitySkins_0"] = e0
                            arts["VanitySkins_1"] = e1
                            arts["VanitySkins_2"] = e2
                            arts["VanitySkins_3"] = e3
                            artes.append(arts)
                        except:
                            arts["VanitySkins_0"] = e0
                            arts["VanitySkins_1"] = e1
                            arts["VanitySkins_2"] = e2
                            artes.append(arts)
                    except:
                        arts["VanitySkins_0"] = e0
                        arts["VanitySkins_1"] = e1
                        artes.append(arts)


        except:
            arts = {"Type": [],
                    "ArtId": [],
                    "StandardMask": [],
                    "PremiumMask": [],
                    "PremiumTexMask":[],
                    "VanitySkins_0": []
                    }
            arts["Type"] = child.attrib['Type']
            arts["ArtId"] = child.attrib['ArtId']
            arts["StandardMask"] = child.attrib['StandardMask']
            arts["PremiumMask"] = child.attrib['PremiumMask']
            arts["PremiumTexMask"] = child.attrib['PremiumTexMask']
            artes.append(arts)
        artes.append(arts)
    except:
        arts = {"Type": [],
                "ArtId": [],
                "VanityId": [],
                "RegionMask": [],

                    }
        arts["Type"] = child.attrib['Type']
        arts["ArtId"] = child.attrib['ArtId']
        arts["VanityId"] = child.attrib['VanityId']
        arts["RegionMask"] = child.attrib['RegionMask']
        artes.append(arts)

df_arte = pd.DataFrame(artes)
df_arte= df_arte.drop_duplicates(subset= ['ArtId'],keep='last').reset_index(drop = True)


# Merger of the arts and cards dataframes

df_arte_carta = pd.merge(df_arte,df_cartas, on = ['ArtId'], how= 'outer')


# Parser of the localization and Abilities

# First Localizations


import re
local= 'data/Localization/en-us.csv'
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    print(cleanr)
    cleantext = re.sub(cleanr, '', raw_html)
    print(cleantext)
    return cleantext

def tooltips_keyswords(self):
    result_keys = re.findall(r'<keyword=([^>]+)>', self)
    #print(result_keys)
    result_abilities= re.findall(r'.?\{([A-z]+)\}.*?', self)
    #print(result_abilities)
    keywords = []
    for key in result_keys:
        if not key in keywords:
            keywords.append(key.capitalize())
    #print(keywords)
    for key in result_abilities:
        key_up = key.capitalize()
        if not key_up in keywords:
            if key != 'Charges' or key != 'Coins':
                keywords.append(key_up)
    keywords = list(set(keywords)) # ponemos el set para quitar los duplis
    return keywords



csv_file = open(local,"r", encoding = 'utf8')
name_text_parsed = {}
fluff_text_parsed ={}
KEYWORDS = {}
CARD_CATEGORY = {}
tooltipo_parsed = {}
tooltipo_keywords_parsed = {}
for line in csv_file:
    split = line.split(";", maxsplit = 1)
    if len(split)< 2:
        continue
    if '_name' in split[0]:
        card_id = split[0].replace('_name', '')
        name_text_parsed[card_id]= split[1].replace('\n','')
    elif '_fluff' in split[0]:
        card_id = split[0].replace('_fluff', '')
        fluff_text_parsed[card_id]= split[1].replace('\n', '')
    elif 'keyword_' in split[0]:
        if split[1] == 'ignore\n' or 'Ignore.\n':
            card_id = split[0].replace('keyword_', '')
            KEYWORDS[card_id]= split[1]
        if re.match("<",split[1]):
        
            card_id = split[0].replace('keyword_', '')
            ruto = split[1].split('>')
            key = ruto[1].split('<')[0]
            text = ruto[2].replace('\n','')
            key_text = key + text
            KEYWORDS[card_id]= key_text
        else:
            
            card_id = split[0].replace('keyword_', '')
            KEYWORDS[card_id]= split[1]
    elif 'card_category_'  in split[0]:
        card_id= split[0]
        CARD_CATEGORY[card_id] = split[1].replace("\n","")
    elif '_tooltip' in split[0]:
        card_id = split[0].replace('_tooltip', '')
        html_cleaned_text = clean_html(split[1])

        tooltipo_parsed[card_id] = html_cleaned_text.replace("-B.P.BB_Hoard", "").replace("Tribute-B.P.BB_Tribute", "Tribute").replace("\\n", " ").replace("\n", " ")
        tooltipo_keywords_parsed[card_id] = tooltips_keyswords(split[1])

## Second Abilities


abities = 'data/Abilities.xml'
tree = ET.parse(abities)
root = tree.getroot()
valores=[]
abilities_corrected ={}
card_abilities={}
card_abilities_persistent={}

dict_abilities = {}
dict_abilities_persistent = {}
for child in root:
    if child.attrib['Type'] == 'CardAbility':
        card_abilities = {}

        card_id = child.attrib['Template']
        for subchild in child:
            if subchild.tag == 'TemporaryVariables':
                if subchild.attrib['Type'] == "AbilityVariables":
                    for subsubchild in subchild:
                        abilities_corrected ={}
                        for i in range(0,7):
                            variables = {}
                            try:
                                valor_e = child.find('TemporaryVariables').find('e' + str(i)).attrib
                               
                                if valor_e['Type'] == 'IntVar':
                                    variables = {valor_e['Name'].capitalize():valor_e['V']}
                                    abilities_corrected.update(variables)
                            except:
                                pass
                        card_abilities[card_id]= abilities_corrected
                        
            elif subchild.tag == 'PersistentVariables':
                if subchild.attrib['Type'] == "AbilityVariables":
                    for subsubchild in subchild:
                        abilities_corrected_persistent ={}
                        for i in range(0,7):
                            variables_persistent = {}
                            try:
                                valor_e = child.find('PersistentVariables').find('e' + str(i)).attrib
                               
                                if valor_e['Type'] == 'IntVar':
                                    variables_persistent = {valor_e['Name'].capitalize():valor_e['V']}
                                    abilities_corrected_persistent.update(variables_persistent)
                            except:
                                pass
                        card_abilities_persistent[card_id]= abilities_corrected_persistent    
                       
    dict_abilities.update(card_abilities) 
    dict_abilities_persistent.update(card_abilities_persistent) 

# Crossrefence between the values of the abilities and localization data. To relate the tooltip values with the numeric values of abilities for the cards and the leaders.


filter_key_length = {key:val for key, val in tooltipo_parsed.items() if len(key)== 6}
habilidades = [dict_abilities,dict_abilities_persistent]
for clave, valor in filter_key_length.items():
    result = re.findall(r'.*?\{(.*?)\}.*?', valor)
    #while result != []:
    for valores_diccionario in habilidades:
        for key, value in filter_key_length.items():
            for key2,value2 in valores_diccionario.items():
                if key == key2:
                    result = re.findall(r'.*?\{(.*?)\}.*?', value)
                    result = result
                    for valor in result:
                        valor_maxus = valor.capitalize()
                        for key3,value3 in value2.items():
                            if valor == key3:
                                filter_key_length[key] = value.replace('{' + valor + '}',value3)
                            elif valor_maxus == key3:
                                filter_key_length[key] = value.replace('{' + valor + '}',value3)
                                    
for i in range(0,len(df_cartas)):
    for key, value in filter_key_length.items():
        if key == df_cartas['ID'].iloc[i]:
            filter_key_length[key] = value.replace('{Template.Provision}',df_cartas['Provision'].iloc[i])
            
# Selection of the names and tooltips with ID has longitud of 6 numbers, only those selected will be the real cards of the game.
filtered_name_text_parsed = {key:val for key, val in name_text_parsed.items() if len(key)== 6}
filterd_tooltipo_keywords_parsed = {key:val for key, val in tooltipo_keywords_parsed.items() if len(key)== 6}

# Merger of the abilities atributes

df_filtered_name_text_parsed = pd.DataFrame(filtered_name_text_parsed, index = [0]).T.reset_index(drop = False).rename(columns = {'index':'ID',0: 'Name'})
df_fluff_text_parsed = pd.DataFrame(fluff_text_parsed, index = [0]).T.reset_index(drop = False).rename(columns = {'index':'ID',0: 'fluff'})
df_filter_key_length = pd.DataFrame(filter_key_length, index = [0]).T.reset_index(drop = False).rename(columns = {'index':'ID',0: 'Tooltip'})
df_filterd_tooltipo_keywords_parsed = pd.DataFrame.from_dict(filterd_tooltipo_keywords_parsed, orient = 'index').reset_index(drop=False).rename(columns={'index':'ID',0:'hab0',1:'hab1',2:'hab2',3:'hab3',4:'hab4',5:'hab5',6:'hab6',7:'hab7'})
df_locations = df_filtered_name_text_parsed.merge(df_fluff_text_parsed, how ='outer', on='ID')
df_locations = df_locations.merge(df_filter_key_length, how ='outer', on='ID')
df_locations = df_locations.merge(df_filterd_tooltipo_keywords_parsed, how ='outer', on='ID')

# Final DataFrame Merger

df_gwent = df_arte_carta.merge(df_locations, how = 'outer', on='ID' )

# Values substitution on the final dataframes

columnas =['FactionId',
           'SecondaryFactionId',
           'Rarity',
           'Type_y',
           'Tier',
           'Available',
           'PrimaryCategory_0',
           'PrimaryCategory_1',
           'PrimaryCategory_2',
           'Categories_0',
           'Categories_1',
           'Categories_2']
diccionarios = [FACTION_ID,
                FACTION_ID,
                RARITY,
                TYPE,
                TIER,
                AVIABILITY,
                CARD_CATEGORY,
                CARD_CATEGORY,
                CARD_CATEGORY,
                CARD_CATEGORY,
                CARD_CATEGORY,
                CARD_CATEGORY]

# Saving of the dataframe before the substition of the values of the game variables for the numeric values, in case we want to try some Machine learning with the data in number not in categoric values.
os.chdir(r'C:/Users/alexs/Desktop/Alejandro/Universidad/Proyectos/Gwent_Data/data')
writer = pd.ExcelWriter('df_gwent_RAW.xlsx', engine='xlsxwriter')
df_gwent.to_excel(writer, sheet_name='Data')
writer.save() 
for i in range(0,len(columnas)):
    
    df_gwent[columnas[i]].replace(diccionarios[i],inplace =True)



# To try to get a corrected way of the artist names, as they are not always well writen.

from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()



df_gwent['ArtistName']= df_gwent['ArtistName'].fillna('None')

for i in range(0,len(df_gwent['ArtistName'])):
    for j in range(0,len(df_gwent['ArtistName'])):
        a=df_gwent['ArtistName'][i]
        b=df_gwent['ArtistName'][j]
        len1 = len(df_gwent['ArtistName'][i])
        len2 = len(df_gwent['ArtistName'][j])
        simulitud = similar(a,b)
        if len1>len2:
            if simulitud> 0.75:
                df_gwent['ArtistName'][i] = df_gwent['ArtistName'][j]
        else:
            if simulitud> 0.75:
                df_gwent['ArtistName'][j] = df_gwent['ArtistName'][i]

df_gwent = df_gwent[['ID','Name_x','Available','Power', 'Armor','Provision','ArtistName' ,'Placement', 'Rarity', 'PrimaryCategory_0',
       'PrimaryCategory_1', 'PrimaryCategory_2', 'Categories_0',
       'Categories_1', 'Categories_2','FactionId','SecondaryFactionId', 'Tier', 'Type_y','fluff', 'Tooltip', 'hab0',
       'hab1', 'hab2', 'hab3', 'hab4', 'hab5', 'hab6', 'hab7']]

df_gwent = df_gwent.drop(['PrimaryCategory_1', 'PrimaryCategory_2', 'Categories_2'], axis = 1)
df_gwent = df_gwent.rename(columns = {'Name_x': 'Name','PrimaryCategory_0':'Category_0', 'Categories_0':'Category_1','Categories_1':'Category_2','SecondaryFactionId':'FactionId2','Type_y': 'Type','fluff':'Fluff'})
df_gwent_leaders = df_gwent[df_gwent['Type'] == 'Leader'][['ID','Name','Available','Provision'	,'ArtistName','Rarity','FactionId','Type','Fluff','Tooltip']]
df_gwent_leaders = df_gwent_leaders.astype({'ID':'int','Provision':'int'})
df_gwent =df_gwent[df_gwent.ID.apply(lambda x: len(str(x))==6)] # para quedarme unicamente aquelals cuyo ID sea el asociado a una carta
df_gwent = df_gwent.astype({'ID':'int','Power':'int','Armor':'int','Provision':'int'})
df_gwent['Num'] = 1 
df_cahir = pd.DataFrame({'ID':[162104],'Category_3':['Knigth']})
df_gwent = df_gwent.merge(df_cahir, on = 'ID',how= 'outer')
df_gwent = df_gwent[['ID','Name','Available' ,'Power','Armor','Provision' ,'ArtistName','Placement' ,'Rarity','Category_0','Category_1','Category_2','Category_3','FactionId' ,'FactionId2','Tier','Type' ,'Fluff','Tooltip','hab0','hab1','hab2','hab3','hab4','hab5','hab6','hab7','Num']]
df_gwent = df_gwent[df_gwent['Type']!='Leader']



os.chdir(r'C:/Users/alexs/Desktop/Alejandro/Universidad/Proyectos/Gwent_Data/data')
# Saving of the final dataframe that will be used in the dashboard.
writer = pd.ExcelWriter('df_gwent.xlsx', engine='xlsxwriter')
df_gwent.to_excel(writer, sheet_name='Data')
writer.save() # Uncommented for saving the data, comment if you dont want to save the data
# Saving of the dataframe that contains the info of the different leaders.
writer = pd.ExcelWriter('df_gwent_leaders.xlsx', engine='xlsxwriter')
df_gwent_leaders.to_excel(writer, sheet_name='Data')
writer.save() # Uncommented for saving the data, comment if you dont want to save the data



print("--- %s seconds ---" % (time.time() - start_time))
# The final Dataframe is saved.