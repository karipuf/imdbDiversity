import pandas as pd
import numpy as np
from langdetect import detect

def toint(instr):
    try: return int(instr)
    except: return 0

def language(instr):
    try: return detect(instr.lower())
    except: return "Unknown"

# Loading stuff in
df=pd.read_csv("title.basics.tsv","\t")
df['year']=df.startYear.apply(toint)
df['minutes']=df.runtimeMinutes.apply(toint)

# Only movies from 2016, for now ;-)
df=df[(df.year>2015) & (df.minutes>80)]

# And, English speaking ones, at that.. this step takes a while, btw ;-)
df['language']=df.originalTitle.apply(language)
df.to_csv('title.basics_processed.csv',index=False)

df=df[df.language=='en']

# Reading in principals
dp=pd.read_csv("title.principals.tsv",'\t')
tset=set(df.tconst)
dp=dp[dp.tconst.isin(tset)]

# Getting all cast members
casts=np.unique(','.join(dp.principalCast).split(','))
dn=pd.read_csv("name.basics.tsv",'\t')
dn=dn[dn.nconst.isin(set(casts))]
dn.primaryName.to_csv('post2015_english_names.csv',index=False)
