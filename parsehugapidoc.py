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

        try:
            version=re.sub("/(v\d+)/.*","_\g<1>",re.search("/v\d+/",k).string)
        except AttributeError as e:
            version=""


        if version.__len__():
            title=k.split('/')[2]
        else:
            title=k.split('/')[1]

        title=title+version
        
        print (title)

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
        output="_params_:\n\n"

    try:
        output=output+"_result_:\n\n"+"\n".join([f"- **{k}**: {w}" for k,w in info['outputs'].items()])
        output=output+"\n\n"
    except KeyError:
        output=output+"_result_:\n\n"

    try:
        output=output+"_usage_:\n\n"+info['usage']+"\n\n"
    except KeyError:
        output=output+"_usage_:\n\n"

    return output

#def get_title_md(title,calls):
#    output=f"#{title.capitalize()}\n"
#    for call,struct in calls.items():
#        output=output+f"## **{call.capitalize()}**\n\n"
#        for prot,info in struct.items():
#            output=output+f"#### {prot}\n-------------\n"
#            output=output+get_prot_md(info)+"\n\n\n\n"
#        output=output+"\n"
#    return output

def get_title_md(title,calls):
    output=f"#{title.capitalize()}\n"
    for call,struct in calls.items():
        for prot,info in struct.items():
            output=output+f"###**{prot}\t_{call.capitalize()}_**\n-------------\n\n\n\n"
            output=output+get_prot_md(info)+"\n\n\n\n"
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

        print ()
        print ()
        print (outfile)
        print ()
        print ()

        try:
            with open(outfile,"w") as o: o.write(md)
        except Exception as e:
            print ( e )
            print ("ERROR with (Maybe the path does not exists?)", outfile)

