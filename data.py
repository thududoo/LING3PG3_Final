languages = {
    "CMN": {"Beijing", "Hebei", "Tianjin", "Liaoning", "Jilin", "Heilongjiang", "Shandong", "Henan", "Ningxia", "Gansu", "Xinjiang", "Sichuan", "Chongqing", "Guizhou", "Hubei", "Jiangsu", "Guangxi", "Shaanxi", "Anhui"},
    "WUU": {"Shanghai", "Jiangsu", "Zhejiang", "Anhui", "Yunnan"},
    "GAN": {"Jiangxi", "Anhui"},
    "MIN": {"Fujian", "Guangdong", "Hainan"},
    "YUE": {"Guangdong", "Guangxi"},
    "HSN": {"Hunan"},
    "HAK": {"Guangdong", "Guangxi", "Fujian", "Jiangxi"},
    "CJY": {"Shanxi"}
}

a = set()
for i in languages.values():
    a = a.union(i)

print(a)

all={"Anhui",
"Beijing",
"Chongqing",
"Fujian",
"Gansu",
"Guangdong",
"Guangxi",
"Guizhou",
"Hainan",
"Hebei",
"Heilongjiang",
"Henan",
"Hubei",
"Hunan",
"InnerMongolia",
"Jiangsu",
"Jiangxi",
"Jilin",
"Liaoning",
"Ningxia",
"Qinghai",
"Shaanxi",
"Shandong",
"Shanghai",
"Shanxi",
"Sichuan",
"Tianjin",
"Tibet",
"Xinjiang",
"Yunnan",
"Zhejiang",
}

b = all.difference(a)
print(b)