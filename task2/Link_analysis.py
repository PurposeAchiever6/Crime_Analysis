from seleniumbase import SB
from time import sleep
import csv
import openai
import os

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import VectorDBQA
from langchain.document_loaders import TextLoader
from dotenv import load_dotenv
load_dotenv('.env')

openai.api_key = os.getenv('OPENAI_API_KEY')

all_urls = []
# [[url, subject, object, search_engine], ...]  ++++++++++++ This is input value.
urls_information = {}
# url -> [specified_subject                     ++++++++++++ This is output value.
# o Identify and categorize judicial cases mentioned
# o Detect mentions of Paul Phua (Wei Sheng Phua) belonging to a criminal group (14k, Triads, gang)
# o Track mentions of the acquittal of cases.
# o Language of the article
# o Date of publication
# o Publisher's name
# o Publisher's specialty, focusing on relations to gambling.
# o Publisher's country
# o Publisher's global contact email
# ]

with open('url.csv', 'r') as f:
    reader = csv.reader(f)
    all_urls = list(reader)

## 1. Data extraction using data scraping technology
def _is_specific_subject(sb):
    try:
        is_paul_phua = sb.assert_text("Paul Phua", "body")
    except Exception as e:
        is_paul_phua = False
    
    try:
        is_wei_seng_phua = sb.assert_text("Wei Seng Phua", "body")
    except Exception as e:
        is_wei_seng_phua = False
    
    return [is_paul_phua, is_wei_seng_phua]

def data_extraction(url_list, sb):
    try:
        sleep(1)
        sb.open(url_list[0])
        sleep(5)
    except Exception as e:
        return False

    [is_paul_phua, is_wei_seng_phua] = _is_specific_subject(sb)
    if is_paul_phua == False and is_wei_seng_phua == False:
        return False
    try:
        element_title = sb.get_title()
    except Exception as e:
        element_title = 'none'
    
    try:
        element_time = sb.get_text_content('div.r, time', by="css selector")
    except Exception as e:
        element_time = 'none'
    try:
        elements = sb.find_elements('div.r, p', by="css selector")
        elements_p = [element.text for element in elements]
        element_p = '\n\n'.join(map(str, elements_p))
    except Exception as e:
        element_p = 'none'
    # print('element_title', element_title)
    # print('element_time', element_time)
    # print('element_p', element_p)
    element_man = 'Wei Seng Phua'
    if is_paul_phua == True : element_man = 'Paul Phua'
    urls_information[url_list[0]] = [element_man]
    return [element_title, element_time, element_p, element_man]


## 2. Understanding about extracted data using Gpt Api
def get_gpt_result(qa, need_information):
    query = f'What is the {need_information}? You must output only {need_information}. You must not say any other words. If you say other words, it is a big mistake. If you can\'t get information from article, output ---.'
    answer = qa.run(query)
    print(answer)
    return answer
def get_gpt_language(article_info, need_information):
    query = f'You get information about the article information from given article. The information you get is {need_information}? You must output only {need_information}. You must not say any other words. If you say other words, it is a big mistake. If you can\'t get information from article, output ---.'
    qu = article_info + query
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": qu}])
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

def data_understanding(url, content):
    file = open('temp.txt', 'wt', encoding='utf-8')
    file.write('\n'.join(map(str, [f'Article title is {content[0]}.', f'Time is {content[1]}.', f'Context is {content[2]}.'])))
    file.close()
    loader = TextLoader('temp.txt', encoding='utf-8')
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(texts, embeddings)
    qa = VectorDBQA.from_chain_type(llm=OpenAI(), chain_type="stuff", vectorstore=vectordb)

    urls_information[url].append(get_gpt_result(qa, 'identification and categorization of mentioned judicial cases'))
    urls_information[url].append(get_gpt_result(qa, f'the detection of mentions of {content[3]}\'s affiliation with a criminal group (14k, Triads, gang)'))
    urls_information[url].append(get_gpt_result(qa, 'information related to the acquittal of cases'))
    urls_information[url].append(get_gpt_language('\n'.join(map(str, [f'Article title is {content[0]}.', f'Time is {content[1]}.', f'Context is {content[2][1:200]}.'])), 'language of the article'))
    urls_information[url].append(get_gpt_result(qa, 'date of publication'))
    urls_information[url].append(get_gpt_result(qa, 'publisher\'s name'))
    urls_information[url].append(get_gpt_result(qa, 'publisher\'s specialty, focusing on relations to gambling'))
    urls_information[url].append(get_gpt_result(qa, 'publisher\'s country'))
    urls_information[url].append(get_gpt_result(qa, 'publisher\'s global contact email'))

chunk_size = 30
except_urls = ['.fr', '.co.nz']
with SB(uc=True) as sb:
    for i in range(0, len(all_urls), chunk_size):
        urls_information = {}
        for url_list in all_urls[i:i+chunk_size]:
            print(url_list[0])
            if any(except_url in url_list[0] for except_url in except_urls):
                urls_information[url_list[0]] = []
                continue
            result_extraction = data_extraction(url_list, sb)
            if result_extraction == False:
                urls_information[url_list[0]] = []
            else:
                data_understanding(url_list[0], result_extraction)

        file_path = f'result/infomation_{i}-{i+chunk_size}.csv'
        urls_information_list = []
        col_name = ['url', 'criminaler', 'Identify and categorize judicial cases mentioned', 'Detect mentions of criminaler belonging to a criminal group (14k, Triads, gang)', 
                    'information related to the acquittal of cases', 'Language of the article', 'Date of publication', 'Publisher\'s name',
                    'Publisher\'s specialty, focusing on relations to gambling', 'Publisher\'s country', 'Publisher\'s global contact email']
        for key, value in urls_information.items():
            urls_information_list.append([key] + value)
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            # Create a CSV writer object
            writer = csv.writer(file)
            # Write the data to the CSV file
            writer.writerow(col_name)
            writer.writerows(urls_information_list)
    # url_list = ['https://theblacksea.eu/stories/football-leaks-2018/paul-phua-gambler-montenegro/', 'Phua', 'Vegas', 'https://www.google.us']
    # result_extraction = data_extraction(url_list, sb)
    # if result_extraction == False:
    #     urls_information[url_list[0]] = []
    # else:
    #     data_understanding(url_list[0], result_extraction)