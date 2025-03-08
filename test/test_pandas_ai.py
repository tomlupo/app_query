import pandasai as pai
import os
from pandasai_openai import OpenAI
import dotenv
import pandas as pd
import numpy as np

# Set your OpenAI API key
dotenv.load_dotenv()
llm = OpenAI(api_token=os.getenv('OPENAI_API_KEY'))
pai.config.set({"llm": llm})

# generate sample data
df = pd.DataFrame(np.random.randint(0, 100, size=(100, 4)), columns=list('ABCD'))
df = pai.DataFrame(df)
response = df.chat("Calculate size of the dataset")
print(response)