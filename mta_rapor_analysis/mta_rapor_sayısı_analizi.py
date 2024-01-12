"""
I made this project to use Panda and Matplotlib together. 
I wanted to work with a bad dataset, but the only problem was typos, so I couldn't do what I wanted.
But I still finished the project.
graphs demonstrates the research topics by amount(miktarına_göre_araştırma_konuları) 
and researchs on different types of coal through the years(yıllara göre Kömür tipleri hakkına yapılan araştırmalar).

"""
import pandas as pd 
import matplotlib.pyplot as plt 
from matplotlib.ticker import ScalarFormatter
data=pd.read_csv("Derleme.csv",on_bad_lines="skip",delimiter=";",index_col="NO")

#I fixed typos and removed unnecessary spaces to make better use of the data
rapor_konulari=data["KONUSU"]
modified_lines=[]
for line in rapor_konulari:
    try:
        modified_line=line.lower().replace(" ","").replace("\n","").replace("\t","").replace("\r","").replace("   ","").replace("   ","").replace("   ","")
        modified_lines.append(modified_line)
    except AttributeError:
        modified_lines.append(line)
data["KONUSU"]=modified_lines

# Creating the figure and axes
fig, ax = plt.subplots(nrows=2, ncols=2)
plt.subplots_adjust(hspace=0.5) 
fig.delaxes(ax[1, 1])
fig.delaxes(ax[0, 1])

ax[0, 0].set_xticklabels([])
ax[0, 0].set_yticklabels([])
ax[0, 0] = plt.subplot2grid((2, 2), (0, 0), colspan=2)

ax[1, 0].set_xticklabels([])
ax[1, 0].set_yticklabels([])
ax[1, 0] = plt.subplot2grid((2, 2), (1, 0), colspan=2)

rapor_sayısı = data.groupby("KONUSU")["RAPOR NO"].count()
rapor_sayısı = rapor_sayısı[rapor_sayısı > 100]
ax[0,0].bar(rapor_sayısı.index, rapor_sayısı.values)

ax[0,0].set_title("miktarına_göre_araştırma_konuları")
ax[0,0].tick_params(axis="x",rotation=90)
ax[0,0].set_ylabel("Rapor Sayısı")

#visıalization of kömür tipine göre araştırmalar
komur_ile_alakali_konular=[]
data=data.dropna(subset=["KONUSU"])
for line in data["KONUSU"]:
    if(line.find("kömür") !=-1): #
        komur_ile_alakali_konular.append(line)

data=data[(data["KONUSU"].isin(komur_ile_alakali_konular))]
#Lets start by fixing the typos first
data.loc[data["KONUSU"].isin(["li̇nyi̇tkömürü","li̇nyi̇tkömür", "kömürbli̇nyi̇t", "kömürli̇nyi̇t"]), "KONUSU"] = "linyit kömürü"
data.loc[data["KONUSU"]=="kömürtaşkömürü", "KONUSU"] = "taş kömürü"
komur_tipleri=data.groupby(["YILI","KONUSU"])["RAPOR NO"].count().unstack()
komur_tipleri=komur_tipleri[["taş kömürü","linyit kömürü"]]
komur_tipleri=komur_tipleri.loc["1316":"2023"]
komur_tipleri.plot(kind="bar",ax=ax[1,0],stacked=True)

ax[1,0].set_title("yıllara göre Kömür tipleri hakkına yapılan araştırmalar")
ax[1,0].legend(loc="upper right")
ax[1,0].set_ylabel("Rapor Sayısı")
ax[1,0].tick_params(axis="x",rotation=90)


plt.show()