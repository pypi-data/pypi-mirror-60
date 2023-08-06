#****************************************************************************
#* template_rgy.py
#*
#* Registry of template info discovered based on a search list
#****************************************************************************
import os

import jinja2
import configparser
#import yaml

class Parameter:
    def __init__(self, pname, desc, has_default, default):
        self.pname = pname
        self.desc = desc
        self.has_default = has_default
        self.default = default

class TemplateInfo (jinja2.BaseLoader):
    def __init__(self, 
                 tmpl_id, 
                 vte_file):
        self.tmpl_id = tmpl_id
        self.tmpl_dir = os.path.dirname(vte_file)
        self.parameters = {}
        self.desc = ""
       
        vte = configparser.ConfigParser()
        vte.read(vte_file)
        
        for s in vte.sections():
            s = s.strip()
            if s.startswith("parameter"):
                colon_idx = s.find(":")
                if s == -1:
                    print("Error: malformed parameter section \"" + s + "\"")
                pname = s[colon_idx+1:].strip()
               
                if "desc" in vte[s].keys():
                    desc = vte[s]["desc"]
                else:
                    desc = ""
                     
                if "default" in vte[s].keys():
                    default_val = vte[s]["default"]
                    has_default = True
                else:
                    default_val = ""
                    has_default = False
                
                param = Parameter(pname, desc, has_default, default_val)
                self.parameters[pname] = param
            elif s == "template":
              if "desc" in vte[s].keys():
                self.desc = vte[s]["desc"];
            else:
              print("Warning: unhandled section \"" + s + "\" in template " + self.tmpl_id)
            
    def list_templates(self):
        templates = []
        self.find_template_files(self.tmpl_dir, "", templates)
        
        return templates
    
    def find_template_files(self, parent_dir_abs, parent_name, templates):
        for f in os.listdir(parent_dir_abs):
            if parent_name == "":
                this_name = f;
            else:
                this_name = os.path.join(parent_name, f)
                
            if os.path.isdir(os.path.join(parent_dir_abs, f)):
                # Must recurse
                self.find_template_files(
                    os.path.join(parent_dir_abs, f),
                    this_name,
                    templates)
            elif f != ".vte" and f.endswith(".swp") == False:
                templates.append(this_name)
                
    
    def get_source(self, environment, template):
        path = os.path.join(self.tmpl_dir, template)
        if not os.path.exists(path):
            raise jinja2.TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        f = open(path, "r")
        try:
          source = f.read()
        except:
          print("Error reading file \"" + path + "\"");
        f.close()
        return source, path, lambda: mtime == os.path.getmtime(path)

        
class TemplateRgy:
    def find_templates(self, dir, template_id):
        
        if os.path.isfile(os.path.join(dir, ".vte")):
            if len(template_id) == 0:
                print("Error: found a template marker (.vte) in a root template-path directory (" + dir + ")");
                exit(1)
            t = TemplateInfo(
                ".".join(template_id),
                os.path.join(dir, ".vte"));
            self.templates.append(t)
            self.template_map[t.tmpl_id] = t
        else:
            for d in os.listdir(dir):
                if os.path.isdir(os.path.join(dir, d)):
                    template_id.append(d)
                    self.find_templates(
                        os.path.join(dir, d),
                        template_id)
                    template_id.pop()

    def __init__(self, template_path):
        self.templates = []
        self.template_map = {}
        
        for d in template_path:
            self.find_templates(d, [])
    
