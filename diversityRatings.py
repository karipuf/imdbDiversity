import pandas as pd
import numpy as np
import pickle
import statsmodels as sm
from statsmodels.regression import linear_model

#############
# Functions
#############
def castGiniDiv(castList,nameDict,ethDict,numName=True,):

    cList=castList.split(',')
    if numName:
        foo=[]

        # Not all names are in the list! imdb has some missing names apparently
        for tmp in cList:
            try: foo.append(nameDict[tmp])
            except KeyError: pass

        cList=foo
        
    ethDist=pd.value_counts([ethdict[tmp] for tmp in cList]).values
    ethDist=ethDist/ethDist.sum()

    return 1-(ethDist**2).sum()

################
# Script stuff
################

# Loading stuff in
###################

df=pd.read_csv('title.basics_processed.csv')
df=df[df.language=='en']

# Reading in principals
dp=pd.read_csv("title.principals.tsv",'\t')
tset=set(df.tconst)
dp=dp[dp.tconst.isin(tset)]

# Getting all cast members
casts=np.unique(','.join(dp.principalCast).split(','))
dn=pd.read_csv("name.basics.tsv",'\t')
dn=dn[dn.nconst.isin(set(casts))]
dndict=dict(dn[['nconst','primaryName']].values)


# Getting ratings
dr=pd.read_csv('title.ratings.tsv','\t')
dr=dr[dr.tconst.isin(tset)]


# Loading in ethnicities
ethdicttmp=pickle.load(open("imdbeths.pkl",'rb'))
ethdict={tmp[0]:','.join([tmp2['best'] for tmp2 in tmp[1]]) for tmp in ethdicttmp.items()}


# Let's do some science!
#########################

# Finding Gini diversity
gini=lambda instr:castGiniDiv(instr,dndict,ethdict)
dp['gini']=dp.principalCast.apply(gini)
dgr=pd.merge(dr,dp,on='tconst')
dgr['constant']=1

# Regressions
dgrFiltered=dgr[dgr.numVotes>1000]
lr1=sm.regression.linear_model.OLS(dgrFiltered.averageRating,dgrFiltered[['gini','constant']])
lr2=sm.regression.linear_model.OLS(dgrFiltered.numVotes,dgrFiltered[['gini','constant']])

# Printing out the results
print(lr1.fit().summary())
print(lr2.fit().summary())
