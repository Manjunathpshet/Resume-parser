from os import sep, write
from pandas.core.indexes.base import Index
import spacy
import pickle
import random
import re
import streamlit as st
import pandas as pd
from pdfminer.high_level import extract_text


st.set_page_config(layout="wide")
st.title('RESUME PARSER')
   
train_data = pickle.load(open('train_data.pkl', 'rb'))


### Traning the NLP model
nlp = spacy.blank('en')

def train_model(train_data):
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last = True)
    
    for _, annotation in train_data:
        for ent in annotation['entities']:
            ner.add_label(ent[2])
          
    
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes): # train only NER
        optimizer = nlp.begin_training()
        for itn in range(1):
            print('Starting iteration ' + str(itn))
            random.shuffle(train_data)
            losses = {}
            index = 0
            for text, annotations in train_data:
                try:
                    nlp.update([text], [annotations], drop =0.2, sgd = optimizer, losses = losses)
                except Exception as e:
                    pass  
        

# train_model(train_data)

## Saving the model
# nlp.to_disk('nlp_model')


## Loading the model
nlp_model = spacy.load('nlp_model')


   
uploaded_file = st.file_uploader("Upload your file :", type=['pdf' , 'docx'], accept_multiple_files=True)
# st.write(type(uploaded_file))

# For Doc file

import docx2txt
def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None



