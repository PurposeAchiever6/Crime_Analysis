import csv
import codecs

all_urls = []
# [[url, subject, object, search_engine], ...]  ++++++++++++ This is input value. (url.csv)
all_information = []
clean_information = []
col_name = ['url', 'criminaler', 'Identify and categorize judicial cases mentioned', 'Detect mentions of criminaler belonging to a criminal group (14k, Triads, gang)', 
                    'information related to the acquittal of cases', 'Language of the article', 'Date of publication', 'Publisher\'s name',
                    'Publisher\'s specialty, focusing on relations to gambling', 'Publisher\'s country', 'Publisher\'s global contact email']

with open('url.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    all_urls = list(reader)

## 3. Data integration
def data_integration():
    for i in range(0, len(all_urls), chunk_size):
        file_path = f'result/infomation_{i}-{i+chunk_size}.csv'
        with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            next(reader)
            all_information.extend(list(reader))
    with open('all_information.csv', 'w', newline='', encoding='utf-8') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        # Write the data to the CSV file
        writer.writerow(col_name)
        writer.writerows(all_information)


## 4. Data clean
def data_clean():
    for i in all_information:
        if(len(i) != 1): clean_information.append(i)
    with open('clean_information.csv', 'w', newline='', encoding='utf-8') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        # Write the data to the CSV file
        writer.writerow(col_name)
        writer.writerows(clean_information)

chunk_size = 30
data_integration()
data_clean()