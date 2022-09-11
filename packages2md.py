import sys, subprocess

__all__=["outputmd"]

pkgs,name2ind=None,None
def outputmd(filepath:str,enable_a:bool=True):
    global pkgs,name2ind
    if pkgs is None or name2ind is None:
        p=subprocess.Popen(sys.executable+" -m pip list",stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        pkgs=p.stdout.read().decode('utf-8').replace('\r','').replace('_','-').lower()
        p.stdout.close()

        pkgs=([_[0] for i in pkgs.split('\n')[2:] if (_:=i.split())])

        p=subprocess.Popen(sys.executable+" -m pip show "+" ".join(pkgs),stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        pkgs=[({_[0]:(None if _[1]=="UNKNOWN" or not _[1] else _[1]) for i in part.split('\n') if len(_:=i.split(': '))>1}) for part in p.stdout.read().decode('utf-8').replace('\r','').split('\n---\n')]
        p.stdout.close()

        for i in pkgs:
            i["Name"]=i["Name"].replace('_','-').lower()
            i["Requires"]=[_ for j in i["Requires"].replace('_','-').lower().split(',') if (_:=j.strip())] if i["Requires"] else []
            i["Required-by"]=[_ for j in i["Required-by"].replace('_','-').lower().split(',') if (_:=j.strip())] if i["Required-by"] else []

        name2ind={i["Name"]:ind for ind,i in enumerate(pkgs)}

    with open(filepath,'w') as f:
        f.write("```mermaid\ngraph LR;\n")
        for i in pkgs:
            f.write("pkg{}(\"{}\")".format(name2ind[i["Name"]],i["Name"]))
            if i["Requires"]:
                f.write(" --> ")
                f.write(" & ".join("pkg{}".format(name2ind[j]) for j in i["Requires"]))
            f.write(";\n")
            if enable_a and i["Home-page"]:
                f.write("click {} href \"{}\";\n".format("pkg{}".format(name2ind[i["Name"]]),i["Home-page"]))
        f.write("```")

if __name__=="__main__":
    outputmd("packages2md_test.md")