if len(uploaded_file) != 0:

    st.subheader('Parsed Data : ')

    st.text('')
    st.text('')

    f = []
    for x in uploaded_file:
        file = x.name.split('.')
        f.append(file[1])

    text = []
    for t in range(len(uploaded_file)):
        if f[t] == 'pdf':
            text.append(extract_text(uploaded_file[t]))
        elif f[t] == 'docx':
            text.append((extract_text_from_docx(uploaded_file[t])))

    details = {'NAME':[] ,'PHONE NUMBER':[] ,'EMAIL-ID':[],'LINKEDIN-LINK':[],'GITHUB-LINK':[],'YEARS OF EXPERIENCE':[],
       'LOCATION':[],'DEGREE':[],'COLLEGE NAME':[],'GRADUATION YEAR':[],'COMPANIES WORKED AT':[],'DESIGNATION':[],'SKILLS':[]}
    for x in range(len(text)):
        new_text = text[x].replace('\n', ' ')  # remove \n in text
        doc = nlp_model(new_text)
        PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
        EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
        LINKED_REG = re.compile('linkedin\.com/in/\w+[a-z0-9-]+\w+')
        GITHUB_LINK = re.compile('github\.com/\w+')
        EXP = re.compile(r'\d+[\.]\d+ years')

        phone_number = re.findall(PHONE_REG, new_text)
        email = re.findall(EMAIL_REG, new_text)
        linked_in = re.findall(LINKED_REG , new_text)
        github = match = re.findall(GITHUB_LINK, new_text)
        exp = re.findall(EXP,new_text)

        try :
            if len(phone_number) != 0:
                details['PHONE NUMBER'].append(phone_number[0])
                # st.write(f'PHONE NUMBER : ' , phone_number[0]) ## number 
            else:
                phone_number = None
                details['PHONE NUMBER'].append(phone_number)
                # st.write(f'PHONE NUMBER : ' , phone_number) ## number

            if len(email) !=0:
                details['EMAIL-ID'].append(email[0])
                # st.write(f'EMAIL-ID     : ', email[0] ) ## Email
            else:
                email = None
                details['EMAIL-ID'].append(email)
                # st.write(f'EMAIL-ID     : ', email ) ## Email


            if linked_in !=0:
                details['LINKEDIN-LINK'].append(linked_in[0])
                # st.write(f'LINKEDIN-LINK     : ', 'https://www.'+linked_in[0]) ## Linkedin
            else:
                linked_in = None
                details['LINKEDIN-LINK'].append(linked_in)
                # st.write(f'LINKEDIN-LINK     : ', linked_in) ## Linkedin

            if len(github) !=0 :
                details['GITHUB-LINK'].append(github[0])
                # st.write(f'GITHUB-LINK : ' , 'https://'+ github[0] ) ## Github 
            else:
                github = None
                details['GITHUB-LINK'].append(github)
                # st.write(f'GITHUB-LINK     : ', github)
            if len(exp) !=0 :
                details['YEARS OF EXPERIENCE'].append(exp[0])
                # st.write(f'YEARS OF EXPERIENCE : ' ,  exp[0] ) ## Years of experience 
            else:
                exp = None
                details['YEARS OF EXPERIENCE'].append(exp)
                # st.write(f'YEARS OF EXPERIENCE    : ', exp)     

        except IndexError:
            pass

        for ent in doc.ents:
            if ent.label_.upper() == 'SKILLS':
                details['SKILLS'].append(ent.text)
                # st.write(f'{ent.label_.upper():{20}}- {ent.text}')
            elif ent.label_.upper() == 'NAME':
                details['NAME'].append(ent.text)
                # st.write(f'{ent.label_.upper():{20}}- {ent.text}')
            elif ent.label_.upper() == 'DEGREE':
                details['DEGREE'].append(ent.text)
                # st.write(f'{ent.label_.upper():{20}}- {ent.text}')
            elif ent.label_.upper() == 'COLLEGE NAME':
                details['COLLEGE NAME'].append(ent.text)
                # st.write(f'{ent.label_.upper():{20}}- {ent.text}')
            elif ent.label_.upper() == 'GRADUATION YEAR':
                details['GRADUATION YEAR'].append(ent.text)
                # st.write(f'{ent.label_.upper():{20}}- {ent.text}') 
            elif ent.label_.upper() == 'DESIGNATION':
                details['DESIGNATION'].append(ent.text)
                # st.write(f'{ent.label_.upper():{20}}- {ent.text}')
            elif ent.label_.upper() == 'COMPANIES WORKED AT':
                details['COMPANIES WORKED AT'].append(ent.text)
                # st.write(f'{ent.label_.upper():{20}}- {ent.text}')
            elif ent.label_.upper() == 'LOCATION':
                details['LOCATION'].append(ent.text)
                # st.write(f'{ent.label_.upper():{20}}- {ent.text}')
            elif ent.label_.upper() == 'YEARS OF EXPERIENCE':
                details['YEARS OF EXPERIENCE'].append(ent.text)
                # st.write(f'{ent.label_.upper():{20}}- {ent.text}')

        # for x , y in details.items():
        #     if y:
        #         st.write(f'{x:{50}} : {*y,}') 
        #         # st.write(*y, sep= ',')
        #         # st.write( x , *y, sep ="," )
        #         # st.write(*y, sep= )
        #     else:
        #         st.write(f'{x:{20}} : None')


    col = ['NAME','PHONE NUMBER','EMAIL-ID','LINKEDIN-LINK','GITHUB-LINK','YEARS OF EXPERIENCE',
       'LOCATION','DEGREE','COLLEGE NAME','GRADUATION YEAR','COMPANIES WORKED AT','DESIGNATION','SKILLS']
    new_dict = {}
    for x in col:
        if x in details.keys():
            new_dict[x] = details[x]
        else:
            new_dict[x]= None


    df=pd.DataFrame.from_dict(new_dict,orient='index').transpose()
    st.table(df.iloc[:len(text), :])
    st.markdown("""---""")
    # @st.cache
    def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv(index= False).encode('utf-8')

    st.text('')
    st.text('')
    csv = convert_df(df)
    st.download_button(label="Download data as CSV", data = csv ,file_name='Parsed_data.csv', mime='text/csv',)


else:
    st.write('Please select the file for parsing : ')

st.text('')
st.text('')
st.text('')
st.text('')


with st.expander("About The App :"):
    st.markdown("""
 * This Resume Parser can extract Name, Phone,Email, Designation, Degree, Skills and University, Location, 
companies worked with and duration details. 
 * We are working on adding other entities and to increase the accuracy of the model.
 
 
 See Source Code:
 * [See Source Code](https://github.com/Manjunathpshet/Resume-parser)
""")
  







