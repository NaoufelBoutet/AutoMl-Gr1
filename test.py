import pandas as pd
df = pd.DataFrame({'col1': [10, 'Hello\nWorld', '\x00test\x7F']})

# Nettoyage avec le regex
df['col1'] = df['col1'].str.replace(r'[\s\x00-\x1F\x7F-\x9F]+', '', regex=True)
print(df)