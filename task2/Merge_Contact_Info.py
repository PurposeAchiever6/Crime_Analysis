import pandas as pd
from urllib.parse import urlparse

# Read CSV files
file1 = pd.read_csv("all_information.csv")
file2 = pd.read_csv("clean_information.csv")
file3 = pd.read_excel("Contact research - V2.xlsx")

def get_url_match(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
    return base_url

# Create a new column containing only the url_match in file1
file1["url_match"] = file1["url"].apply(get_url_match)
file2["url_match"] = file2["url"].apply(get_url_match)

# Merge based on "url_match" and "Link"
merged1 = file1.merge(file3, left_on="url_match", right_on="Link", how="left")
merged2 = file2.merge(file3, left_on="url_match", right_on="Link", how="left")

# Drop one of the duplicate ID columns, if needed
merged1.drop("url_match", axis=1, inplace=True)
merged1.drop("#", axis=1, inplace=True)
merged1.drop("Link", axis=1, inplace=True)
merged2.drop("url_match", axis=1, inplace=True)
merged2.drop("#", axis=1, inplace=True)
merged2.drop("Link", axis=1, inplace=True)

# Save the merged CSV file
merged1.to_csv("all_information_merged.csv", index=False)
merged2.to_csv("clean_information_merged.csv", index=False)