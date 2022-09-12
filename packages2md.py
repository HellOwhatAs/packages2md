from pip import main
from io import StringIO
import sys
from typing import List,Dict,Union,Tuple

__all__=["pkgs_info", "outputmd"]

def pkgs_info()->Tuple[List[Dict[str, Union[str,None,List[str]]]],Dict[str,int]]:
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    main(["list"])
    sys.stdout = old_stdout
    pkgs=([_[0] for i in mystdout.getvalue().replace('\r','').replace('_','-').lower().split('\n')[2:] if (_:=i.split())])

    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    main(["show"]+pkgs)
    sys.stdout=old_stdout
    pkgs=[({_[0]:(None if _[1]=="UNKNOWN" or not _[1] else _[1]) for i in part.split('\n') if len(_:=i.split(': '))>1}) for part in mystdout.getvalue().replace('\r','').split('\n---\n')]
    
    for i in pkgs:
        i["Name"]=i["Name"].replace('_','-').lower()
        i["Requires"]=[_ for j in i["Requires"].replace('_','-').lower().split(',') if (_:=j.strip())] if i["Requires"] else []
        i["Required-by"]=[_ for j in i["Required-by"].replace('_','-').lower().split(',') if (_:=j.strip())] if i["Required-by"] else []
    
    return pkgs,{i["Name"]:ind for ind,i in enumerate(pkgs)}

def outputmd(filepath:str,enable_a:bool=True,_pkgs_info:Union[Tuple[List[Dict[str, Union[str,None,List[str]]]],Dict[str,int]],None]=None):

    if _pkgs_info is None:pkgs,name2ind=pkgs_info()
    else:pkgs,name2ind=_pkgs_info

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
