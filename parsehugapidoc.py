# coding: utf-8
import json
import sys
import re


def open_struct(filename):
    with open(filename) as o:
        return json.load(o)

def get_titles(struct):
    titles={}
    for k,w in struct.items():
        print (k)
        title=k.split('/')[1]
        try:
            titles[title][k]=w
        except Exception:
            titles[title]={k:w}
    return titles

def get_prot_md(info):
    output=""
    try:
        output="_params_:\n\n"+"\n".join([f"- **{k}**: {w['type']}" for k,w in info['inputs'].items()])
        output=output+"\n\n"
    except KeyError:
        pass

    try:
        output=output+"_result_:\n\n"+"\n".join([f"- **{k}**: {w}" for k,w in info['outputs'].items()])
        output=output+"\n\n"
    except KeyError:
        pass  

    try:
        output=output+"_description_:\n\n"+info['usage']+"\n\n"
    except KeyError:
        pass

    return output

def get_title_md(title,calls):
    output=f"#{title.capitalize()}\n"
    for call,struct in calls.items():
        output=output+f"## *{call.capitalize()}*\n"
        for prot,info in struct.items():
            output=output+f"\n\n\n###{prot}\n-------------\n"
            output=output+get_prot_md(info)
        output=output+"\n"
    return output


if __name__ == "__main__":
    
    try:    
        filename=sys.argv[1]
        parsed=open_struct( filename )
    except Exception as e:    
        raise e       
        sys.exit(1)   
        
    try:    
        outpath=sys.argv[2]
    except Exception as e:    
        outpath='docs/API Reference'
    
    for title,struct in get_titles(parsed['documentation']['handlers']).items():
        md=get_title_md(title,struct)
        outfile=f"{outpath}/{title}.md"
        with open(outfile,"w") as o: o.write(md)

